#include "pyrinas.h"

struct Point {
    int x;
    int y;
};

Result create_safe_point(int x_val, int y_val) {
    if (((x_val < 0)||(y_val < 0))) {
        return (Result){ .type = ERR, .value = { .str_val = "Coordinates cannot be negative" } };
    }
    if (((x_val > 1000)||(y_val > 1000))) {
        return (Result){ .type = ERR, .value = { .str_val = "Coordinates too large" } };
    }
    struct Point p = {0};
    p.x = x_val;
    p.y = y_val;
    return (Result){ .type = OK, .value = { .int_val = p } };
}
Result divide_coordinates(struct Point p, int divisor) {
    if ((divisor == 0)) {
        return (Result){ .type = ERR, .value = { .str_val = "Cannot divide by zero" } };
    }
    struct Point result = {0};
    result.x = (p.x / divisor);
    result.y = (p.y / divisor);
    return (Result){ .type = OK, .value = { .int_val = result } };
}
Result calculate_distance_safe(struct Point p1, struct Point p2) {
    int dx = (p1.x - p2.x);
    int dy = (p1.y - p2.y);
    int dist_squared = ((dx * dx) + (dy * dy));
    if ((dist_squared < 0)) {
        return (Result){ .type = ERR, .value = { .str_val = "Invalid distance calculation" } };
    }
    return (Result){ .type = OK, .value = { .int_val = dist_squared } };
}

int main() {
    point1_result = create_safe_point(10, 20);
    point2_result = create_safe_point(5, 15);
    invalid_result = create_safe_point(5, 10);
    too_large_result = create_safe_point(2000, 5);
    printf("%d\n", 1);
    struct Point test_point = {0};
    test_point.x = 100;
    test_point.y = 50;
    divide_result = divide_coordinates(test_point, 2);
    divide_error = divide_coordinates(test_point, 0);
    printf("%d\n", 1);
    struct Point p1 = {0};
    p1.x = 3;
    p1.y = 4;
    struct Point p2 = {0};
    p2.x = 0;
    p2.y = 0;
    distance_result = calculate_distance_safe(p1, p2);
    printf("%d\n", 1);
}