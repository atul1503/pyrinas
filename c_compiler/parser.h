#ifndef PARSER_H
#define PARSER_H

#include "ast.h"
#include "lexer.h"

typedef struct {
    TokenArray* tokens;
    size_t current;
    bool has_error;
    char* error_message;
} Parser;

// Parser management
Parser* parser_new(TokenArray* tokens);
void parser_free(Parser* parser);

// Main parsing function
ASTNode* parser_parse(Parser* parser);

// Statement parsing
ASTNode* parse_statement(Parser* parser);
ASTNode* parse_function_def(Parser* parser);
ASTNode* parse_class_def(Parser* parser);
ASTNode* parse_if_statement(Parser* parser);
ASTNode* parse_while_statement(Parser* parser);
ASTNode* parse_for_statement(Parser* parser);
ASTNode* parse_return_statement(Parser* parser);
ASTNode* parse_assign_statement(Parser* parser);
ASTNode* parse_expression_statement(Parser* parser);

// Expression parsing
ASTNode* parse_expression(Parser* parser);
ASTNode* parse_or_expression(Parser* parser);
ASTNode* parse_and_expression(Parser* parser);
ASTNode* parse_not_expression(Parser* parser);
ASTNode* parse_comparison(Parser* parser);
ASTNode* parse_arithmetic_expression(Parser* parser);
ASTNode* parse_term(Parser* parser);
ASTNode* parse_factor(Parser* parser);
ASTNode* parse_primary(Parser* parser);
ASTNode* parse_call(Parser* parser, ASTNode* primary);
ASTNode* parse_attribute(Parser* parser, ASTNode* primary);
ASTNode* parse_subscript(Parser* parser, ASTNode* primary);

// Utility functions
ASTNode* parse_arguments(Parser* parser);
NodeArray* parse_parameter_list(Parser* parser);
NodeArray* parse_statement_list(Parser* parser);
ASTNode* parse_type_annotation(Parser* parser);

// Token utilities
Token* current_token(Parser* parser);
Token* peek_token(Parser* parser);
bool match_token(Parser* parser, TokenType type);
bool consume_token(Parser* parser, TokenType type);
void advance_token(Parser* parser);
bool at_end(Parser* parser);

// Error handling
void parser_error(Parser* parser, const char* message);

#endif // PARSER_H