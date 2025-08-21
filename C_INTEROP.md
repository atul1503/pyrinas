# C Interoperability in Pyrinas

Pyrinas provides seamless integration with C libraries through decorator-based syntax, enabling you to call C functions directly from Pyrinas code with full type safety.

## Features

- **Zero Overhead**: Direct C function calls without wrappers
- **Type Safe**: Full Pyrinas type checking maintained
- **Easy Integration**: Simple decorator-based syntax
- **Library Support**: Works with any C library
- **Automatic Linking**: Math library linked by default

## Syntax

### Including C Headers

Use the `@c_include` decorator to include C headers:

```python
@c_include("stdio.h")
@c_include("math.h")
@c_include("string.h")
```

### Declaring C Functions

Use the `@c_function` decorator to declare external C functions:

```python
@c_function
def sin(x: float) -> float:
    """C math library sine function"""
    pass

@c_function  
def strlen(s: str) -> int:
    """C string length function"""
    pass
```

## Type Mapping

Pyrinas types automatically map to corresponding C types:

| Pyrinas Type | C Type |
|--------------|--------|
| `int` | `int` |
| `float` | `float` |
| `str` | `char*` |
| `ptr[str]` | `char**` |
| `ptr[int]` | `int*` |

## Example

```python
# C Interop Example
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

def calculate_hypotenuse(a: float, b: float) -> float:
    """Calculate hypotenuse using C math functions"""
    a_squared: float = pow(a, 2.0)
    b_squared: float = pow(b, 2.0)
    return sqrt(a_squared + b_squared)

def main():
    angle: float = 1.57079633  # π/2 radians
    sine_val: float = sin(angle)
    cosine_val: float = cos(angle)
    
    print(sine_val)   # ≈ 1.0
    print(cosine_val) # ≈ 0.0
    
    # Use composite function
    hypotenuse: float = calculate_hypotenuse(3.0, 4.0)
    print(hypotenuse) # 5.0
```

## Compilation

C interop works automatically with the standard compilation process:

```bash
python3 -m pyrinas.cli my_program.pyr -o my_program
```

The compiler automatically:
- Includes the specified C headers
- Links the math library (`-lm`)
- Generates direct C function calls
- Links additional libraries as needed

## Supported Libraries

Pyrinas C interop works with any standard C library:

- **Math**: `sin`, `cos`, `sqrt`, `pow`, `fabs`, etc.
- **String**: `strlen`, `strcmp`, `strcpy`, etc.
- **I/O**: `printf`, `scanf`, `fopen`, etc.
- **Memory**: `malloc`, `free`, `memcpy`, etc.
- **Custom**: Any C library with proper headers

## Generated C Code

Pyrinas generates clean, efficient C code:

```c
#include "pyrinas.h"
#include <math.h>
#include <stdio.h>

int main() {
    float angle = 1.57079633;
    float sine_val = sin(angle);    // Direct C call
    float cosine_val = cos(angle);  // Direct C call
    
    printf("%f\n", sine_val);
    printf("%f\n", cosine_val);
}
```

## Best Practices

1. **Group Related Headers**: Use multiple `@c_include` decorators for organization
2. **Type Annotations**: Always provide complete type annotations for C functions
3. **Documentation**: Add docstrings to C function declarations for clarity
4. **Error Handling**: Use Pyrinas Result types for functions that can fail
5. **Memory Management**: Be careful with C functions that allocate memory

## Limitations

- C functions must be declared with `pass` body (external functions only)
- Complex C types (unions, complex structs) require manual mapping
- C macros are not directly supported (use wrapper functions)
- Variadic functions require fixed-argument wrappers

## Testing

The C interop feature is fully tested in the Pyrinas test suite. See `examples/c_math_demo.pyr` for a comprehensive example.