class Point:
    x: int
    y: int

class Circle:
    center: Point
    radius: int

class Rectangle:
    top_left: Point
    bottom_right: Point
    
class ComplexShape:
    main_rect: Rectangle
    inner_circle: Circle
    name: str

def create_point(x: int, y: int) -> Point:
    p: Point = Point()
    p.x = x
    p.y = y
    return p

def create_circle(center_x: int, center_y: int, r: int) -> Circle:
    c: Circle = Circle()
    c.center = create_point(center_x, center_y)
    c.radius = r
    return c

def create_rectangle(x1: int, y1: int, x2: int, y2: int) -> Rectangle:
    rect: Rectangle = Rectangle()
    rect.top_left = create_point(x1, y1)
    rect.bottom_right = create_point(x2, y2)
    return rect

def get_rectangle_width(rect: Rectangle) -> int:
    return rect.bottom_right.x - rect.top_left.x

def get_rectangle_height(rect: Rectangle) -> int:
    return rect.bottom_right.y - rect.top_left.y

def main():
    # Test basic nested struct creation
    circle: Circle = create_circle(10, 20, 5)
    print(circle.center.x)     # Should print 10
    print(circle.center.y)     # Should print 20
    print(circle.radius)       # Should print 5
    
    # Test rectangle with nested points
    rect: Rectangle = create_rectangle(0, 0, 100, 50)
    width: int = get_rectangle_width(rect)
    height: int = get_rectangle_height(rect)
    print(width)               # Should print 100
    print(height)              # Should print 50
    
    # Test complex nested structure
    complex_shape: ComplexShape = ComplexShape()
    complex_shape.main_rect = rect
    complex_shape.inner_circle = circle
    
    # Access deeply nested values
    main_width: int = get_rectangle_width(complex_shape.main_rect)
    inner_radius: int = complex_shape.inner_circle.radius
    center_x: int = complex_shape.inner_circle.center.x
    
    print(main_width)          # Should print 100
    print(inner_radius)        # Should print 5
    print(center_x)            # Should print 10