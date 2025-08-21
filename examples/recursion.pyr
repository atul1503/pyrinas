def factorial(n: int) -> int:
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

def countdown(n: int) -> None:
    if n > 0:
        print(n)
        countdown(n - 1)

def main():
    # Test factorial
    fact5: int = factorial(5)
    print(fact5)  # Should print 120
    
    # Test fibonacci
    fib6: int = fibonacci(6)
    print(fib6)   # Should print 8
    
    # Test countdown
    countdown(3)  # Should print 3, 2, 1