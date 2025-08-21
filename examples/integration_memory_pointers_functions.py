# Integration test: Memory Management + Pointers + Functions
# Tests dynamic memory allocation with functions and pointers

def allocate_int_array(size: int) -> 'ptr[int]':
    # Test sizeof and malloc together
    element_size: int = sizeof("int")
    total_size: int = size * element_size
    ptr: 'ptr[void]' = malloc(total_size)
    int_ptr: 'ptr[int]' = ptr  # Test void pointer assignment
    return int_ptr

def fill_array(arr: 'ptr[int]', size: int, start_value: int):
    i: int = 0
    while i < size:
        # Test pointer arithmetic simulation
        current_ptr: 'ptr[int]' = arr  # Simplified - would need actual pointer arithmetic
        assign(current_ptr, start_value + i)
        i = i + 1

def sum_array(arr: 'ptr[int]', size: int) -> int:
    total: int = 0
    i: int = 0
    while i < size:
        # Test dereferencing in loop
        value: int = deref(arr)
        total = total + value
        i = i + 1
    return total

def cleanup_array(arr: 'ptr[int]'):
    # Test free function
    free(arr)

def main():
    # Test dynamic memory allocation
    size: int = 5
    numbers: 'ptr[int]' = allocate_int_array(size)
    
    # Test function with pointer parameter
    fill_array(numbers, size, 10)  # Fill with values 10, 11, 12, 13, 14
    
    # Test dereferencing allocated memory
    first_value: int = deref(numbers)
    print(first_value)  # Should print 10
    
    # Note: This is simplified since we don't have pointer arithmetic yet
    # In a full implementation, we'd need to advance the pointer
    
    # Test memory cleanup
    cleanup_array(numbers)
    
    print(255)  # Success indicator