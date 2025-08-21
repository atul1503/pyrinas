# Integration test: Complex Control Flow + Arrays + Functions
# Tests nested loops with labeled breaks, arrays, and functions

def find_pair_sum(matrix: 'array[int, 9]', target: int) -> bool:
    # Simulate a 3x3 matrix as flat array
    # Test nested loops with labeled break
    i: int = 0
    "outer_loop"
    while i < 3:
        j: int = 0
        "inner_loop"
        while j < 3:
            k: int = j + 1
            while k < 3:
                # Calculate indices for 3x3 matrix
                idx1: int = i * 3 + j
                idx2: int = i * 3 + k
                
                val1: int = matrix[idx1]
                val2: int = matrix[idx2]
                sum_val: int = val1 + val2
                
                if sum_val == target:
                    return True
                
                # Test continue in nested loop
                if sum_val > target:
                    "inner_loop"
                    continue
                
                k = k + 1
            
            # Test labeled break
            if j == 1:
                "outer_loop"  
                break
            
            j = j + 1
        i = i + 1
    
    return False

def process_array_with_breaks(arr: 'array[int, 5]') -> int:
    count: int = 0
    i: int = 0
    
    "processing_loop"
    while i < 5:
        value: int = arr[i]
        
        # Test multiple break conditions
        if value < 0:
            "processing_loop"
            break
        
        if value % 2 == 0:
            count = count + 1
        
        # Test continue
        if value > 10:
            i = i + 1
            "processing_loop"
            continue
        
        count = count + value % 3
        i = i + 1
    
    return count

def main():
    # Test array initialization with function calls
    test_matrix: 'array[int, 9]'
    test_matrix[0] = 1
    test_matrix[1] = 2
    test_matrix[2] = 3
    test_matrix[3] = 4
    test_matrix[4] = 5
    test_matrix[5] = 6
    test_matrix[6] = 7
    test_matrix[7] = 8
    test_matrix[8] = 9
    
    # Test function with complex control flow
    found: bool = find_pair_sum(test_matrix, 9)  # Looking for pair that sums to 9
    if found:
        print(1)  # Found pair
    else:
        print(0)  # No pair found
    
    # Test another complex control flow function
    test_array: 'array[int, 5]'
    test_array[0] = 2
    test_array[1] = 7
    test_array[2] = 4
    test_array[3] = 11
    test_array[4] = 6
    
    result: int = process_array_with_breaks(test_array)
    print(result)  # Should print calculated count