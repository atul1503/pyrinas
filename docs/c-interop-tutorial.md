# C Interop Tutorial: Step by Step

This tutorial walks you through using C libraries in Pyrinas with hands-on examples.

## Prerequisites

- Pyrinas compiler installed and working
- Basic understanding of Pyrinas syntax
- C compiler (gcc) available on your system

## Tutorial 1: Your First C Function Call

Let's start with something simple - calling the C `sqrt` function from the math library.

### Step 1: Create the File

Create a new file called `first_c_call.pyr`:

```python
# first_c_call.pyr - My first C interop program

# Step 1: Include the C header
@c_include("math.h")

# Step 2: Declare the C function
@c_function
def sqrt(x: float) -> float:
    """Square root function from C math library"""
    pass  # This MUST be 'pass' - tells Pyrinas it's external

# Step 3: Use it in your code
def main():
    number: float = 16.0
    result: float = sqrt(number)
    print(result)  # Will print 4.0
```

### Step 2: Compile and Run

```bash
python3 -m pyrinas.cli first_c_call.pyr -o first_c_call
./first_c_call
```

Expected output:
```
4.000000
```

### What Happened?

1. `@c_include("math.h")` told Pyrinas to include the C math header
2. `@c_function` marked `sqrt` as an external C function
3. `pass` told Pyrinas not to generate code for this function
4. Pyrinas automatically linked with the math library (`-lm`)

## Tutorial 2: Multiple C Functions

Let's use several math functions together:

```python
# math_combo.pyr - Using multiple C math functions

@c_include("math.h")

@c_function
def sin(x: float) -> float:
    pass

@c_function
def cos(x: float) -> float:
    pass

@c_function
def pow(base: float, exponent: float) -> float:
    pass

def pythagorean_identity(angle: float) -> float:
    """Verify that sin²(x) + cos²(x) = 1"""
    sin_val: float = sin(angle)
    cos_val: float = cos(angle)
    
    sin_squared: float = pow(sin_val, 2.0)
    cos_squared: float = pow(cos_val, 2.0)
    
    return sin_squared + cos_squared

def main():
    angle: float = 0.785398  # π/4 radians (45 degrees)
    result: float = pythagorean_identity(angle)
    print(result)  # Should be very close to 1.0
```

Compile and run:
```bash
python3 -m pyrinas.cli math_combo.pyr -o math_combo
./math_combo
```

## Tutorial 3: String Functions

Now let's work with C string functions:

```python
# string_demo.pyr - Working with C string functions

@c_include("string.h")

@c_function
def strlen(s: str) -> int:
    """Get string length"""
    pass

@c_function
def strcmp(s1: str, s2: str) -> int:
    """Compare two strings"""
    pass

def analyze_string(text: str) -> None:
    """Analyze a string using C functions"""
    length: int = strlen(text)
    print(length)
    
    # strcmp returns 0 if strings are equal
    if strcmp(text, "hello") == 0:
        print(1)  # Found "hello"
    else:
        print(0)  # Not "hello"

def main():
    analyze_string("hello")      # Length: 5, Match: 1
    analyze_string("world")      # Length: 5, Match: 0  
    analyze_string("hi")         # Length: 2, Match: 0
```

## Tutorial 4: Combining Pyrinas and C Code

Here's a more complex example that combines Pyrinas logic with C functions:

```python
# calculator.pyr - A calculator using C math functions

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

@c_function
def fabs(x: float) -> float:
    pass

def calculate_triangle_area(a: float, b: float, c: float) -> float:
    """Calculate triangle area using Heron's formula with C functions"""
    # Semi-perimeter
    s: float = (a + b + c) / 2.0
    
    # Heron's formula: sqrt(s * (s-a) * (s-b) * (s-c))
    term1: float = s - a
    term2: float = s - b  
    term3: float = s - c
    
    under_sqrt: float = s * term1 * term2 * term3
    area: float = sqrt(under_sqrt)
    
    return area

def distance_between_points(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate distance between two points"""
    dx: float = x2 - x1
    dy: float = y2 - y1
    
    dx_squared: float = pow(dx, 2.0)
    dy_squared: float = pow(dy, 2.0)
    
    return sqrt(dx_squared + dy_squared)

def main():
    # Test triangle area (3-4-5 triangle)
    area: float = calculate_triangle_area(3.0, 4.0, 5.0)
    print(area)  # Should be 6.0
    
    # Test distance calculation
    dist: float = distance_between_points(0.0, 0.0, 3.0, 4.0)
    print(dist)  # Should be 5.0
```

## Tutorial 5: Error Handling Pattern

When working with C functions, it's important to handle potential errors:

```python
# safe_math.pyr - Safe C function usage

@c_include("math.h")

@c_function
def sqrt(x: float) -> float:
    pass

@c_function
def log(x: float) -> float:
    pass

def safe_sqrt(x: float) -> Result[float, str]:
    """Safe square root with error checking"""
    if x < 0.0:
        return Err("Cannot take square root of negative number")
    
    result: float = sqrt(x)
    return Ok(result)

def safe_log(x: float) -> Result[float, str]:
    """Safe logarithm with error checking"""
    if x <= 0.0:
        return Err("Logarithm undefined for non-positive numbers")
    
    result: float = log(x)
    return Ok(result)

def main():
    # Test safe functions
    sqrt_result: Result[float, str] = safe_sqrt(16.0)
    if is_ok(sqrt_result):
        value: float = unwrap_float(sqrt_result)
        print(value)  # 4.0
    
    log_result: Result[float, str] = safe_log(-1.0)
    if is_err(log_result):
        print(1)  # Error detected
```

## Common Patterns

### Pattern 1: Header + Functions Together

```python
# Group related functions with their header
@c_include("math.h")
@c_function
def sin(x: float) -> float:
    pass

@c_function  
def cos(x: float) -> float:
    pass
```

### Pattern 2: Multiple Headers

```python
# Multiple headers for different function groups
@c_include("math.h")
@c_function
def sqrt(x: float) -> float:
    pass

@c_include("string.h")
@c_function
def strlen(s: str) -> int:
    pass
```

### Pattern 3: Wrapper Functions

```python
# Create Pyrinas wrappers for complex C functions
@c_function
def pow(base: float, exp: float) -> float:
    pass

def square(x: float) -> float:
    """Convenience function for squaring"""
    return pow(x, 2.0)

def cube(x: float) -> float:
    """Convenience function for cubing"""
    return pow(x, 3.0)
```

## Debugging Tips

### 1. Check Generated C Code

Look at the generated `.c` file to see what Pyrinas produces:

```bash
python3 -m pyrinas.cli my_program.pyr -o my_program
cat my_program.c  # Check the generated C code
```

### 2. Verify Headers Are Included

Make sure you see your headers in the generated code:
```c
#include "pyrinas.h"
#include <math.h>      // Your header should be here
#include <string.h>    // And this one too
```

### 3. Check Function Signatures

Verify the C function signatures match your declarations:
```c
float result = sin(x);  // Should match your Pyrinas declaration
```

## Exercises

Try these exercises to practice C interop:

### Exercise 1: Temperature Converter
Create a program that uses C math functions to convert between Celsius and Fahrenheit.

### Exercise 2: String Utilities  
Write a program that uses C string functions to count vowels in a string.

### Exercise 3: Math Library
Create a small math library using C functions for common calculations.

### Exercise 4: File Processing
Use C I/O functions to read and process a text file.

## Next Steps

- Read the [API Reference](c-interop-api.md) for complete function lists
- Check [Advanced Usage](c-interop-advanced.md) for custom libraries
- See [examples/](../examples/) for more complex examples

## Troubleshooting

**Problem: "Header not found"**
- Make sure the header name is correct and available on your system
- Check that you're using standard C library headers

**Problem: "Function not linking"**  
- Verify the function exists in the header you included
- Some functions may require additional library flags

**Problem: "Type mismatch"**
- Double-check your type annotations match the C function signature
- Remember: `char*` maps to `str`, `int*` maps to `ptr[int]`