# C Interop API Reference

This document provides ready-to-use Pyrinas declarations for common C library functions.

## Math Library (`math.h`)

### Trigonometric Functions

```python
@c_include("math.h")
@c_function
def sin(x: float) -> float:
    """Sine function"""
    pass

@c_function
def cos(x: float) -> float:
    """Cosine function"""
    pass

@c_function
def tan(x: float) -> float:
    """Tangent function"""
    pass

@c_function
def asin(x: float) -> float:
    """Arc sine function"""
    pass

@c_function
def acos(x: float) -> float:
    """Arc cosine function"""
    pass

@c_function
def atan(x: float) -> float:
    """Arc tangent function"""
    pass

@c_function
def atan2(y: float, x: float) -> float:
    """Arc tangent of y/x"""
    pass
```

### Exponential and Logarithmic Functions

```python
@c_function
def exp(x: float) -> float:
    """e raised to the power of x"""
    pass

@c_function
def log(x: float) -> float:
    """Natural logarithm"""
    pass

@c_function
def log10(x: float) -> float:
    """Base-10 logarithm"""
    pass

@c_function
def pow(base: float, exponent: float) -> float:
    """base raised to the power of exponent"""
    pass

@c_function
def sqrt(x: float) -> float:
    """Square root"""
    pass

@c_function
def cbrt(x: float) -> float:
    """Cube root"""
    pass
```

### Rounding and Absolute Value

```python
@c_function
def fabs(x: float) -> float:
    """Absolute value"""
    pass

@c_function
def floor(x: float) -> float:
    """Largest integer ≤ x"""
    pass

@c_function
def ceil(x: float) -> float:
    """Smallest integer ≥ x"""
    pass

@c_function
def round(x: float) -> float:
    """Round to nearest integer"""
    pass

@c_function
def trunc(x: float) -> float:
    """Truncate to integer"""
    pass
```

### Other Math Functions

```python
@c_function
def fmod(x: float, y: float) -> float:
    """Floating-point remainder of x/y"""
    pass

@c_function
def fmax(x: float, y: float) -> float:
    """Maximum of x and y"""
    pass

@c_function
def fmin(x: float, y: float) -> float:
    """Minimum of x and y"""
    pass
```

## String Library (`string.h`)

### String Length and Comparison

```python
@c_include("string.h")
@c_function
def strlen(s: str) -> int:
    """String length"""
    pass

@c_function
def strcmp(s1: str, s2: str) -> int:
    """String comparison"""
    pass

@c_function
def strncmp(s1: str, s2: str, n: int) -> int:
    """String comparison (first n chars)"""
    pass

@c_function
def strcasecmp(s1: str, s2: str) -> int:
    """Case-insensitive string comparison"""
    pass
```

### String Search

```python
@c_function
def strchr(s: str, c: int) -> ptr[str]:
    """Find first occurrence of character"""
    pass

@c_function
def strrchr(s: str, c: int) -> ptr[str]:
    """Find last occurrence of character"""
    pass

@c_function
def strstr(haystack: str, needle: str) -> ptr[str]:
    """Find first occurrence of substring"""
    pass
```

### String Copying (Use with caution - manual memory management)

```python
@c_function
def strcpy(dest: ptr[str], src: str) -> ptr[str]:
    """Copy string"""
    pass

@c_function
def strncpy(dest: ptr[str], src: str, n: int) -> ptr[str]:
    """Copy string (max n chars)"""
    pass

@c_function
def strcat(dest: ptr[str], src: str) -> ptr[str]:
    """Concatenate strings"""
    pass

@c_function
def strncat(dest: ptr[str], src: str, n: int) -> ptr[str]:
    """Concatenate strings (max n chars)"""
    pass
```

## Standard I/O Library (`stdio.h`)

### Basic Output

```python
@c_include("stdio.h")
@c_function
def printf(format: str, value: int) -> int:
    """Formatted output (int version)"""
    pass

@c_function
def puts(s: str) -> int:
    """Print string with newline"""
    pass

@c_function
def putchar(c: int) -> int:
    """Print single character"""
    pass
```

### File Operations

```python
@c_function
def fopen(filename: str, mode: str) -> ptr[void]:
    """Open file"""
    pass

@c_function
def fclose(file: ptr[void]) -> int:
    """Close file"""
    pass

@c_function
def fgetc(file: ptr[void]) -> int:
    """Read character from file"""
    pass

@c_function
def fputc(c: int, file: ptr[void]) -> int:
    """Write character to file"""
    pass
```

## Standard Library (`stdlib.h`)

### Memory Management

```python
@c_include("stdlib.h")
@c_function
def malloc(size: int) -> ptr[void]:
    """Allocate memory"""
    pass

@c_function
def calloc(count: int, size: int) -> ptr[void]:
    """Allocate and zero memory"""
    pass

@c_function
def realloc(ptr: ptr[void], size: int) -> ptr[void]:
    """Reallocate memory"""
    pass

@c_function
def free(ptr: ptr[void]) -> None:
    """Free memory"""
    pass
```

### Conversion Functions

```python
@c_function
def atoi(s: str) -> int:
    """String to integer"""
    pass

@c_function
def atof(s: str) -> float:
    """String to float"""
    pass

@c_function
def strtol(s: str, endptr: ptr[ptr[str]], base: int) -> int:
    """String to long with error checking"""
    pass

@c_function
def strtod(s: str, endptr: ptr[ptr[str]]) -> float:
    """String to double with error checking"""
    pass
```

### Other Standard Functions

```python
@c_function
def abs(x: int) -> int:
    """Absolute value (integer)"""
    pass

@c_function
def exit(status: int) -> None:
    """Exit program"""
    pass

@c_function
def rand() -> int:
    """Random number"""
    pass

@c_function
def srand(seed: int) -> None:
    """Seed random number generator"""
    pass
```

## Memory Functions (`string.h`)

```python
@c_function
def memcpy(dest: ptr[void], src: ptr[void], n: int) -> ptr[void]:
    """Copy memory"""
    pass

@c_function
def memmove(dest: ptr[void], src: ptr[void], n: int) -> ptr[void]:
    """Move memory (safe for overlapping)"""
    pass

@c_function
def memset(ptr: ptr[void], value: int, n: int) -> ptr[void]:
    """Set memory to value"""
    pass

@c_function
def memcmp(ptr1: ptr[void], ptr2: ptr[void], n: int) -> int:
    """Compare memory"""
    pass
```

## Usage Examples

### Complete Math Example

```python
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

def main():
    # Calculate distance between two points
    x1: float = 1.0
    y1: float = 2.0
    x2: float = 4.0
    y2: float = 6.0
    
    dx: float = x2 - x1
    dy: float = y2 - y1
    distance: float = sqrt(pow(dx, 2.0) + pow(dy, 2.0))
    
    print(distance)  # 5.0
```

### String Processing Example

```python
@c_include("string.h")
@c_function
def strlen(s: str) -> int:
    pass

@c_function
def strcmp(s1: str, s2: str) -> int:
    pass

@c_function
def strchr(s: str, c: int) -> ptr[str]:
    pass

def main():
    text: str = "Hello, World!"
    length: int = strlen(text)
    print(length)  # 13
    
    # Compare strings
    result: int = strcmp("abc", "abc")
    print(result)  # 0 (equal)
```

## Notes

1. **Return Values**: Pay attention to C return conventions
   - `strcmp` returns 0 for equal strings
   - `strchr` returns NULL (null pointer) if not found
   - `malloc` returns NULL on failure

2. **Memory Management**: Functions like `malloc`, `strcpy` require careful memory management

3. **Error Handling**: C functions often use return values or global `errno` for error reporting

4. **Type Safety**: Pyrinas enforces type safety at compile time, but C functions may have different runtime behavior

5. **Platform Differences**: Some functions may behave differently on different platforms