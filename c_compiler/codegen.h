#ifndef CODEGEN_H
#define CODEGEN_H

#include "ast.h"
#include "semantic.h"

typedef struct {
    String* main_code;
    String* function_definitions;
    String* struct_definitions;
    String* includes;
    String* current_output;  // Points to the current target for statement generation
    SymbolTable* symbol_table;
    SemanticAnalyzer* semantic_analyzer;
    int indent_level;
} CodeGenerator;

// Code generator management
CodeGenerator* codegen_new(SymbolTable* symbol_table, SemanticAnalyzer* analyzer);
void codegen_free(CodeGenerator* codegen);

// Main generation function
char* codegen_generate(CodeGenerator* codegen, ASTNode* ast);

// Statement generation
void generate_statement(CodeGenerator* codegen, ASTNode* node);
void generate_function_def(CodeGenerator* codegen, ASTNode* node);
void generate_class_def(CodeGenerator* codegen, ASTNode* node);
void generate_assign(CodeGenerator* codegen, ASTNode* node);
void generate_ann_assign(CodeGenerator* codegen, ASTNode* node);
void generate_if(CodeGenerator* codegen, ASTNode* node);
void generate_while(CodeGenerator* codegen, ASTNode* node);
void generate_for(CodeGenerator* codegen, ASTNode* node);
void generate_return(CodeGenerator* codegen, ASTNode* node);
void generate_expr_stmt(CodeGenerator* codegen, ASTNode* node);

// Expression generation
void generate_expression(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_name(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_constant(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_binop(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_unaryop(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_compare(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_boolop(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_call(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_attribute(CodeGenerator* codegen, ASTNode* node, String* output);
void generate_subscript(CodeGenerator* codegen, ASTNode* node, String* output);

// Utility functions
void generate_indent(CodeGenerator* codegen, String* output);
char* c_type_from_pyrinas_type(const char* pyrinas_type);
void generate_struct_definition(CodeGenerator* codegen, Symbol* struct_symbol);
void generate_enum_definition(CodeGenerator* codegen, Symbol* enum_symbol);

#endif // CODEGEN_H