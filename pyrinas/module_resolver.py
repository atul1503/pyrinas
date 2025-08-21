"""
Module Resolution System for Pyrinas

Handles importing modules from various sources:
- Relative paths (./module.pyr, ../module.pyr)
- Absolute paths (/full/path/module.pyr)
- Module names with intelligent guessing (module -> ./module.pyr, ./modules/module.pyr, etc.)
- URL imports (https://example.com/module.pyr)
"""

import os
import urllib.request
import urllib.parse
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Set
from pyrinas.parser import get_ast
from pyrinas.semantic import SemanticAnalyzer, ParentageVisitor


class ModuleResolver:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.cache_dir = Path(tempfile.gettempdir()) / "pyrinas_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Track loaded modules to prevent circular imports
        self.loaded_modules: Set[str] = set()
        self.module_symbols: Dict[str, object] = {}  # Module path -> SemanticAnalyzer
        
        # Search paths for module resolution
        self.search_paths = [
            self.base_path,
            self.base_path / "modules",
            self.base_path / "lib",
            self.base_path / "src",
        ]

    def resolve_import(self, import_path: str, current_file: Optional[str] = None) -> str:
        """
        Resolve an import path to an absolute file path.
        
        Args:
            import_path: The import path (relative, absolute, URL, or module name)
            current_file: Path of the file doing the importing (for relative imports)
            
        Returns:
            Absolute path to the resolved module file
            
        Raises:
            FileNotFoundError: If module cannot be found
        """
        # Handle URL imports
        if import_path.startswith(("http://", "https://")):
            return self._resolve_url_import(import_path)
        
        # Handle absolute paths
        if import_path.startswith("/"):
            if import_path.endswith(".pyr"):
                abs_path = Path(import_path)
            else:
                abs_path = Path(import_path + ".pyr")
            
            if abs_path.exists():
                return str(abs_path.resolve())
            raise FileNotFoundError(f"Module not found: {import_path}")
        
        # Handle relative paths
        if import_path.startswith("./") or import_path.startswith("../"):
            if current_file:
                current_dir = Path(current_file).parent
            else:
                current_dir = self.base_path
            
            if import_path.endswith(".pyr"):
                rel_path = current_dir / import_path
            else:
                rel_path = current_dir / (import_path + ".pyr")
            
            if rel_path.exists():
                return str(rel_path.resolve())
            raise FileNotFoundError(f"Module not found: {import_path}")
        
        # Handle paths with slashes (treat as relative to base directory)
        if "/" in import_path:
            if current_file:
                current_dir = Path(current_file).parent
            else:
                current_dir = self.base_path
            
            if import_path.endswith(".pyr"):
                rel_path = current_dir / import_path
            else:
                rel_path = current_dir / (import_path + ".pyr")
            
            if rel_path.exists():
                return str(rel_path.resolve())
            raise FileNotFoundError(f"Module not found: {import_path}")
        
        # Handle module names with intelligent guessing
        return self._resolve_module_name(import_path, current_file)

    def _resolve_url_import(self, url: str) -> str:
        """Download and cache a module from a URL."""
        # Create a cache key from the URL
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_file = self.cache_dir / f"{url_hash}.pyr"
        
        # Check if already cached
        if cache_file.exists():
            return str(cache_file)
        
        # Download the module
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
            
            # Save to cache
            with open(cache_file, 'w') as f:
                f.write(content)
            
            return str(cache_file)
        except Exception as e:
            raise FileNotFoundError(f"Failed to download module from {url}: {e}")

    def _resolve_module_name(self, module_name: str, current_file: Optional[str] = None) -> str:
        """Resolve a module name using intelligent guessing."""
        # Possible file names
        possible_names = [
            f"{module_name}.pyr",
            f"{module_name}/main.pyr",
            f"{module_name}/index.pyr",
            f"{module_name}/{module_name}.pyr",
        ]
        
        # Search paths to try
        search_dirs = list(self.search_paths)
        
        # Add current file's directory if available
        if current_file:
            current_dir = Path(current_file).parent
            search_dirs.insert(0, current_dir)
        
        # Try each combination
        for search_dir in search_dirs:
            for name in possible_names:
                candidate = search_dir / name
                if candidate.exists():
                    return str(candidate.resolve())
        
        raise FileNotFoundError(f"Module '{module_name}' not found in search paths: {[str(p) for p in search_dirs]}")

    def load_module(self, import_path: str, current_file: Optional[str] = None) -> 'SemanticAnalyzer':
        """
        Load and analyze a module, returning its semantic analyzer.
        
        Args:
            import_path: The import path to resolve
            current_file: Path of the file doing the importing
            
        Returns:
            SemanticAnalyzer instance for the loaded module
        """
        # Resolve the import path
        resolved_path = self.resolve_import(import_path, current_file)
        
        # Check if already loaded (prevent circular imports)
        if resolved_path in self.loaded_modules:
            return self.module_symbols[resolved_path]
        
        # Mark as being loaded
        self.loaded_modules.add(resolved_path)
        
        try:
            # Read and parse the module
            with open(resolved_path, 'r') as f:
                code = f.read()
            
            tree = get_ast(code)
            
            # Analyze the module
            ParentageVisitor().visit(tree)
            analyzer = SemanticAnalyzer(current_file=resolved_path, module_resolver=self)
            analyzer.visit(tree)
            
            # Store the analyzer
            self.module_symbols[resolved_path] = analyzer
            
            return analyzer
            
        except Exception as e:
            # Remove from loaded modules if loading failed
            self.loaded_modules.discard(resolved_path)
            raise ImportError(f"Failed to load module '{import_path}': {e}")

    def get_module_exports(self, analyzer: 'SemanticAnalyzer') -> Dict[str, object]:
        """Extract exportable symbols from a module's semantic analyzer."""
        exports = {}
        
        # Get all symbols from the global scope
        if analyzer.symbol_table._scopes:
            global_scope = analyzer.symbol_table._scopes[0]
            for name, symbol in global_scope.items():
                # Export functions, classes, and constants (non-internal variables)
                if symbol.type in ('function', 'struct', 'enum', 'interface'):
                    exports[name] = symbol
                elif symbol.type in ('int', 'float', 'str', 'bool') and not name.startswith('_'):
                    # Export constants (basic types that aren't private)
                    exports[name] = symbol
        
        return exports

    def clear_cache(self):
        """Clear the module cache."""
        self.loaded_modules.clear()
        self.module_symbols.clear()