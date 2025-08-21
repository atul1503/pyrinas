# Test immutability feature
from typing import Final

def main():
    # Mutable variable
    x: int = 5
    print(x)
    x = 10
    print(x)
    
    # Immutable variable  
    y: Final[int] = 42
    print(y)