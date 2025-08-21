# Basic immutability test
from typing import Final

def main():
    # Mutable variable (works fine)
    x: int = 5
    print(x)
    x = 10  # ✅ Should work
    print(x)
    
    # Immutable variable  
    y: Final[int] = 42
    print(y)
    # y = 50  # ❌ This should cause a compilation error
    
    # Immutable with different types
    name: Final[str] = "Hello"
    print(name)
    
    pi: Final[float] = 3.14
    print(int(pi))