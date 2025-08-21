class Point:
    x: int
    y: float

def main():
    p1: Point
    p1.x = 10
    p1.y = 20.5

    print(p1.x)
    print(p1.y)

    # Structs are value types, so this is a copy
    p2: Point = p1
    p2.x = 30

    print(p1.x) # Should still be 10
    print(p2.x) # Should be 30