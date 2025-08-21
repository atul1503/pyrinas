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
python3 -m pyrinas.cli input.py -o output_executable
```

**Example:**
```bash
# Compile hello.py to an executable named 'hello'
python3 -m pyrinas.cli examples/hello.py -o hello

# Run the compiled program
./hello
```

### Complete Workflow

1. **Write Pyrinas Code** (`.py` files with type annotations)
2. **Compile to C** → Pyrinas compiler generates C code
3. **Compile C to Executable** → GCC compiles C code + runtime
4. **Run Executable** → Native binary execution

```
hello.py → [Pyrinas Compiler] → hello.c → [GCC + Runtime] → hello (executable) → ./hello
```

### Example Program

**hello.py:**
```python
def main() -> int:
    print("Hello, Pyrinas!")
    return 0
```

**Compilation:**
```bash
python3 -m pyrinas.cli hello.py -o hello
./hello
# Output: Hello, Pyrinas!
```

### More Examples

See the `examples/` directory for comprehensive examples:

- **`functions.py`** - Function definitions and calls
- **`pointers.py`** - Pointer operations and memory access
- **`structs.py`** - User-defined data structures
- **`arrays.py`** - Array declarations and manipulation
- **`errors.py`** - Result type error handling
- **`memory.py`** - Manual memory management

## Testing

Run the complete test suite:

```bash
python3 -m pytest tests/test_compiler.py -v
```

This compiles and runs all examples, verifying correct output.
