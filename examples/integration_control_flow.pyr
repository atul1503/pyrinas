# Simple integration test: Control Flow + Arrays + Functions
# Tests combination of control flow, arrays, and functions

def process_array_with_breaks(arr: 'array[int, 5]') -> int:
    count: int = 0
    i: int = 0
    
    while i < 5:
        value: int = arr[i]
        
        # Test break condition
        if value < 0:
            break
        
        # Test continue condition
        if value > 20:
            i = i + 1
            continue
        
        count = count + 1
        i = i + 1
    
    return count

def nested_loops_with_break(limit: int) -> int:
    total: int = 0
    i: int = 0
    
    "outer"
    while i < limit:
        j: int = 0
        while j < limit:
            if i + j > 5:
                "outer"
                break
            total = total + 1
            j = j + 1
        i = i + 1
    
    return total

def main():
    # Test control flow with arrays
    test_array: 'array[int, 5]'
    test_array[0] = 5
    test_array[1] = 10
    test_array[2] = 25  # Should be skipped (> 20)
    test_array[3] = 3
    test_array[4] = 8
    
    count: int = process_array_with_breaks(test_array)
    print(count)  # Should print 3 (5, 10, 3, 8 - skipping 25)
    
    # Test nested loops with labeled break
    total: int = nested_loops_with_break(4)
    print(total)  # Should print number of iterations before break
    
    # Test simple loop with continue
    sum_even: int = 0
    i: int = 0
    while i < 10:
        if i % 2 == 1:  # Skip odd numbers
            i = i + 1
            continue
        sum_even = sum_even + i
        i = i + 1
    
    print(sum_even)  # Should print 20 (0+2+4+6+8)