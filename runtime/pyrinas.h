#ifndef PYRINAS_H
#define PYRINAS_H

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

// Generic Result type for error handling
typedef enum {
    OK,
    ERR
} ResultType;

// A generic value union
typedef union {
    int int_val;
    float float_val;
    char* str_val;
    void* ptr_val;
} Value;

typedef struct {
    ResultType type;
    Value value;
} Result;

#endif // PYRINAS_H
