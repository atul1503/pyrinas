#include "pyrinas.h"
#include <stdio.h>
#include <stdlib.h>

// Result utility functions

bool is_ok(Result r) {
    return r.type == OK;
}

bool is_err(Result r) {
    return r.type == ERR;
}

int unwrap_int(Result r) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: attempted to unwrap an Err result\n");
        exit(1);
    }
    return r.value.int_val;
}

float unwrap_float(Result r) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: attempted to unwrap an Err result\n");
        exit(1);
    }
    return r.value.float_val;
}

char* unwrap_str(Result r) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: attempted to unwrap an Err result\n");
        exit(1);
    }
    return r.value.str_val;
}

void* unwrap_ptr(Result r) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: attempted to unwrap an Err result\n");
        exit(1);
    }
    return r.value.ptr_val;
}

int unwrap_or_int(Result r, int default_val) {
    if (r.type == ERR) {
        return default_val;
    }
    return r.value.int_val;
}

float unwrap_or_float(Result r, float default_val) {
    if (r.type == ERR) {
        return default_val;
    }
    return r.value.float_val;
}

char* unwrap_or_str(Result r, char* default_val) {
    if (r.type == ERR) {
        return default_val;
    }
    return r.value.str_val;
}

void* unwrap_or_ptr(Result r, void* default_val) {
    if (r.type == ERR) {
        return default_val;
    }
    return r.value.ptr_val;
}

int expect_int(Result r, char* message) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: %s\n", message);
        exit(1);
    }
    return r.value.int_val;
}

float expect_float(Result r, char* message) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: %s\n", message);
        exit(1);
    }
    return r.value.float_val;
}

char* expect_str(Result r, char* message) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: %s\n", message);
        exit(1);
    }
    return r.value.str_val;
}

void* expect_ptr(Result r, char* message) {
    if (r.type == ERR) {
        fprintf(stderr, "Error: %s\n", message);
        exit(1);
    }
    return r.value.ptr_val;
}
