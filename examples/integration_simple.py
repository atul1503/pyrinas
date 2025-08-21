# Simple integration test: Functions + Structs (basic)
# Tests basic combination of functions and structs

class Point:
    x: int
    y: int

def create_point(x_val: int, y_val: int) -> Point:
    p: Point = Point()
    p.x = x_val
    p.y = y_val
    return p

def get_distance_squared(p1: Point, p2: Point) -> int:
    dx: int = p1.x - p2.x
    dy: int = p1.y - p2.y
    return dx * dx + dy * dy

def main():
    # Test struct creation through function
    origin: Point = create_point(0, 0)
    point1: Point = create_point(3, 4)
    
    # Test struct field access
    print(point1.x)  # Should print 3
    print(point1.y)  # Should print 4
    
    # Test function with struct parameters
    dist_sq: int = get_distance_squared(origin, point1)
    print(dist_sq)   # Should print 25 (3*3 + 4*4)