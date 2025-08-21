def main():
    x: int = 42
    p1: 'ptr[int]' = addr(x)
    p2: 'ptr[ptr[int]]' = addr(p1)

    # Dereference twice to get the original value
    print(deref(deref(p2)))

    # Change the value using the double pointer
    assign(deref(p2), 100)
    print(x)

    # You can also change what the first pointer points to
    y: int = 50
    assign(p2, addr(y))
    print(deref(p1))