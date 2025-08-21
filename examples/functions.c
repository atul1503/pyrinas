#include "../runtime/pyrinas.h"

int add(int a, int b) {
    return (a + b);
}


int main() {
    int c = add(5, 3);
    printf("%d\n", c);
}
