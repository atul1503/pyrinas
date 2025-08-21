#include "../runtime/pyrinas.h"

struct Point {
    int x;
    float y;
};


int main() {
    struct Point p1;
    p1.x = 10;
    p1.y = 20.500000;
    printf("%d\n", p1.x);
    printf("%d\n", p1.y);
    struct Point p2 = p1;
    p2.x = 30;
    printf("%d\n", p1.x);
    printf("%d\n", p2.x);
}
