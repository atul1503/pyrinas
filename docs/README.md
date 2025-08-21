# Pyrinas Documentation

Welcome to the Pyrinas programming language documentation!

## What is Pyrinas?

Pyrinas is a strongly-typed subset of Python that compiles to efficient C code. It combines Python's familiar syntax with C's performance and provides seamless C library integration.

## Documentation Structure

### 📚 Core Language
- [Language Overview](language-overview.md) - Core Pyrinas features and syntax
- [Type System](type-system.md) - Understanding Pyrinas types
- [Memory Management](memory-management.md) - Pointers and manual memory control

### 🔌 C Interoperability
- **[C Interop Guide](c-interop-guide.md)** - Complete guide to using C libraries
- **[C Interop Tutorial](c-interop-tutorial.md)** - Step-by-step hands-on tutorial  
- **[C Interop API Reference](c-interop-api.md)** - Ready-to-use C function declarations

### 🚀 Getting Started
- [Installation](installation.md) - Setting up Pyrinas
- [Quick Start](quick-start.md) - Your first Pyrinas program
- [Examples](../examples/) - Sample programs and code

### 📖 Advanced Topics
- [Advanced C Interop](c-interop-advanced.md) - Custom libraries and complex usage
- [Error Handling](error-handling.md) - Result types and safe programming
- [Performance](performance.md) - Optimization tips and benchmarks

## C Interoperability Highlights

Pyrinas provides **zero-overhead** C interoperability. You can call C functions directly:

```python
@c_include("math.h")
@c_function
def sin(x: float) -> float:
    pass

def main():
    result: float = sin(3.14159)  # Direct C library call!
    print(result)
```

**Key Features:**
- 🔥 **Zero Overhead** - Direct C function calls, no wrappers
- 🛡️ **Type Safe** - Full compile-time type checking
- 🎯 **Easy Integration** - Simple decorator-based syntax
- 📚 **Any C Library** - Works with math, string, I/O, custom libraries
- ⚡ **Automatic Linking** - No manual build configuration needed

## Quick Reference

### Using C Functions (3 Steps)

1. **Include Header:**
   ```python
   @c_include("math.h")
   ```

2. **Declare Function:**
   ```python
   @c_function
   def sqrt(x: float) -> float:
       pass
   ```

3. **Use Normally:**
   ```python
   result: float = sqrt(25.0)  # Returns 5.0
   ```

### Common C Libraries

| Library | Header | Functions |
|---------|--------|-----------|
| **Math** | `math.h` | `sin`, `cos`, `sqrt`, `pow`, `log` |
| **String** | `string.h` | `strlen`, `strcmp`, `strcpy` |
| **I/O** | `stdio.h` | `printf`, `scanf`, `fopen` |
| **Memory** | `stdlib.h` | `malloc`, `free`, `atoi` |

## Examples

### Math Calculations
```python
@c_include("math.h")
@c_function
def pow(base: float, exp: float) -> float:
    pass

@c_function  
def sqrt(x: float) -> float:
    pass

def hypotenuse(a: float, b: float) -> float:
    return sqrt(pow(a, 2.0) + pow(b, 2.0))

def main():
    result: float = hypotenuse(3.0, 4.0)
    print(result)  # 5.0
```

### String Processing
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
    
    if strcmp(text, "Hello, World!") == 0:
        print("Strings match!")
```

## Getting Help

- **Examples**: Check the [examples/](../examples/) directory for working code
- **Tutorial**: Follow the [step-by-step tutorial](c-interop-tutorial.md)
- **API Reference**: Find function declarations in the [API reference](c-interop-api.md)
- **Issues**: Report bugs or ask questions on GitHub

## Contributing

- Documentation improvements welcome
- Example programs appreciated  
- Bug reports and feature requests encouraged

---

**Start with the [C Interop Tutorial](c-interop-tutorial.md) for hands-on learning!**