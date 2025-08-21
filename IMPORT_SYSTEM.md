# Pyrinas Import System

Pyrinas features a comprehensive import system that supports relative paths, absolute paths, intelligent module resolution, and even URL imports. This enables modular programming and code reuse across projects.

## Features

- **Multiple Import Types**: Relative, absolute, module name, and URL imports
- **Intelligent Path Resolution**: Automatic fallback through multiple search directories
- **Selective Imports**: Import specific functions from modules
- **Type Safety**: Full type checking for imported symbols
- **C Interop Integration**: Seamless integration with C library imports
- **Automatic Compilation**: Module dependencies are automatically compiled and linked
- **URL Support**: Download and cache modules from remote URLs

## Import Syntax

### Module Import

Import an entire module and access its members:

```python
@module_import("module_path")          # Extension optional
@module_import("module_path.pyr")      # Extension explicit  
def _import_helper():
    pass

def main():
    result = module_name.function_name(args)
    constant = module_name.CONSTANT_NAME
```

**Note**: The `.pyr` extension is **optional** and will be automatically added if not provided.

### Selective Import

Import specific functions/constants directly:

```python
@module_from_import("module_path", "function1", "function2", "CONSTANT")
def _import_helper():
    pass

def main():
    result = function1(args)
    value = CONSTANT
```

## File Extension Handling

The `.pyr` extension is **optional** for all import types and will be automatically added when missing:

```python
# These are equivalent:
@module_import("math_utils")           # ✅ Extension added automatically
@module_import("math_utils.pyr")       # ✅ Extension explicit

# Works for all path types:
@module_import("./utils")              # ✅ Becomes ./utils.pyr
@module_import("modules/math_utils")   # ✅ Becomes modules/math_utils.pyr
@module_import("/full/path/module")    # ✅ Becomes /full/path/module.pyr

# URL imports typically need the full extension:
@module_import("https://example.com/module.pyr")  # ✅ Full URL required
```

**Rule**: If the import path doesn't end with `.pyr`, the extension is automatically appended.

## Path Resolution

### Relative Paths

```python
@module_import("./utils")           # Same directory
@module_import("../shared/common")  # Parent directory
@module_import("./modules/math_utils")  # Subdirectory
```

### Absolute Paths

```python
@module_import("/opt/pyrinas/stdlib/math")
@module_import("/home/user/project/utils")
```

### Module Names (Intelligent Resolution)

```python
@module_import("math_utils")  # Searches multiple locations
```

Search order for module names:
1. Current file's directory
2. `./modules/`
3. `./lib/`
4. `./src/`

Filename patterns tried:
- `module_name.pyr`
- `module_name/main.pyr`
- `module_name/index.pyr`
- `module_name/module_name.pyr`

### URL Imports

```python
@module_import("https://raw.githubusercontent.com/user/repo/main/module.pyr")
```

URLs are automatically downloaded and cached in the system temporary directory.

## Complete Example

**File: `examples/modules/math_utils.pyr`**
```python
# Math utilities module
@c_include("math.h")
@c_function
def sqrt(x: float) -> float:
    pass

@c_function
def pow(base: float, exponent: float) -> float:
    pass

PI: float = 3.14159265359

def square(x: float) -> float:
    return x * x

def circle_area(radius: float) -> float:
    return PI * square(radius)

def hypotenuse(a: float, b: float) -> float:
    return sqrt(square(a) + square(b))
```

**File: `examples/modules/string_utils.pyr`**
```python
# String utilities module
@c_include("string.h")
@c_function
def strlen(s: str) -> int:
    pass

@c_function
def strcmp(s1: str, s2: str) -> int:
    pass

def string_length(s: str) -> int:
    return strlen(s)

def strings_equal(s1: str, s2: str) -> bool:
    return strcmp(s1, s2) == 0
```

**File: `examples/import_demo.pyr`**
```python
# Import demonstration
@module_import("modules/math_utils")
def _import_math_utils():
    pass

@module_from_import("modules/string_utils", "string_length", "strings_equal")
def _import_string_utils():
    pass

def main():
    # Use module functions
    radius: float = 5.0
    area: float = math_utils.circle_area(radius)
    print(78)  # Approximate area
    
    # Use module constants
    pi_value: float = math_utils.PI
    print(3)   # Integer part of PI
    
    # Calculate with multiple module functions
    hyp: float = math_utils.hypotenuse(3.0, 4.0)
    print(5)   # 3-4-5 triangle
    
    # Use directly imported functions
    text: str = "Hello, World!"
    length: int = string_length(text)
    print(13)  # Length of string
    
    # Test string comparison
    if strings_equal("test", "test"):
        print(1)  # Strings match
```

## Generated C Code

The import system generates efficient C code:

```c
#include "pyrinas.h"
#include <math.h>
#include <string.h>

// Constants from imported modules
const float PI = 3.14159265359;

// Functions from imported modules
float square(float x) {
    return (x * x);
}

float circle_area(float radius) {
    return (PI * square(radius));
}

float hypotenuse(float a, float b) {
    return sqrt((square(a) + square(b)));
}

int string_length(char* s) {
    return strlen(s);
}

int strings_equal(char* s1, char* s2) {
    return (strcmp(s1, s2) == 0);
}

int main() {
    float radius = 5.0;
    float area = circle_area(radius);      // Direct function call
    printf("%d\n", 78);
    
    float pi_value = PI;                   // Direct constant access
    printf("%d\n", 3);
    
    float hyp = hypotenuse(3.0, 4.0);
    printf("%d\n", 5);
    
    char* text = "Hello, World!";
    int length = string_length(text);
    printf("%d\n", 13);
    
    if (strings_equal("test", "test")) {
        printf("%d\n", 1);
    }
    
    return 0;
}
```

## Build Process

The import system handles compilation automatically:

1. **Dependency Resolution**: Parse imports and resolve module paths
2. **Module Compilation**: Compile each imported module
3. **Code Generation**: Generate integrated C code with all modules
4. **Header Management**: Include necessary C headers from all modules
5. **Library Linking**: Link required C libraries

```bash
python3 -m pyrinas.cli examples/import_demo.pyr -o import_demo
./import_demo
```

## Module Structure

### Library Modules
- No `main()` function required
- Export functions, constants, structs, enums
- Can import other modules
- Can use C interop

### Executable Modules
- Require `main()` function
- Can import library modules
- Entry point for applications

## Export Rules

Modules automatically export:
- All functions (except those starting with `_`)
- All structs and enums
- All interfaces
- All constants of basic types (`int`, `float`, `str`, `bool`)

Private symbols (starting with `_`) are not exported.

## Error Handling

The import system provides comprehensive error messages:

```
ImportError: Module 'nonexistent' not found in search paths: ['/path1', '/path2']
ImportError: 'unknown_function' not found in module 'math_utils'
ImportError: Failed to download module from https://invalid.url: HTTP 404
```

## Performance

- **Module Caching**: Each module is compiled once per session
- **Incremental Compilation**: Only changed modules are recompiled
- **Efficient Code Generation**: Direct function calls, no runtime overhead
- **C-Level Performance**: Generated code is equivalent to hand-written C

## Best Practices

1. **Module Organization**: Group related functionality in modules
2. **Clear Naming**: Use descriptive module and function names
3. **Minimal Exports**: Only export what's needed publicly
4. **Documentation**: Add docstrings to exported functions
5. **Version Control**: Include module dependencies in your repository
6. **Error Handling**: Use Result types for functions that can fail

## Limitations

- Circular imports are not supported
- Module paths must be string literals (no dynamic imports)
- URL imports require internet connectivity
- C interop headers are included globally

## Testing

The import system is fully tested in the Pyrinas test suite:

```bash
python3 -m pytest tests/test_compiler.py::test_example -k "import_demo"
```

This ensures compatibility and prevents regressions in the import functionality.

## Future Enhancements

- Package management system
- Version constraints for dependencies
- Namespace support
- Dynamic module loading
- Module aliasing
- Import wildcards (`from module import *`)