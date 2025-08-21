# Simple integration test: Functions + Pointers
# Tests basic combination of functions and pointers

def modify_value_by_pointer(ptr: 'ptr[int]', new_value: int):
    assign(ptr, new_value)

def read_value_through_pointer(ptr: 'ptr[int]') -> int:
    return deref(ptr)

def swap_values(ptr1: 'ptr[int]', ptr2: 'ptr[int]'):
    val1: int = deref(ptr1)
    val2: int = deref(ptr2)
    assign(ptr1, val2)
    assign(ptr2, val1)

def main():
    # Test pointer operations with functions
    a: int = 42
    b: int = 100
    
    a_ptr: 'ptr[int]' = addr(a)
    b_ptr: 'ptr[int]' = addr(b)
    
    # Test function that modifies through pointer
    modify_value_by_pointer(a_ptr, 50)
    
    # Test function that reads through pointer
    modified_a: int = read_value_through_pointer(a_ptr)
    print(modified_a)  # Should print 50
    
    # Test function that works with multiple pointers
    print(b)  # Should print 100 (original value)
    swap_values(a_ptr, b_ptr)
    
    # Test that values were swapped
    final_a: int = deref(a_ptr)
    final_b: int = deref(b_ptr)
    print(final_a)  # Should print 100 (swapped from b)
    print(final_b)  # Should print 50 (swapped from a)