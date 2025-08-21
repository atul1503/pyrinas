#include "pyrinas.h"

struct Point {
    int x;
    int y;
};

struct Point create_point(int x_val, int y_val) {
    struct Point p = {0};
    p.x = x_val;
    p.y = y_val;
    return p;
}
void move_point_by_pointer(struct Point* p, int dx, int dy) {
    struct Point current_p = (*p);
    int new_x = (current_p.x + dx);
    int new_y = (current_p.y + dy);
    struct Point updated = {0};
    updated.x = new_x;
    updated.y = new_y;
    *(p) = updated;
}
int distance_squared(struct Point p1, struct Point p2) {
    int dx = (p1.x - p2.x);
    int dy = (p1.y - p2.y);
    return ((dx * dx) + (dy * dy));
}

int main() {
    struct Point origin = create_point(0, 0);
    struct Point point1 = create_point(3, 4);
    printf("%d\n", point1.x);
    printf("%d\n", point1.y);
    struct Point* p1_ptr = &point1;
    move_point_by_pointer(p1_ptr, 2, 1);
    struct Point moved_point = (*p1_ptr);
    printf("%d\n", moved_point.x);
    printf("%d\n", moved_point.y);
    int dist_sq = distance_squared(origin, moved_point);
    printf("%d\n", dist_sq);
}