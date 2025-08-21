#include "../runtime/pyrinas.h"

int main() {
    int x = 10;
    float y = 3.500000;
    float result_add = (x + y);
    int result_sub = (x - 5);
    float result_mul = (y * 2.000000);
    float result_div = (x / 4.000000);
    printf("%d\n", result_add);
    printf("%d\n", result_sub);
    printf("%d\n", result_mul);
    printf("%d\n", result_div);
    int is_equal = x == 10;
    int is_greater = y == x;
    printf("%d\n", is_equal);
    printf("%d\n", is_greater);
    return 0;
}
