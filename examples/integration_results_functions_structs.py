# Integration test: Result Types + Functions + Structs
# Tests Result types combined with functions and structs

class Point:
    x: int
    y: int

def create_safe_point(x_val: int, y_val: int) -> (Point, str):
    # Test Result type with struct return
    if x_val < 0 or y_val < 0:
        return Err("Coordinates cannot be negative")
    
    if x_val > 1000 or y_val > 1000:
        return Err("Coordinates too large")
    
    p: Point = Point()
    p.x = x_val
    p.y = y_val
    return Ok(p)

def divide_coordinates(p: Point, divisor: int) -> (Point, str):
    # Test Result type with struct parameter and return
    if divisor == 0:
        return Err("Cannot divide by zero")
    
    result: Point = Point()
    result.x = p.x / divisor
    result.y = p.y / divisor
    return Ok(result)

def calculate_distance_safe(p1: Point, p2: Point) -> (int, str):
    # Test Result type with multiple struct parameters
    dx: int = p1.x - p2.x
    dy: int = p1.y - p2.y
    
    # Simplified distance calculation (no sqrt)
    dist_squared: int = dx * dx + dy * dy
    
    if dist_squared < 0:  # Should never happen, but for testing
        return Err("Invalid distance calculation")
    
    return Ok(dist_squared)

def main():
    # Test Result type creation - these should succeed
    point1_result = create_safe_point(10, 20)  # Should be Ok
    point2_result = create_safe_point(5, 15)   # Should be Ok
    
    # Test Result type creation - these should fail
    invalid_result = create_safe_point(-5, 10)    # Should be Err (negative x)
    too_large_result = create_safe_point(2000, 5) # Should be Err (too large x)
    
    # For now, we can't actually check the Results, so just print success indicators
    print(1)  # Point creation tests completed
    
    # Test Result type with struct operations
    test_point: Point = Point()
    test_point.x = 100
    test_point.y = 50
    
    divide_result = divide_coordinates(test_point, 2)   # Should be Ok
    divide_error = divide_coordinates(test_point, 0)    # Should be Err
    
    print(1)  # Division tests completed
    
    # Test Result type with multiple struct parameters
    p1: Point = Point()
    p1.x = 3
    p1.y = 4
    
    p2: Point = Point()
    p2.x = 0
    p2.y = 0
    
    distance_result = calculate_distance_safe(p1, p2)  # Should be Ok(25)
    
    print(1)  # Distance calculation completed
    
    # Note: Once we implement Result helper functions (is_ok, unwrap, etc.),
    # we could actually check and use these Results properly