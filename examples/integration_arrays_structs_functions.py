# Integration test: Arrays + Structs + Functions
# Tests arrays of structs and functions that manipulate them

class Student:
    id: int
    grade: int

def create_student(student_id: int, student_grade: int) -> Student:
    s: Student = Student()
    s.id = student_id
    s.grade = student_grade
    return s

def find_best_student(students: 'array[Student, 3]') -> Student:
    best: Student = students[0]
    i: int = 1
    while i < 3:
        current: Student = students[i]
        if current.grade > best.grade:
            best = current
        i = i + 1
    return best

def calculate_average_grade(students: 'array[Student, 3]') -> int:
    total: int = 0
    i: int = 0
    while i < 3:
        current: Student = students[i]
        total = total + current.grade
        i = i + 1
    return total / 3

def main():
    # Test array of structs initialization
    students: 'array[Student, 3]'
    
    # Test struct creation and array assignment
    students[0] = create_student(101, 85)
    students[1] = create_student(102, 92)
    students[2] = create_student(103, 78)
    
    # Test array access and struct field access
    first_student: Student = students[0]
    print(first_student.id)     # Should print 101
    print(first_student.grade)  # Should print 85
    
    # Test function with array parameter
    best: Student = find_best_student(students)
    print(best.id)    # Should print 102 (student with grade 92)
    print(best.grade) # Should print 92
    
    # Test another function with array parameter
    avg: int = calculate_average_grade(students)
    print(avg)  # Should print 85 ((85+92+78)/3 = 85)