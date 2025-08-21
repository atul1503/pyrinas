# C Interoperability Guide

This guide explains how to seamlessly integrate C libraries into your Pyrinas programs.

## Overview

Pyrinas provides zero-overhead C interoperability through decorators. You can call C functions directly from Pyrinas code while maintaining full type safety.

## Quick Start

### 1. Include C Headers

Use the `@c_include` decorator to include C header files:

```python
@c_include("math.h")
@c_include("stdio.h")
@c_include("string.h")
```

### 2. Declare C Functions

Use the `@c_function` decorator with a `pass` body:

```python
@c_function
def sin(x: float) -> float:
    """C math library sine function"""
    pass
```

### 3. Use Functions Normally

Call C functions just like any Pyrinas function:

```python
def main():
    angle: float = 1.57079633  # π/2 radians
    result: float = sin(angle)
    print(result)  # Prints ~1.0
```

### 4. Compile

No special flags needed - just compile normally:

```bash
python3 -m pyrinas.cli my_program.pyr -o my_program
./my_program
```

## Detailed Process

### Step 1: Header Inclusion

The `@c_include` decorator tells Pyrinas to include C headers in the generated code:

```python
@c_include("math.h")     # For mathematical functions
@c_include("string.h")   # For string manipulation
@c_include("stdio.h")    # For I/O functions
```

**Important:** Place `@c_include` decorators on the first function that uses functions from that header.

### Step 2: Function Declaration

Declare C functions using the `@c_function` decorator:

```python
@c_function
def strlen(s: str) -> int:
    """Returns the length of a C string"""
    pass  # MUST use 'pass' - indicates external function
```

**Key Points:**
- **Must use `pass`**: This tells Pyrinas the function is external (defined in C)
- **Type annotations required**: Pyrinas needs to know parameter and return types
- **Docstrings optional**: But recommended for clarity

### Step 3: Type Mapping

Pyrinas automatically maps types between Pyrinas and C:

| Pyrinas Type | C Type | Usage |
|--------------|--------|-------|
| `int` | `int` | Integers |
| `float` | `float` | Floating point |
| `str` | `char*` | Strings |
| `ptr[int]` | `int*` | Pointer to int |
| `ptr[str]` | `char**` | Pointer to string |

### Step 4: Function Usage

Use C functions exactly like Pyrinas functions:

```python
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    dx: float = x2 - x1
    dy: float = y2 - y1
    return sqrt(dx * dx + dy * dy)  # sqrt is from C math library
```

## Complete Example

```python
# File: math_example.pyr

# Include C headers
@c_include("math.h")
@c_function
def sin(x: float) -> float:
    pass

@c_function
def cos(x: float) -> float:
    pass

@c_function
def sqrt(x: float) -> float:
    pass

@c_function
def pow(base: float, exp: float) -> float:
    pass

# Pyrinas function using C functions
def pythagorean_theorem(a: float, b: float) -> float:
    """Calculate hypotenuse using C math functions"""
    a_squared: float = pow(a, 2.0)
    b_squared: float = pow(b, 2.0)
    return sqrt(a_squared + b_squared)

def main():
    # Test trigonometric functions
    angle: float = 1.57079633  # π/2 radians
    print(sin(angle))  # ~1.0
    print(cos(angle))  # ~0.0
    
    # Test composite function
    hypotenuse: float = pythagorean_theorem(3.0, 4.0)
    print(hypotenuse)  # 5.0
```

Compile and run:
```bash
python3 -m pyrinas.cli math_example.pyr -o math_example
./math_example
```

## Generated C Code

Pyrinas generates clean, efficient C code:

```c
#include "pyrinas.h"
#include <math.h>

float pythagorean_theorem(float a, float b) {
    float a_squared = pow(a, 2.0);
    float b_squared = pow(b, 2.0);
    return sqrt(a_squared + b_squared);
}

int main() {
    float angle = 1.57079633;
    printf("%f\n", sin(angle));    // Direct C call
    printf("%f\n", cos(angle));    // Direct C call
    
    float hypotenuse = pythagorean_theorem(3.0, 4.0);
    printf("%f\n", hypotenuse);
}
```

## Common Patterns

### String Functions

```python
@c_include("string.h")
@c_function
def strlen(s: str) -> int:
    pass

@c_function
def strcmp(s1: str, s2: str) -> int:
    pass

def main():
    text: str = "Hello, World!"
    length: int = strlen(text)
    print(length)  # 13
```

### Math Functions

```python
@c_include("math.h")
@c_function
def fabs(x: float) -> float:
    pass

@c_function
def floor(x: float) -> float:
    pass

@c_function
def ceil(x: float) -> float:
    pass

def main():
    x: float = -7.8
    print(fabs(x))   # 7.8
    print(floor(x))  # -8.0
    print(ceil(x))   # -7.0
```

### I/O Functions

```python
@c_include("stdio.h")
@c_function
def printf(format: str, value: int) -> int:
    pass

def main():
    printf("The answer is %d\n", 42)
```

## Best Practices

1. **Group Related Headers**: Place `@c_include` decorators together
2. **Document Functions**: Add docstrings to C function declarations
3. **Type Everything**: Always provide complete type annotations
4. **Use Pass**: Always use `pass` for external function bodies
5. **Test Thoroughly**: C functions don't have Pyrinas safety checks

## Troubleshooting

### Common Errors

**Error: "Parameter must have a type annotation"**
```python
# ❌ Wrong - missing type annotation
@c_function
def sin(x) -> float:
    pass

# ✅ Correct - has type annotation
@c_function
def sin(x: float) -> float:
    pass
```

**Error: "Function body must be pass"**
```python
# ❌ Wrong - has implementation
@c_function
def sin(x: float) -> float:
    return 0.0

# ✅ Correct - uses pass
@c_function
def sin(x: float) -> float:
    pass
```

**Error: "Header not found"**
```python
# ❌ Wrong - invalid header
@c_include("nonexistent.h")

# ✅ Correct - standard header
@c_include("math.h")
```

## Limitations

- C functions must have `pass` body (external only)
- Complex C structures require manual mapping
- C macros are not supported directly
- Variadic functions need fixed-argument wrappers
- Memory management is manual (C rules apply)

## Next Steps

- See [API Reference](c-interop-api.md) for complete function list
- Check [Examples](../examples/) for more complex use cases
- Read [Advanced Usage](c-interop-advanced.md) for custom libraries