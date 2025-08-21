def main() -> int:
    a: bool = True
    b: bool = False
    c: bool = True
    
    result_and: bool = a and b
    result_or: bool = a or b
    result_not: bool = not b
    
    print(result_and)
    print(result_or)
    print(result_not)
    
    complex_expr: bool = (a and c) or (not b)
    print(complex_expr)
    
    return 0
