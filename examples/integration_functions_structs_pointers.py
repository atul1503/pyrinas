# Integration test: Functions + Structs + Pointers
# Tests that functions can work with struct pointers, modify them, and return them

class Point:
    x: int
    y: int

def create_point(x_val: int, y_val: int) -> Point:
    p: Point = Point()
    p.x = x_val
    p.y = y_val
    return p

def move_point_by_pointer(p: 'ptr[Point]', dx: int, dy: int):
    # Test dereferencing pointer and accessing struct fields
    current_p: Point = deref(p)
    new_x: int = current_p.x + dx
    new_y: int = current_p.y + dy
    
    # Create updated point and assign back through pointer
    updated: Point = Point()
    updated.x = new_x
    updated.y = new_y
    assign(p, updated)

def distance_squared(p1: Point, p2: Point) -> int:
    dx: int = p1.x - p2.x
    dy: int = p1.y - p2.y
    return dx * dx + dy * dy

def main():
    # Test struct creation and function calls
    origin: Point = create_point(0, 0)
    point1: Point = create_point(3, 4)
    
    print(point1.x)  # Should print 3
    print(point1.y)  # Should print 4
    
    # Test pointer operations with structs
    p1_ptr: 'ptr[Point]' = addr(point1)
    move_point_by_pointer(p1_ptr, 2, 1)  # Move from (3,4) to (5,5)
    
    moved_point: Point = deref(p1_ptr)
    print(moved_point.x)  # Should print 5
    print(moved_point.y)  # Should print 5
    
    # Test function with struct parameters
    dist_sq: int = distance_squared(origin, moved_point)
    print(dist_sq)  # Should print 50 (5*5 + 5*5)