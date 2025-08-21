#include "pyrinas.h"
#include <math.h>
#include <string.h>
const float PI = 3.14159265359;
float square(float x) {
    "Calculate the square of a number";
    return (x * x);
}
float cube(float x) {
    "Calculate the cube of a number";
    return ((x * x) * x);
}
float hypotenuse(float a, float b) {
    "Calculate hypotenuse using Pythagorean theorem";
    return sqrt((square(a) + square(b)));
}
float circle_area(float radius) {
    "Calculate the area of a circle";
    return (PI * square(radius));
}
float degrees_to_radians(float degrees) {
    "Convert degrees to radians";
    return ((degrees * PI) / 180.0);
}
float radians_to_degrees(float radians) {
    "Convert radians to degrees";
    return ((radians * 180.0) / PI);
}
float distance_2d(float x1, float y1, float x2, float y2) {
    "Calculate 2D distance between two points";
    float dx = (x2 - x1);
    float dy = (y2 - y1);
    return sqrt((square(dx) + square(dy)));
}
int string_length(char* s) {
    "Get the length of a string";
    return strlen(s);
}
int strings_equal(char* s1, char* s2) {
    "Check if two strings are equal";
    return (strcmp(s1, s2) == 0);
}
int string_compare(char* s1, char* s2) {
    "Compare two strings lexicographically";
    return strcmp(s1, s2);
}
int is_empty(char* s) {
    "Check if a string is empty";
    return (strlen(s) == 0);
}
int count_words(char* text) {
    "Count words in a string (simplified - counts spaces + 1)";
    if (is_empty(text)) {
        return 0;
    }
    int length = strlen(text);
    int word_count = 1;
    return word_count;
}
struct Point create_point(float x, float y) {
    "Create a new point";
    struct Point p = {0};
    p.x = x;
    p.y = y;
    return p;
}
struct Rectangle create_rectangle(float width, float height) {
    "Create a new rectangle";
    struct Rectangle r = {0};
    r.width = width;
    r.height = height;
    return r;
}
struct Circle create_circle(float radius) {
    "Create a new circle";
    struct Circle c = {0};
    c.radius = radius;
    return c;
}
float rectangle_area(struct Rectangle rect) {
    "Calculate the area of a rectangle";
    return (rect.width * rect.height);
}
float rectangle_perimeter(struct Rectangle rect) {
    "Calculate the perimeter of a rectangle";
    return (2.0 * (rect.width + rect.height));
}

int main() {
    float area = circle_area(1.0);
    printf("%d\n", 3);
    int length = string_length("hi");
    printf("%d\n", 2);
    circle = create_circle(5.0);
    printf("%d\n", 5);
}