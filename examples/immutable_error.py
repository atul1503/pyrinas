# This should cause compilation errors
from typing import Final

def main():
    # Immutable variable  
    x: Final[int] = 42
    print(x)
    
    # This should cause an error
    x = 50