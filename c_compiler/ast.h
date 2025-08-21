#ifndef AST_H
#define AST_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Forward declarations
typedef struct ASTNode ASTNode;
typedef struct Symbol Symbol;
typedef struct SymbolTable SymbolTable;

// String utilities
typedef struct {
    char* data;
    size_t length;
    size_t capacity;
} String;

String* string_new(const char* initial);
void string_append(String* str, const char* to_append);
void string_free(String* str);
char* string_cstr(String* str);

// Dynamic array for AST nodes
typedef struct {
    ASTNode** items;
    size_t count;
    size_t capacity;
} NodeArray;

NodeArray* node_array_new(void);
void node_array_push(NodeArray* arr, ASTNode* node);
void node_array_free(NodeArray* arr);

// Dynamic array for strings
typedef struct {
    char** items;
    size_t count;
    size_t capacity;
} StringArray;

StringArray* string_array_new(void);
void string_array_push(StringArray* arr, const char* str);
void string_array_free(StringArray* arr);

// AST Node Types
typedef enum {
    // Top level
    AST_MODULE,
    AST_FUNCTION_DEF,
    AST_CLASS_DEF,
    
    // Statements
    AST_ASSIGN,
    AST_ANN_ASSIGN,
    AST_IF,
    AST_WHILE,
    AST_FOR,
    AST_BREAK,
    AST_CONTINUE,
    AST_RETURN,
    AST_EXPR_STMT,
    AST_PASS,
    AST_MATCH,
    
    // Expressions
    AST_NAME,
    AST_CONSTANT,
    AST_BINOP,
    AST_UNARYOP,
    AST_COMPARE,
    AST_BOOLOP,
    AST_CALL,
    AST_ATTRIBUTE,
    AST_SUBSCRIPT,
    
    // Others
    AST_ARG,
    AST_ARGUMENTS,
    AST_MATCH_CASE
} ASTNodeType;

// Binary operators
typedef enum {
    BINOP_ADD,
    BINOP_SUB,
    BINOP_MULT,
    BINOP_DIV,
    BINOP_MOD,
    BINOP_FLOORDIV
} BinOpType;

// Unary operators
typedef enum {
    UNARYOP_NOT,
    UNARYOP_USUB,
    UNARYOP_UADD
} UnaryOpType;

// Comparison operators
typedef enum {
    CMP_EQ,
    CMP_NOTEQ,
    CMP_LT,
    CMP_LTE,
    CMP_GT,
    CMP_GTE
} CompareOpType;

// Boolean operators
typedef enum {
    BOOLOP_AND,
    BOOLOP_OR
} BoolOpType;

// Context for Name nodes
typedef enum {
    CTX_LOAD,
    CTX_STORE
} ExprContext;

// Constant value types
typedef enum {
    CONST_INT,
    CONST_FLOAT,
    CONST_STRING,
    CONST_BOOL,
    CONST_NONE
} ConstantType;

typedef struct {
    ConstantType type;
    union {
        int int_val;
        double float_val;
        char* str_val;
        bool bool_val;
    };
} ConstantValue;

// Base AST Node structure
struct ASTNode {
    ASTNodeType type;
    int line_no;
    
    union {
        // Module
        struct {
            NodeArray* body;
        } module;
        
        // Function definition
        struct {
            char* name;
            struct ASTNode* args;  // AST_ARGUMENTS
            struct ASTNode* returns;  // return type annotation
            NodeArray* body;
            NodeArray* decorator_list;
        } function_def;
        
        // Class definition
        struct {
            char* name;
            NodeArray* bases;  // base classes
            NodeArray* body;
        } class_def;
        
        // Variable assignment
        struct {
            NodeArray* targets;
            struct ASTNode* value;
        } assign;
        
        // Annotated assignment
        struct {
            struct ASTNode* target;
            struct ASTNode* annotation;
            struct ASTNode* value;  // can be NULL
        } ann_assign;
        
        // If statement
        struct {
            struct ASTNode* test;
            NodeArray* body;
            NodeArray* orelse;
        } if_stmt;
        
        // While loop
        struct {
            struct ASTNode* test;
            NodeArray* body;
        } while_stmt;
        
        // For loop
        struct {
            struct ASTNode* target;
            struct ASTNode* iter;
            NodeArray* body;
        } for_stmt;
        
        // Break/Continue
        struct {
            char* label;  // optional label
        } break_continue;
        
        // Return statement
        struct {
            struct ASTNode* value;
        } return_stmt;
        
        // Expression statement
        struct {
            struct ASTNode* value;
        } expr_stmt;
        
        // Match statement
        struct {
            struct ASTNode* subject;
            NodeArray* cases;  // AST_MATCH_CASE nodes
        } match_stmt;
        
        // Match case
        struct {
            struct ASTNode* pattern;
            NodeArray* body;
        } match_case;
        
        // Name (variable/identifier)
        struct {
            char* id;
            ExprContext ctx;
        } name;
        
        // Constant
        struct {
            ConstantValue value;
        } constant;
        
        // Binary operation
        struct {
            struct ASTNode* left;
            BinOpType op;
            struct ASTNode* right;
        } binop;
        
        // Unary operation
        struct {
            UnaryOpType op;
            struct ASTNode* operand;
        } unaryop;
        
        // Comparison
        struct {
            struct ASTNode* left;
            CompareOpType* ops;
            NodeArray* comparators;
            size_t ops_count;
        } compare;
        
        // Boolean operation
        struct {
            BoolOpType op;
            NodeArray* values;
        } boolop;
        
        // Function call
        struct {
            struct ASTNode* func;
            NodeArray* args;
        } call;
        
        // Attribute access (obj.attr)
        struct {
            struct ASTNode* value;
            char* attr;
            ExprContext ctx;
        } attribute;
        
        // Subscript (obj[index])
        struct {
            struct ASTNode* value;
            struct ASTNode* slice;
            ExprContext ctx;
        } subscript;
        
        // Function argument
        struct {
            char* arg;
            struct ASTNode* annotation;
        } arg;
        
        // Function arguments list
        struct {
            NodeArray* args;
        } arguments;
    };
};

// AST Node constructors
ASTNode* ast_module_new(NodeArray* body);
ASTNode* ast_function_def_new(const char* name, ASTNode* args, ASTNode* returns, NodeArray* body, NodeArray* decorators);
ASTNode* ast_class_def_new(const char* name, NodeArray* bases, NodeArray* body);
ASTNode* ast_assign_new(NodeArray* targets, ASTNode* value);
ASTNode* ast_ann_assign_new(ASTNode* target, ASTNode* annotation, ASTNode* value);
ASTNode* ast_if_new(ASTNode* test, NodeArray* body, NodeArray* orelse);
ASTNode* ast_while_new(ASTNode* test, NodeArray* body);
ASTNode* ast_for_new(ASTNode* target, ASTNode* iter, NodeArray* body);
ASTNode* ast_break_new(const char* label);
ASTNode* ast_continue_new(const char* label);
ASTNode* ast_return_new(ASTNode* value);
ASTNode* ast_expr_stmt_new(ASTNode* value);
ASTNode* ast_pass_new(void);
ASTNode* ast_match_new(ASTNode* subject, NodeArray* cases);
ASTNode* ast_match_case_new(ASTNode* pattern, NodeArray* body);
ASTNode* ast_name_new(const char* id, ExprContext ctx);
ASTNode* ast_constant_int_new(int value);
ASTNode* ast_constant_float_new(double value);
ASTNode* ast_constant_string_new(const char* value);
ASTNode* ast_constant_bool_new(bool value);
ASTNode* ast_constant_none_new(void);
ASTNode* ast_binop_new(ASTNode* left, BinOpType op, ASTNode* right);
ASTNode* ast_unaryop_new(UnaryOpType op, ASTNode* operand);
ASTNode* ast_compare_new(ASTNode* left, CompareOpType* ops, NodeArray* comparators, size_t ops_count);
ASTNode* ast_boolop_new(BoolOpType op, NodeArray* values);
ASTNode* ast_call_new(ASTNode* func, NodeArray* args);
ASTNode* ast_attribute_new(ASTNode* value, const char* attr, ExprContext ctx);
ASTNode* ast_subscript_new(ASTNode* value, ASTNode* slice, ExprContext ctx);
ASTNode* ast_arg_new(const char* arg, ASTNode* annotation);
ASTNode* ast_arguments_new(NodeArray* args);

// Memory management
void ast_node_free(ASTNode* node);

// Utility functions
const char* ast_node_type_name(ASTNodeType type);
void ast_print(ASTNode* node, int indent);

#endif // AST_H