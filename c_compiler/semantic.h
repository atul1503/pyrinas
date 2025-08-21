#ifndef SEMANTIC_H
#define SEMANTIC_H

#include "ast.h"
#include <stdbool.h>

// Symbol types
typedef enum {
    SYM_VARIABLE,
    SYM_FUNCTION,
    SYM_STRUCT,
    SYM_ENUM,
    SYM_INTERFACE,
    SYM_MODULE
} SymbolType;

// Forward declarations
typedef struct Symbol Symbol;
typedef struct SymbolTable SymbolTable;
typedef struct SemanticAnalyzer SemanticAnalyzer;

// Symbol structure
struct Symbol {
    char* name;
    SymbolType type;
    char* value_type;  // Type of the symbol (int, float, etc.)
    
    // Function-specific
    StringArray* param_types;
    char* return_type;
    
    // Struct/Interface-specific
    struct {
        char** field_names;
        char** field_types;
        size_t field_count;
    } fields;
    
    struct {
        char** method_names;
        StringArray** method_param_types;
        char** method_return_types;
        size_t method_count;
    } methods;
    
    // Enum-specific
    struct {
        char** member_names;
        int* member_values;
        size_t member_count;
    } enum_members;
    
    // General flags
    bool immutable;
    bool is_c_function;
    char* c_library;
    
    // Interface implementation
    StringArray* implements;
    
    // Module exports
    SymbolTable* exports;
};

// Symbol table scope
typedef struct Scope {
    Symbol** symbols;
    size_t count;
    size_t capacity;
    struct Scope* parent;
} Scope;

// Symbol table
struct SymbolTable {
    Scope* current_scope;
    Scope* global_scope;
};

// Semantic analyzer
struct SemanticAnalyzer {
    SymbolTable* symbol_table;
    char* current_function_return_type;
    int loop_depth;
    StringArray* loop_labels;
    
    // C interop tracking
    StringArray* c_includes;
    SymbolTable* c_functions;
    StringArray* c_libraries;
    
    // Module system
    char* current_file;
    SymbolTable* imported_modules;
    
    // Error tracking
    bool has_error;
    char* error_message;
};

// Symbol management
Symbol* symbol_new(const char* name, SymbolType type, const char* value_type);
void symbol_free(Symbol* symbol);
void symbol_add_field(Symbol* symbol, const char* field_name, const char* field_type);
void symbol_add_method(Symbol* symbol, const char* method_name, StringArray* param_types, const char* return_type);
void symbol_add_enum_member(Symbol* symbol, const char* member_name, int value);

// Scope management
Scope* scope_new(Scope* parent);
void scope_free(Scope* scope);
void scope_insert(Scope* scope, Symbol* symbol);
Symbol* scope_lookup(Scope* scope, const char* name);

// Symbol table management
SymbolTable* symbol_table_new(void);
void symbol_table_free(SymbolTable* table);
void symbol_table_push_scope(SymbolTable* table);
void symbol_table_pop_scope(SymbolTable* table);
void symbol_table_insert(SymbolTable* table, Symbol* symbol);
Symbol* symbol_table_lookup(SymbolTable* table, const char* name);
Symbol* symbol_table_lookup_current_scope(SymbolTable* table, const char* name);

// Semantic analyzer
SemanticAnalyzer* semantic_analyzer_new(const char* current_file);
void semantic_analyzer_free(SemanticAnalyzer* analyzer);

// Analysis functions
bool analyze_ast(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_module(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_function_def(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_class_def(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_assign(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_ann_assign(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_if(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_while(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_for(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_return(SemanticAnalyzer* analyzer, ASTNode* node);
bool analyze_expression(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_name(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_constant(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_binop(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_unaryop(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_compare(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_boolop(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_call(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_attribute(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);
bool analyze_subscript(SemanticAnalyzer* analyzer, ASTNode* node, char** result_type);

// Type utilities
char* get_type_name(ASTNode* annotation);
bool types_compatible(const char* type1, const char* type2);
bool is_pointer_type(const char* type);
bool is_array_type(const char* type);
bool is_result_type(const char* type);
char* extract_pointer_base_type(const char* pointer_type);
void parse_array_type(const char* array_type, char** base_type, int* size);
void parse_result_type(const char* result_type, char** success_type, char** error_type);

// Error handling
void semantic_error(SemanticAnalyzer* analyzer, const char* message);

#endif // SEMANTIC_H