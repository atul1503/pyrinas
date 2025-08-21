# Integration test: Kitchen Sink - All Features Combined
# Tests as many language features together as possible

class Point:
    x: int
    y: float

class Rectangle:
    top_left: Point
    width: int
    height: int

def create_point(x_val: int, y_val: float) -> Point:
    p: Point = Point()
    p.x = x_val
    p.y = y_val
    return p

def create_rectangle(x: int, y: float, w: int, h: int) -> Rectangle:
    rect: Rectangle = Rectangle()
    rect.top_left = create_point(x, y)
    rect.width = w
    rect.height = h
    return rect

def calculate_areas(rectangles: 'array[Rectangle, 3]') -> 'ptr[float]':
    # Test dynamic memory allocation for results
    float_size: int = sizeof("float")
    total_size: int = 3 * float_size
    areas_ptr: 'ptr[void]' = malloc(total_size)
    areas: 'ptr[float]' = areas_ptr
    
    i: int = 0
    "calculation_loop"
    while i < 3:
        rect: Rectangle = rectangles[i]
        
        # Test struct field access and arithmetic
        area: float = float(rect.width * rect.height)
        
        # Test pointer assignment (simplified - would need proper pointer arithmetic)
        assign(areas, area)
        
        # Test labeled continue
        if area > 100.0:
            i = i + 1
            "calculation_loop"
            continue
        
        i = i + 1
    
    return areas

def process_rectangles_with_pointers(rect_ptr: 'ptr[Rectangle]', count: int) -> bool:
    # Test multi-level dereferencing and complex conditions
    i: int = 0
    valid_count: int = 0
    
    "validation_loop"
    while i < count:
        # Test pointer dereferencing with structs
        rect: Rectangle = deref(rect_ptr)
        
        # Test nested struct access
        x_coord: int = rect.top_left.x
        y_coord: float = rect.top_left.y
        
        # Test complex boolean logic
        valid_position: bool = x_coord >= 0 and y_coord >= 0.0
        valid_size: bool = rect.width > 0 and rect.height > 0
        
        if valid_position and valid_size:
            valid_count = valid_count + 1
        else:
            # Test labeled break from nested conditions
            if x_coord < -100:
                "validation_loop"
                break
        
        i = i + 1
    
    # Test comparison returning boolean
    return valid_count == count

def main():
    # Test struct creation and array initialization
    rectangles: 'array[Rectangle, 3]'
    rectangles[0] = create_rectangle(0, 0.0, 10, 5)
    rectangles[1] = create_rectangle(5, 2.5, 8, 6)
    rectangles[2] = create_rectangle(-1, 1.0, 12, 4)
    
    # Test function returning pointer and memory management
    areas: 'ptr[float]' = calculate_areas(rectangles)
    
    # Test dereferencing returned pointer
    first_area: float = deref(areas)
    print(int(first_area))  # Should print 50 (10 * 5)
    
    # Test pointer to struct operations
    first_rect: Rectangle = rectangles[0]
    rect_ptr: 'ptr[Rectangle]' = addr(first_rect)
    
    # Test function with pointer parameter
    all_valid: bool = process_rectangles_with_pointers(rect_ptr, 1)
    if all_valid:
        print(1)  # All rectangles valid
    else:
        print(0)  # Some invalid
    
    # Test complex struct field access
    second_rect: Rectangle = rectangles[1]
    top_left_x: int = second_rect.top_left.x
    top_left_y: float = second_rect.top_left.y
    
    print(top_left_x)           # Should print 5
    print(int(top_left_y))      # Should print 2
    
    # Test arithmetic with struct fields
    total_width: int = rectangles[0].width + rectangles[1].width + rectangles[2].width
    print(total_width)          # Should print 30 (10 + 8 + 12)
    
    # Test memory cleanup
    free(areas)