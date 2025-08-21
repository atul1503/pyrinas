import ast
import re
from typing import Optional

class Symbol:
    def __init__(self, name, type, param_types=None, return_type=None, fields=None, immutable=False, methods=None, implements=None, enum_members=None, is_c_function=False, c_library=None):
        self.name = name
        self.type = type
        self.param_types = param_types
        self.return_type = return_type
        self.fields = fields # For structs
        self.immutable = immutable # Whether this variable is immutable
        self.methods = methods or {} # For interfaces: method_name -> (param_types, return_type)
        self.implements = implements or [] # For structs: list of interface names they implement
        self.enum_members = enum_members or {} # For enums: member_name -> value
        # C interop attributes
        self.is_c_function = is_c_function # Whether this is a C function
        self.c_library = c_library # C library name (if any)

class SymbolTable:
    def __init__(self):
        self._scopes = [{}] # List of dictionaries, each dict is a scope

    def push_scope(self):
        self._scopes.append({})

    def pop_scope(self):
        if len(self._scopes) > 1:
            self._scopes.pop()
        else:
            raise Exception("Cannot pop global scope.")

    def insert(self, symbol):
        self._scopes[-1][symbol.name] = symbol

    def lookup(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name):
        return self._scopes[-1].get(name)

class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self, current_file: Optional[str] = None, module_resolver=None):
        self.symbol_table = SymbolTable()
        self.current_function_return_type = None
        self.loop_depth = 0
        self.loop_labels = []
        # C interop tracking
        self.c_includes = set()  # Set of C headers to include
        self.c_functions = {}    # Function name -> C library info
        self.c_libraries = set() # Set of C libraries to link
        # Import system
        self.current_file = current_file
        self.module_resolver = module_resolver
        self.imported_modules = {}  # import_path -> analyzer
    
    def _get_type_name(self, annotation):
        """Extract type name from annotation node (handles both ast.Name and ast.Constant)"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            return annotation.value
        elif isinstance(annotation, ast.Subscript):
            # Handle subscript annotations like ptr[str], array[int, 5], Result[int, str]
            base_name = getattr(annotation.value, 'id', None)
            if base_name == 'ptr':
                inner_type = getattr(annotation.slice, 'id', None)
                return f'ptr[{inner_type}]'
            elif base_name == 'array':
                if isinstance(annotation.slice, ast.Tuple) and len(annotation.slice.elts) == 2:
                    type_name = getattr(annotation.slice.elts[0], 'id', None)
                    size = annotation.slice.elts[1].value
                    return f'array[{type_name},{size}]'
            elif base_name == 'Result':
                if isinstance(annotation.slice, ast.Tuple) and len(annotation.slice.elts) == 2:
                    success_type = getattr(annotation.slice.elts[0], 'id', None)
                    error_type = getattr(annotation.slice.elts[1], 'id', None)
                    return f'Result[{success_type},{error_type}]'
            return None
        else:
            return None

    def _process_decorators(self, decorators):
        """Process function decorators for C interop"""
        is_c_function = False
        c_library = None
        
        for decorator in decorators:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'c_function':
                    is_c_function = True
                elif decorator.id == 'c_include':
                    # This should be handled at module level, not function level
                    pass
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'c_function' and decorator.args:
                        is_c_function = True
                        if isinstance(decorator.args[0], ast.Constant):
                            c_library = decorator.args[0].value
                    elif decorator.func.id == 'c_include' and decorator.args:
                        if isinstance(decorator.args[0], ast.Constant):
                            self.c_includes.add(decorator.args[0].value)
        
        return is_c_function, c_library

    def _is_external_function(self, node):
        """Check if a function is external (has only pass statements)"""
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True
        return False

    def _process_import(self, import_path: str, alias: Optional[str] = None, from_import: bool = False, import_names: Optional[list] = None):
        """Process an import statement."""
        if not self.module_resolver:
            raise ImportError("Module resolver not available for imports")
        
        try:
            # Load the module
            module_analyzer = self.module_resolver.load_module(import_path, self.current_file)
            self.imported_modules[import_path] = module_analyzer
            
            # Get exportable symbols from the module
            exports = self.module_resolver.get_module_exports(module_analyzer)
            
            if from_import and import_names:
                # from "module" import func1, func2
                for name in import_names:
                    if name in exports:
                        symbol = exports[name]
                        # Import the symbol directly into current scope
                        self.symbol_table.insert(symbol)
                    else:
                        raise ImportError(f"'{name}' not found in module '{import_path}'")
            else:
                # import "module" [as alias]
                module_name = alias if alias else import_path.split('/')[-1].replace('.pyr', '')
                
                # Create a module symbol containing all exports
                module_symbol = Symbol(module_name, 'module')
                module_symbol.exports = exports
                self.symbol_table.insert(module_symbol)
                
        except Exception as e:
            raise ImportError(f"Failed to import '{import_path}': {e}")

    def _handle_import_statement(self, node):
        """Handle import statements in the AST (using decorators)."""
        if isinstance(node, ast.FunctionDef):
            # Check for import decorators
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'module_import' and len(decorator.args) >= 1:
                        # @module_import("module_path")
                        if isinstance(decorator.args[0], ast.Constant):
                            import_path = decorator.args[0].value
                            alias = decorator.args[1].value if len(decorator.args) > 1 and isinstance(decorator.args[1], ast.Constant) else None
                            self._process_import(import_path, alias)
                            return True
                    elif decorator.func.id == 'module_from_import' and len(decorator.args) >= 2:
                        # @from_import("module_path", "func1", "func2", ...)
                        if isinstance(decorator.args[0], ast.Constant):
                            import_path = decorator.args[0].value
                            import_names = []
                            for i in range(1, len(decorator.args)):
                                if isinstance(decorator.args[i], ast.Constant):
                                    import_names.append(decorator.args[i].value)
                            self._process_import(import_path, from_import=True, import_names=import_names)
                            return True
        return False

    def visit_Module(self, node):
        # Phase 0: Process imports first
        for item in node.body:
            if self._handle_import_statement(item):
                continue  # Skip further processing for import statements
        
        # Ensure 'main' function is defined (unless this is a library module)
        main_found = False
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'main':
                main_found = True
                break
        
        # Only require main function for executable modules (not library modules)
        if not main_found:
            if self.current_file and ('/modules/' in self.current_file or self.current_file.endswith('_utils.pyr')):
                # Allow library modules to not have main
                pass
            else:
                raise NameError("main function not found.")
        
        # First pass: register all function signatures and struct definitions (without processing bodies)
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Register function signature without visiting its body
                func_name = item.name
                
                # Process decorators for C interop
                is_c_function, c_library = self._process_decorators(item.decorator_list)
                
                # Determine return type
                return_type = None
                if item.returns:
                    if isinstance(item.returns, ast.Name):
                        return_type = item.returns.id
                    elif isinstance(item.returns, ast.Constant) and isinstance(item.returns.value, str):
                        return_type = item.returns.value  # Handle string literal annotations like 'ptr[float]'
                    elif isinstance(item.returns, ast.Tuple) and len(item.returns.elts) == 2:
                        success_type = getattr(item.returns.elts[0], 'id', 'unknown')
                        error_type = getattr(item.returns.elts[1], 'id', 'unknown')
                        return_type = f'Result[{success_type},{error_type}]'
                    elif isinstance(item.returns, ast.Subscript) and getattr(item.returns.value, 'id', None) == 'Result':
                        # Handle Result[type1,type2] syntax
                        if isinstance(item.returns.slice, ast.Tuple) and len(item.returns.slice.elts) == 2:
                            success_type = getattr(item.returns.slice.elts[0], 'id', 'unknown')
                            error_type = getattr(item.returns.slice.elts[1], 'id', 'unknown')
                            return_type = f'Result[{success_type},{error_type}]'
                    elif isinstance(item.returns, ast.Constant) and item.returns.value is None:
                        # Handle None return type
                        return_type = None
                
                # Extract parameter types
                param_types = []
                for arg in item.args.args:
                    type_name = self._get_type_name(arg.annotation)
                    if type_name is None:
                        raise TypeError(f"Parameter '{arg.arg}' must have a type annotation.")
                    param_types.append(type_name)
                
                # Handle C function registration
                if is_c_function:
                    self.c_functions[func_name] = c_library
                    if c_library:
                        self.c_libraries.add(c_library)
                
                # Register the function
                if self.symbol_table.lookup_current_scope(func_name):
                    raise NameError(f"Function '{func_name}' already defined.")
                symbol = Symbol(func_name, 'function', param_types=param_types, return_type=return_type, is_c_function=is_c_function, c_library=c_library)
                self.symbol_table.insert(symbol)
            elif isinstance(item, ast.ClassDef):
                # Register struct definition
                self.visit_ClassDef(item)
        
        # Second pass: visit all nodes including function bodies
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.visit(item)
            elif not isinstance(item, ast.ClassDef):
                self.visit(item)

    def visit_ClassDef(self, node):
        class_name = node.name
        if self.symbol_table.lookup_current_scope(class_name):
            raise NameError(f"Type '{class_name}' already defined.")
        
        # Check if this class inherits from Enum
        is_enum = False
        implements = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                if base_name == 'Enum':
                    is_enum = True
                else:
                    base_symbol = self.symbol_table.lookup(base_name)
                    if base_symbol and base_symbol.type == 'interface':
                        implements.append(base_name)
                    else:
                        raise TypeError(f"Class '{class_name}' can only inherit from interfaces or Enum, not '{base_name}'.")
        
        if is_enum:
            # This is an enum - parse enum members
            enum_members = {}
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    # Enum member assignment (e.g., RED = 0)
                    if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                        member_name = stmt.targets[0].id
                        if isinstance(stmt.value, ast.Constant):
                            enum_members[member_name] = stmt.value.value
                        else:
                            raise TypeError(f"Enum member '{member_name}' must have a constant value.")
                    else:
                        raise TypeError("Enum member assignments must be simple assignments.")
                elif not isinstance(stmt, ast.Pass):
                    raise TypeError("Enum body can only contain member assignments or pass.")
            
            symbol = Symbol(class_name, 'enum', enum_members=enum_members)
        else:
            # Analyze class body to determine if it's an interface or struct
            fields = {}
            methods = {}
            has_fields = False
            has_method_implementations = False
            
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    # Field declaration
                    field_name = stmt.target.id
                    field_type = self._get_type_name(stmt.annotation)
                    if field_type is None:
                        field_type = "unknown"
                    fields[field_name] = field_type
                    has_fields = True
                    
                elif isinstance(stmt, ast.FunctionDef):
                    # Method declaration
                    method_name = stmt.name
                    
                    # Extract parameter types (skip 'self' parameter)
                    param_types = []
                    for arg in stmt.args.args[1:]:  # Skip self
                        type_name = self._get_type_name(arg.annotation)
                        if type_name is None:
                            raise TypeError(f"Method parameter '{arg.arg}' must have a type annotation.")
                        param_types.append(type_name)
                    
                    # Extract return type
                    return_type = None
                    if stmt.returns:
                        if isinstance(stmt.returns, ast.Name):
                            return_type = stmt.returns.id
                        elif isinstance(stmt.returns, ast.Constant) and isinstance(stmt.returns.value, str):
                            return_type = stmt.returns.value
                    
                    methods[method_name] = (param_types, return_type)
                    
                    # Check if method has implementation or just pass
                    if len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Pass):
                        # Just a pass statement - interface method
                        pass
                    else:
                        # Has implementation - struct method
                        has_method_implementations = True
                        
                elif not isinstance(stmt, ast.Pass):
                    raise TypeError("Class body can only contain field declarations, method signatures, or pass.")
            
            # Determine if this is an interface or struct
            if has_fields or has_method_implementations or implements:
                # This is a struct
                if implements:
                    # Validate that struct implements all interface methods
                    self._validate_interface_implementation(class_name, implements, methods)
                
                symbol = Symbol(class_name, 'struct', fields=fields, methods=methods, implements=implements)
            else:
                # This is an interface (only method signatures with pass)
                symbol = Symbol(class_name, 'interface', methods=methods)
        
        self.symbol_table.insert(symbol)

    def _validate_interface_implementation(self, struct_name, implements, struct_methods):
        """Validate that a struct implements all required interface methods"""
        for interface_name in implements:
            interface_symbol = self.symbol_table.lookup(interface_name)
            if not interface_symbol:
                raise NameError(f"Interface '{interface_name}' not found.")
            
            # Check each method in the interface
            for method_name, (interface_param_types, interface_return_type) in interface_symbol.methods.items():
                if method_name not in struct_methods:
                    raise TypeError(f"Struct '{struct_name}' must implement method '{method_name}' from interface '{interface_name}'.")
                
                struct_param_types, struct_return_type = struct_methods[method_name]
                
                # Check parameter types match
                if struct_param_types != interface_param_types:
                    raise TypeError(f"Method '{method_name}' in struct '{struct_name}' has parameter types {struct_param_types}, but interface '{interface_name}' requires {interface_param_types}.")
                
                # Check return types match
                if struct_return_type != interface_return_type:
                    raise TypeError(f"Method '{method_name}' in struct '{struct_name}' has return type '{struct_return_type}', but interface '{interface_name}' requires '{interface_return_type}'.")

    def visit_FunctionDef(self, node):
        # Set current function return type for return statement validation
        return_type = None
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return_type = node.returns.id
            elif isinstance(node.returns, ast.Constant) and isinstance(node.returns.value, str):
                return_type = node.returns.value  # Handle string literal annotations like 'ptr[float]'
            elif isinstance(node.returns, ast.Tuple) and len(node.returns.elts) == 2:
                success_type = getattr(node.returns.elts[0], 'id', 'unknown')
                error_type = getattr(node.returns.elts[1], 'id', 'unknown')
                return_type = f'Result[{success_type},{error_type}]'
            elif isinstance(node.returns, ast.Subscript) and getattr(node.returns.value, 'id', None) == 'Result':
                # Handle Result[type1,type2] syntax
                if isinstance(node.returns.slice, ast.Tuple) and len(node.returns.slice.elts) == 2:
                    success_type = getattr(node.returns.slice.elts[0], 'id', 'unknown')
                    error_type = getattr(node.returns.slice.elts[1], 'id', 'unknown')
                    return_type = f'Result[{success_type},{error_type}]'
                else:
                    raise TypeError("Result return type must have exactly two type parameters.")
            elif isinstance(node.returns, ast.Constant) and node.returns.value is None:
                # Handle None return type
                return_type = None
            else:
                raise TypeError("Unsupported return type annotation.")
        self.current_function_return_type = return_type

        # Push a new scope for function parameters and local variables
        self.symbol_table.push_scope()

        # Register parameters in the new scope
        for arg in node.args.args:
            var_name = arg.arg
            type_name = self._get_type_name(arg.annotation)
            if type_name is None:
                raise TypeError(f"Parameter '{var_name}' must have a type annotation.")
            self.symbol_table.insert(Symbol(var_name, type_name))

        # Check if this is an external C function
        is_c_function, _ = self._process_decorators(node.decorator_list)
        is_external = self._is_external_function(node)
        
        # For external C functions, skip body validation
        if is_c_function and is_external:
            # External C function - skip body processing
            pass
        else:
            # Visit the function body for regular functions
            for statement in node.body:
                self.visit(statement)

        # Pop the scope after visiting the body
        self.symbol_table.pop_scope()
        self.current_function_return_type = None # Reset

    def visit_AnnAssign(self, node):
        var_name = node.target.id
        
        type_name = None
        is_immutable = False
        
        if isinstance(node.annotation, ast.Name):
            type_name = node.annotation.id
        elif isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            type_str = node.annotation.value
            if type_str.startswith('ptr[') and type_str.endswith(']'):
                type_name = type_str  # Keep the full 'ptr[...]' string as the type
            elif type_str.startswith('array[') and type_str.endswith(']'):
                type_name = type_str  # Keep the full 'array[...]' string as the type
            else:
                raise TypeError(f"Invalid string annotation: {type_str}. Only 'ptr[...]' and 'array[...]' are supported.")
        elif isinstance(node.annotation, ast.Subscript):
            annotation_name = getattr(node.annotation.value, 'id', None)
            
            if annotation_name == 'Final':
                # Handle Final[type] for immutable variables
                is_immutable = True
                inner_annotation = node.annotation.slice
                
                if isinstance(inner_annotation, ast.Name):
                    type_name = inner_annotation.id
                elif isinstance(inner_annotation, ast.Constant) and isinstance(inner_annotation.value, str):
                    type_str = inner_annotation.value
                    if type_str.startswith('ptr[') and type_str.endswith(']'):
                        type_name = type_str
                    elif type_str.startswith('array[') and type_str.endswith(']'):
                        type_name = type_str
                    else:
                        raise TypeError(f"Invalid Final annotation: {type_str}")
                else:
                    raise TypeError("Final annotation must contain a simple type.")
                
            elif annotation_name == 'array':
                # Handle array[type, size] annotations
                # The slice for an array annotation should be a tuple of (type, size)
                if not isinstance(node.annotation.slice, ast.Tuple) or len(node.annotation.slice.elts) != 2:
                    raise TypeError("Array annotation requires a tuple of [type, size].")
                
                base_type_node = node.annotation.slice.elts[0]
                size_node = node.annotation.slice.elts[1]
                
                base_type = getattr(base_type_node, 'id', None)
                if not isinstance(size_node, ast.Constant) or not isinstance(size_node.value, int):
                    raise TypeError("Array size must be an integer literal.")
                size = size_node.value

                type_name = f'array[{base_type},{size}]'
            elif annotation_name == 'Result':
                # Handle Result[success_type, error_type] annotations
                if not isinstance(node.annotation.slice, ast.Tuple) or len(node.annotation.slice.elts) != 2:
                    raise TypeError("Result annotation requires a tuple of [success_type, error_type].")
                
                success_type_node = node.annotation.slice.elts[0]
                error_type_node = node.annotation.slice.elts[1]
                
                success_type = getattr(success_type_node, 'id', None)
                error_type = getattr(error_type_node, 'id', None)
                
                if not success_type or not error_type:
                    raise TypeError("Result types must be simple type names.")

                type_name = f'Result[{success_type},{error_type}]'
            else:
                raise TypeError(f"Unsupported subscript type annotation: {annotation_name}")
        else:
            raise TypeError("Type annotation must be a name, a pointer string, an array annotation, Result[type1,type2], or Final[type].")
        
        if self.symbol_table.lookup_current_scope(var_name):
            raise NameError(f"Variable '{var_name}' already declared in this scope.")
        
        # Immutable variables must be initialized at declaration
        if is_immutable and not node.value:
            raise TypeError(f"Immutable variable '{var_name}' must be initialized at declaration.")
            
        self.symbol_table.insert(Symbol(var_name, type_name, immutable=is_immutable))
        
        if node.value:
            value_type = self.visit(node.value)
            # Allow assigning ptr[void] (from malloc) to any other pointer type
            if value_type == 'ptr[void]' and type_name.startswith('ptr['):
                pass # This is a valid assignment
            elif value_type != type_name and not (type_name == 'bool' and value_type == 'int'):
                raise TypeError(f"Type mismatch assigning to '{var_name}': expected {type_name}, got {value_type}")
    
    def visit_Assign(self, node):
        """Handle assignments and check for immutability violations"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                symbol = self.symbol_table.lookup(var_name)
                
                if not symbol:
                    # Variable not declared - infer type from the assigned value
                    value_type = self.visit(node.value)
                    # Register the variable with the inferred type
                    self.symbol_table.insert(Symbol(var_name, value_type))
                else:
                    if symbol.immutable:
                        raise TypeError(f"Cannot reassign immutable variable '{var_name}'.")
                        
                    # Type check the assignment
                    value_type = self.visit(node.value)
                    if value_type != symbol.type and not (symbol.type == 'bool' and value_type == 'int'):
                        raise TypeError(f"Type mismatch assigning to '{var_name}': expected {symbol.type}, got {value_type}")
                    
            elif isinstance(target, ast.Subscript):
                # Handle array/subscript assignments - check if the array itself is immutable
                var_name = getattr(target.value, 'id', None)
                if var_name:
                    symbol = self.symbol_table.lookup(var_name)
                    if symbol and symbol.immutable:
                        raise TypeError(f"Cannot modify immutable array '{var_name}'.")
                # Continue with normal subscript processing
                self.visit(target)
                self.visit(node.value)
            elif isinstance(target, ast.Attribute):
                # Handle struct field assignments - check if the struct itself is immutable
                var_name = getattr(target.value, 'id', None)
                if var_name:
                    symbol = self.symbol_table.lookup(var_name)
                    if symbol and symbol.immutable:
                        raise TypeError(f"Cannot modify immutable struct '{var_name}'.")
                # Continue with normal attribute processing
                self.visit(target)
                self.visit(node.value)
            else:
                # For other assignment types, just visit normally
                self.visit(target)
            self.visit(node.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            symbol = self.symbol_table.lookup(node.id)
            if not symbol:
                raise NameError(f"Variable '{node.id}' not declared.")
            return symbol.type # Return the type of the variable
        self.generic_visit(node)

    def visit_BinOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Simple type promotion for now
        if left_type == 'float' or right_type == 'float':
            return 'float'
        elif left_type == 'int' and right_type == 'int':
            return 'int'
        else:
            raise TypeError(f"Unsupported binary operation between {left_type} and {right_type}")

    def visit_Compare(self, node):
        left_type = self.visit(node.left)
        # Assuming only one comparator for now
        right_type = self.visit(node.comparators[0])

        # Check enum type compatibility for comparisons
        left_symbol = self.symbol_table.lookup(left_type)
        right_symbol = self.symbol_table.lookup(right_type)
        
        # If both sides are enum types, they must be the same enum type
        if (left_symbol and left_symbol.type == 'enum' and 
            right_symbol and right_symbol.type == 'enum'):
            if left_type != right_type:
                raise TypeError(f"Cannot compare different enum types: '{left_type}' and '{right_type}'.")

        # Comparison operations always result in a boolean
        return 'bool'

    def visit_Attribute(self, node):
        # This handles expressions like `p1.x`, `rect.top_left.x`, or `Color.RED`
        
        # First, get the type of the object being accessed
        if isinstance(node.value, ast.Name):
            # Simple access like `p.x` or `Color.RED`
            name = node.value.id
            symbol = self.symbol_table.lookup(name)
            if not symbol:
                raise NameError(f"Name '{name}' not declared.")
            
            # Check if this is module access (module.function or module.constant)
            if symbol.type == 'module':
                member_name = node.attr
                if hasattr(symbol, 'exports') and member_name in symbol.exports:
                    exported_symbol = symbol.exports[member_name]
                    if exported_symbol.type == 'function':
                        # For function references, return the function type
                        return f'function:{exported_symbol.return_type}'
                    else:
                        # For constants/variables, return their type
                        return exported_symbol.type
                else:
                    raise AttributeError(f"Module '{name}' has no member '{member_name}'.")
            
            # Check if this is enum member access (EnumName.MEMBER)
            if symbol.type == 'enum':
                member_name = node.attr
                if member_name not in symbol.enum_members:
                    raise NameError(f"Enum '{name}' has no member '{member_name}'.")
                # Return the enum type name for enum member access
                return name
            
            # Handle struct field access
            if symbol.type == 'struct':
                struct_symbol = symbol
                object_type = symbol.type
            else:
                # It's a variable of a struct type
                struct_symbol = self.symbol_table.lookup(symbol.type)
                if not struct_symbol or struct_symbol.type != 'struct':
                    raise TypeError(f"Variable '{name}' is not a struct and has no attributes.")
                object_type = symbol.type
            
        else:
            # Complex expression like `rect.top_left.x` - recursively get the type
            object_type = self.visit(node.value)
            struct_symbol = self.symbol_table.lookup(object_type)
            if not struct_symbol or struct_symbol.type != 'struct':
                raise TypeError(f"Expression of type '{object_type}' is not a struct and has no attributes.")

        field_name = node.attr
        if field_name not in struct_symbol.fields:
            raise NameError(f"Struct '{struct_symbol.name}' has no field '{field_name}'.")
        
        # Return the type of the accessed field
        return struct_symbol.fields[field_name]

    def visit_Subscript(self, node):
        var_name = getattr(node.value, 'id', None)
        symbol = self.symbol_table.lookup(var_name)
        
        # Debug: print what we found to understand the issue
        if not symbol:
            raise TypeError(f"Variable '{var_name}' not found.")
        
        symbol_type = symbol.type
        if not symbol_type.startswith('array['):
            raise TypeError(f"Variable '{var_name}' is not an array and cannot be subscripted. Type: {symbol_type}")
        
        # Check that the index is an integer
        index_type = self.visit(node.slice)
        if index_type != 'int':
            raise TypeError(f"Array index must be an integer, but got {index_type}.")
            
        # Return the base type of the array
        match = re.match(r'array\[(\w+),\s*(\d+)\]', symbol_type)
        if match:
            return match.group(1)
        else:
            raise TypeError(f"Could not parse array type: {symbol_type}")

    def visit_Match(self, node):
        subject_type = self.visit(node.subject)
        if not subject_type.startswith('Result['):
            raise TypeError(f"Subject of a match statement must be a Result type, but got {subject_type}")

        # Basic validation for now: ensure Ok and Err cases are handled.
        # A more robust implementation would check for exhaustiveness.
        has_ok = False
        has_err = False
        for case in node.cases:
            if isinstance(case.pattern, ast.MatchAs) and isinstance(case.pattern.pattern, ast.MatchClass):
                 class_name = getattr(case.pattern.pattern.cls, 'id', None)
                 if class_name == 'Ok':
                     has_ok = True
                 elif class_name == 'Err':
                     has_err = True

                 # Analyze the body of the case in a new scope with the captured variable
                 self.symbol_table.push_scope()
                 
                 # Determine the type of the captured variable
                 import re
                 match = re.match(r'Result\[(\w+),(\w+)\]', subject_type)
                 success_type, error_type = match.groups()
                 captured_var_type = success_type if class_name == 'Ok' else error_type
                 
                 captured_var_name = case.pattern.name
                 self.symbol_table.insert(Symbol(captured_var_name, captured_var_type))
                 
                 for stmt in case.body:
                     self.visit(stmt)
                 self.symbol_table.pop_scope()

        if not (has_ok and has_err):
            raise SyntaxError("Match statement must handle both 'Ok' and 'Err' cases.")


    def visit_BoolOp(self, node):
        # All operands must be boolean
        for value in node.values:
            if self.visit(value) != 'bool':
                raise TypeError("Operands of boolean operations must be boolean.")
        return 'bool'

    def visit_If(self, node):
        test_type = self.visit(node.test)
        if test_type != 'bool':
            raise TypeError("If condition must be a boolean expression.")
        
        for statement in node.body:
            self.visit(statement)
        
        for statement in node.orelse:
            self.visit(statement)

    def visit_While(self, node):
        test_type = self.visit(node.test)
        if test_type != 'bool':
            raise TypeError("While condition must be a boolean expression.")
        
        self.loop_depth += 1
        # Check for a label preceding the loop
        label = self._get_preceding_label(node)
        if label:
            self.loop_labels.append(label)
        
        for statement in node.body:
            self.visit(statement)
        
        if label:
            self.loop_labels.pop()
        self.loop_depth -= 1

    def visit_For(self, node):
        # Assume loop variable is int for now
        loop_var_name = node.target.id
        if self.symbol_table.lookup_current_scope(loop_var_name):
            raise NameError(f"Variable '{loop_var_name}' already declared in this scope.")
        self.symbol_table.insert(Symbol(loop_var_name, 'int'))

        # Visit the iterable (e.g., range() call)
        self.visit(node.iter)

        # Visit the body of the loop
        self.loop_depth += 1
        # Check for a label preceding the loop
        label = self._get_preceding_label(node)
        if label:
            self.loop_labels.append(label)

        for statement in node.body:
            self.visit(statement)

        if label:
            self.loop_labels.pop()
        self.loop_depth -= 1

    def visit_UnaryOp(self, node):
        operand_type = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            if operand_type != 'bool': # Assuming 'bool' type for logical operations
                raise TypeError(f"Unsupported unary operation 'not' on type {operand_type}")
            return 'bool'
        elif isinstance(node.op, ast.USub):
            # Unary minus: -x
            if operand_type in ('int', 'float'):
                return operand_type  # -int -> int, -float -> float
            else:
                raise TypeError(f"Unsupported unary operation '-' on type {operand_type}")
        elif isinstance(node.op, ast.UAdd):
            # Unary plus: +x
            if operand_type in ('int', 'float'):
                return operand_type  # +int -> int, +float -> float
            else:
                raise TypeError(f"Unsupported unary operation '+' on type {operand_type}")
        else:
            raise NotImplementedError(f"Unary operator {type(node.op).__name__} not implemented.")

    def visit_Break(self, node):
        if self.loop_depth == 0:
            raise SyntaxError("'break' outside loop")
        label = self._get_preceding_label(node)
        if label and label not in self.loop_labels:
            raise NameError(f"Label '{label}' not found.")

    def visit_Continue(self, node):
        if self.loop_depth == 0:
            raise SyntaxError("'continue' outside loop")
        label = self._get_preceding_label(node)
        if label and label not in self.loop_labels:
            raise NameError(f"Label '{label}' not found.")

    def visit_Return(self, node):
        if not self.current_function_return_type:
            raise Exception("Return statement outside of function.")

        returned_type = self.visit(node.value)

        # Handle Result types
        if self.current_function_return_type.startswith('Result['):
            import re
            match = re.match(r'Result\[(\w+),(\w+)\]', self.current_function_return_type)
            success_type, error_type = match.groups()

            if returned_type.startswith('Ok[') and returned_type.endswith(']'):
                inner_type = returned_type[3:-1]
                if inner_type != success_type:
                    raise TypeError(f"Type mismatch in Ok return: expected {success_type}, got {inner_type}")
            elif returned_type.startswith('Err[') and returned_type.endswith(']'):
                inner_type = returned_type[4:-1]
                if inner_type != error_type:
                    raise TypeError(f"Type mismatch in Err return: expected {error_type}, got {inner_type}")
            else:
                raise TypeError(f"Must return an Ok or Err value from a function with a Result return type.")

        elif returned_type != self.current_function_return_type:
            raise TypeError(f"Return type mismatch: expected {self.current_function_return_type}, got {returned_type}.")

    def visit_Constant(self, node):
        # Check bool before int since bool is a subclass of int in Python
        if isinstance(node.value, bool):
            return 'bool'
        elif isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, float):
            return 'float'
        elif isinstance(node.value, str):
            return 'str'
        else:
            raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name == 'print':
                # For print, we just visit the arguments to ensure they are semantically valid
                for arg in node.args:
                    self.visit(arg)
                return # print doesn't return a value we care about for type checking
            elif func_name in ('int', 'float', 'str', 'bool'):
                # Built-in type conversion functions
                if len(node.args) != 1:
                    raise TypeError(f"{func_name}() expects exactly one argument.")
                arg_type = self.visit(node.args[0])
                # Type conversions are generally allowed between basic types
                return func_name
            elif func_name == 'range':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, int):
                    raise TypeError("range() expects exactly one integer argument.")
                return 'range_object' # A special type to indicate it's a range object
            elif func_name == 'addr':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    raise TypeError("addr() expects a single variable name as an argument.")
                var_name = node.args[0].id
                symbol = self.symbol_table.lookup(var_name)
                if not symbol:
                    raise NameError(f"Variable '{var_name}' not declared.")
                return f'ptr[{symbol.type}]'
            elif func_name == 'deref':
                if len(node.args) != 1:
                    raise TypeError("deref() expects a single argument.")
                ptr_type = self.visit(node.args[0])
                if not ptr_type.startswith('ptr[') or not ptr_type.endswith(']'):
                    raise TypeError(f"Cannot dereference non-pointer type: {ptr_type}")
                return ptr_type[4:-1] # Extract the inner type, e.g., 'int' from 'ptr[int]'
            elif func_name == 'assign':
                if len(node.args) != 2:
                    raise TypeError("assign() expects two arguments: a pointer and a value.")
                ptr_type = self.visit(node.args[0])
                if not ptr_type.startswith('ptr[') or not ptr_type.endswith(']'):
                    raise TypeError(f"First argument to assign() must be a pointer, got {ptr_type}")
                
                value_type = self.visit(node.args[1])
                expected_type = ptr_type[4:-1]
                if value_type != expected_type:
                    raise TypeError(f"Type mismatch in assign(): pointer is {ptr_type}, but value is {value_type}")
                return None # assign does not return a value
            elif func_name == 'sizeof':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                    raise TypeError("sizeof() expects a single string literal argument representing a type.")
                return 'int' # sizeof always returns an integer
            elif func_name == 'malloc':
                if len(node.args) != 1:
                    raise TypeError("malloc() expects a single integer argument (size).")
                size_type = self.visit(node.args[0])
                if size_type != 'int':
                    raise TypeError(f"Argument to malloc() must be an integer, but got {size_type}.")
                return 'ptr[void]' # malloc returns a generic pointer
            elif func_name == 'free':
                if len(node.args) != 1:
                    raise TypeError("free() expects a single pointer argument.")
                arg_type = self.visit(node.args[0])
                if not arg_type.startswith('ptr['):
                    raise TypeError(f"Argument to free() must be a pointer, but got {arg_type}.")
                return None # free does not return a value
            elif func_name in ('Ok', 'Err'):
                if len(node.args) != 1:
                    raise TypeError(f"{func_name}() expects exactly one argument.")
                inner_type = self.visit(node.args[0])
                return f'{func_name}[{inner_type}]'
            elif func_name in ('is_ok', 'is_err'):
                if len(node.args) != 1:
                    raise TypeError(f"{func_name}() expects exactly one argument.")
                arg_type = self.visit(node.args[0])
                # The argument should be a Result type (we'll be flexible about the exact format)
                return 'bool'
            elif func_name.startswith('unwrap_or_'):
                if len(node.args) != 2:
                    raise TypeError(f"{func_name}() expects exactly two arguments.")
                result_type = self.visit(node.args[0])
                default_type = self.visit(node.args[1])
                # Extract the type from the function name
                return_type = func_name[10:]  # Remove 'unwrap_or_' prefix
                # Verify the default value matches the expected type
                if default_type != return_type:
                    raise TypeError(f"Default value type {default_type} doesn't match expected type {return_type}")
                return return_type
            elif func_name.startswith('unwrap_'):
                if len(node.args) != 1:
                    raise TypeError(f"{func_name}() expects exactly one argument.")
                arg_type = self.visit(node.args[0])
                # Extract the type from the function name (unwrap_int -> int, unwrap_str -> str, etc.)
                return_type = func_name[7:]  # Remove 'unwrap_' prefix
                return return_type
            elif func_name.startswith('expect_'):
                if len(node.args) != 2:
                    raise TypeError(f"{func_name}() expects exactly two arguments.")
                result_type = self.visit(node.args[0])
                message_type = self.visit(node.args[1])
                if message_type != 'str':
                    raise TypeError(f"Second argument to {func_name}() must be a string, got {message_type}")
                # Extract the type from the function name
                return_type = func_name[7:]  # Remove 'expect_' prefix
                return return_type
            else:
                # Check if this is a struct constructor call
                struct_symbol = self.symbol_table.lookup(func_name)
                if struct_symbol and struct_symbol.type == 'struct':
                    # This is a struct constructor - should have no arguments for default constructor
                    if len(node.args) != 0:
                        raise TypeError(f"Struct constructor '{func_name}' expects no arguments, but got {len(node.args)}.")
                    return func_name  # Return the struct type name
                
                # Handle user-defined function calls
                func_symbol = self.symbol_table.lookup(func_name) # Use lookup for functions as they can be defined before use
                if not func_symbol or func_symbol.type != 'function':
                    raise NameError(f"Function '{func_name}' not defined.")
                
                # Validate argument count and types
                if len(node.args) != len(func_symbol.param_types):
                    raise TypeError(f"Function '{func_name}' expects {len(func_symbol.param_types)} arguments, but got {len(node.args)}.")
                
                for i, arg_node in enumerate(node.args):
                    arg_type = self.visit(arg_node)
                    expected_type = func_symbol.param_types[i]
                    if arg_type != expected_type:
                        raise TypeError(f"Argument {i+1} of function '{func_name}' has type {arg_type}, but expected {expected_type}.")
                
                return func_symbol.return_type
        elif isinstance(node.func, ast.Attribute):
            # Method call (e.g., obj.method())
            return self._visit_method_call(node)
        else:
            raise NotImplementedError("Only direct function calls and method calls are supported.")

    def _visit_method_call(self, node):
        """Handle method calls like obj.method() and module function calls like module.function()"""
        # Get the object being called
        obj_node = node.func.value
        method_name = node.func.attr
        
        # Get the type of the object
        if isinstance(obj_node, ast.Name):
            obj_name = obj_node.id
            obj_symbol = self.symbol_table.lookup(obj_name)
            if not obj_symbol:
                raise NameError(f"Variable '{obj_name}' not defined.")
            
            # Check if this is a module access (module.function)
            if obj_symbol.type == 'module':
                # This is a module function call
                if hasattr(obj_symbol, 'exports') and method_name in obj_symbol.exports:
                    func_symbol = obj_symbol.exports[method_name]
                    
                    # Validate function call
                    if func_symbol.type != 'function':
                        raise TypeError(f"'{method_name}' in module '{obj_name}' is not a function.")
                    
                    # Validate argument count and types
                    if len(node.args) != len(func_symbol.param_types):
                        raise TypeError(f"Function '{obj_name}.{method_name}' expects {len(func_symbol.param_types)} arguments, but got {len(node.args)}.")
                    
                    for i, arg_node in enumerate(node.args):
                        arg_type = self.visit(arg_node)
                        expected_type = func_symbol.param_types[i]
                        if arg_type != expected_type:
                            raise TypeError(f"Argument {i+1} of function '{obj_name}.{method_name}' has type {arg_type}, but expected {expected_type}.")
                    
                    return func_symbol.return_type
                else:
                    raise AttributeError(f"Module '{obj_name}' has no function '{method_name}'.")
            
            obj_type = obj_symbol.type
        else:
            # For more complex expressions, get the type recursively
            obj_type = self.visit(obj_node)
        
        # Look up the struct/interface type definition
        type_symbol = self.symbol_table.lookup(obj_type)
        if not type_symbol:
            raise NameError(f"Type '{obj_type}' not defined.")
        
        # Check if the method exists in this type
        if not type_symbol.methods or method_name not in type_symbol.methods:
            raise AttributeError(f"Type '{obj_type}' has no method '{method_name}'.")
        
        # Get method signature
        param_types, return_type = type_symbol.methods[method_name]
        
        # Validate arguments (excluding 'self')
        if len(node.args) != len(param_types):
            raise TypeError(f"Method '{method_name}' expects {len(param_types)} arguments, but got {len(node.args)}.")
        
        for i, arg_node in enumerate(node.args):
            arg_type = self.visit(arg_node)
            expected_type = param_types[i]
            if arg_type != expected_type:
                raise TypeError(f"Argument {i+1} of method '{method_name}' has type {arg_type}, but expected {expected_type}.")
        
        return return_type

    def visit_Expr(self, node):
        # Visit the expression, but don't return its type
        self.visit(node.value)

    def _get_preceding_label(self, loop_node):
        # This is a bit of a hack. We need to find the label
        # that immediately precedes the loop in the AST.
        if hasattr(loop_node, 'parent'):
            body = loop_node.parent.body
            idx = body.index(loop_node)
            if idx > 0 and isinstance(body[idx - 1], ast.Expr) and isinstance(body[idx - 1].value, ast.Constant) and isinstance(body[idx - 1].value.value, str):
                return body[idx - 1].value.value
        return None

class ParentageVisitor(ast.NodeVisitor):
    def visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        self.generic_visit(node)

if __name__ == '__main__':
    with open('examples/hello.pyr', 'r') as f:
        code = f.read()
    
    tree = ast.parse(code)
    ParentageVisitor().visit(tree)
    analyzer = SemanticAnalyzer()
    analyzer.visit(tree)
    print("Semantic analysis successful!")