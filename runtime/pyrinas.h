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

// Result utility functions
bool is_ok(Result r);
bool is_err(Result r);
int unwrap_int(Result r);
float unwrap_float(Result r);
char* unwrap_str(Result r);
void* unwrap_ptr(Result r);
int unwrap_or_int(Result r, int default_val);
float unwrap_or_float(Result r, float default_val);
char* unwrap_or_str(Result r, char* default_val);
void* unwrap_or_ptr(Result r, void* default_val);
int expect_int(Result r, char* message);
float expect_float(Result r, char* message);
char* expect_str(Result r, char* message);
void* expect_ptr(Result r, char* message);

#endif // PYRINAS_H
