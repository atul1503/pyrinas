#include "pyrinas.h"

struct Student {
    int id;
    int grade;
};

struct Student create_student(int student_id, int student_grade) {
    struct Student s = {0};
    s.id = student_id;
    s.grade = student_grade;
    return s;
}
struct Student find_best_student(struct Student* students) {
    struct Student best = students[0];
    int i = 1;
    while ((i < 3)) {
        struct Student current = students[i];
        if ((current.grade > best.grade)) {
            best = current;
        }
        i = (i + 1);
    }
    return best;
}
int calculate_average_grade(struct Student* students) {
    int total = 0;
    int i = 0;
    while ((i < 3)) {
        struct Student current = students[i];
        total = (total + current.grade);
        i = (i + 1);
    }
    return (total / 3);
}

int main() {
    struct Student students[3];
    students[0] = create_student(101, 85);
    students[1] = create_student(102, 92);
    students[2] = create_student(103, 78);
    struct Student first_student = students[0];
    printf("%d\n", first_student.id);
    printf("%d\n", first_student.grade);
    struct Student best = find_best_student(students);
    printf("%d\n", best.id);
    printf("%d\n", best.grade);
    int avg = calculate_average_grade(students);
    printf("%d\n", avg);
}