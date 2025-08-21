# Pyrinas

A compiler for a strongly-typed subset of Python that compiles to C.

## Features

### Core Language Features
- **Functions**: Function definitions with typed parameters and return values
- **Variables**: Strongly-typed variables (`int`, `float`, `bool`, `str`)
- **Control Flow**: `if/else`, `for` loops, `while` loops, `break`, `continue`
- **Labeled Control Flow**: Labeled `break` and `continue` for nested loops
- **Operators**: Arithmetic, comparison, logical, and modulo operators

### Advanced Features
- **Pointers**: Manual pointer management with `addr()`, `deref()`, `assign()`
- **Multi-level Pointers**: Support for pointers to pointers (`ptr[ptr[int]]`)
- **Manual Memory Management**: `malloc()`, `free()`, `sizeof()` functions
- **Arrays**: Fixed-size arrays with type safety
- **Structs**: User-defined composite data types using `class` syntax
- **Modern Error Handling**: `Result` types with `Ok()` and `Err()` constructors

### System Features
- **C Interoperability**: Compiles to readable C code
- **Type Safety**: Comprehensive semantic analysis and type checking
- **Memory Safety**: Explicit memory management with pointer validation

## Building

### Prerequisites
First, build the runtime library:

```bash
make
```

This compiles the Pyrinas runtime (`runtime/pyrinas.c`) into an object file that gets linked with your programs.

## Usage

### Compiling Pyrinas Programs

To compile a Pyrinas program to an executable:

```bash
python3 -m pyrinas.cli input.pyr -o output_executable
```

**Example:**
```bash
# Compile hello.pyr to an executable named 'hello'
python3 -m pyrinas.cli examples/hello.pyr -o hello

# Run the compiled program
./hello
```

### Complete Workflow

1. **Write Pyrinas Code** (`.pyr` files with type annotations)
2. **Compile to C** → Pyrinas compiler generates C code
3. **Compile C to Executable** → GCC compiles C code + runtime
4. **Run Executable** → Native binary execution

```
hello.pyr → [Pyrinas Compiler] → hello.c → [GCC + Runtime] → hello (executable) → ./hello
```

### Example Program

**hello.pyr:**
```python
def main() -> int:
    print("Hello, Pyrinas!")
    return 0
```

**Compilation:**
```bash
python3 -m pyrinas.cli hello.pyr -o hello
./hello
# Output: Hello, Pyrinas!
```

### Documentation

See the `docs/` directory for comprehensive guides:

- **[C Interop Guide](docs/c-interop-guide.md)** - Complete C library integration guide
- **[C Interop Tutorial](docs/c-interop-tutorial.md)** - Step-by-step hands-on tutorial
- **[C Interop API Reference](docs/c-interop-api.md)** - Ready-to-use C function declarations

### More Examples

See the `examples/` directory for comprehensive examples:

- **`functions.pyr`** - Function definitions and calls
- **`pointers.pyr`** - Pointer operations and memory access
- **`structs.pyr`** - User-defined data structures
- **`arrays.pyr`** - Array declarations and manipulation
- **`errors.pyr`** - Result type error handling
- **`memory.pyr`** - Manual memory management
- **`c_math_demo.pyr`** - C library integration demo

## Testing

Run the complete test suite:

```bash
python3 -m pytest tests/test_compiler.py -v
```

This compiles and runs all examples, verifying correct output.
