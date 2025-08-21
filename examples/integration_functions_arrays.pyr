# Simple integration test: Functions + Arrays
# Tests basic combination of functions and arrays

def fill_array(arr: 'array[int, 5]', start_value: int):
    i: int = 0
    while i < 5:
        arr[i] = start_value + i
        i = i + 1

def sum_array(arr: 'array[int, 5]') -> int:
    total: int = 0
    i: int = 0
    while i < 5:
        total = total + arr[i]
        i = i + 1
    return total

def find_max(arr: 'array[int, 5]') -> int:
    max_val: int = arr[0]
    i: int = 1
    while i < 5:
        if arr[i] > max_val:
            max_val = arr[i]
        i = i + 1
    return max_val

def main():
    # Test array declaration and function that modifies array
    numbers: 'array[int, 5]'
    fill_array(numbers, 10)  # Fill with 10, 11, 12, 13, 14
    
    # Test array access after function call
    print(numbers[0])  # Should print 10
    print(numbers[4])  # Should print 14
    
    # Test function that reads array
    total: int = sum_array(numbers)
    print(total)       # Should print 60 (10+11+12+13+14)
    
    # Test another function with array parameter
    max_val: int = find_max(numbers)
    print(max_val)     # Should print 14