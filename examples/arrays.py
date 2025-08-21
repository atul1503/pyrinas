def main():
    my_array: array[int, 5]
    
    # Fill the array
    i: int = 0
    while i < 5:
        my_array[i] = i * 10
        i = i + 1
        
    # Read from the array
    i = 0
    while i < 5:
        print(my_array[i])
        i = i + 1