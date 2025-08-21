#ifndef LEXER_H
#define LEXER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

// Token types
typedef enum {
    // Literals
    TOK_NUMBER,
    TOK_STRING,
    TOK_IDENTIFIER,
    
    // Keywords
    TOK_DEF,
    TOK_CLASS,
    TOK_IF,
    TOK_ELSE,
    TOK_ELIF,
    TOK_WHILE,
    TOK_FOR,
    TOK_BREAK,
    TOK_CONTINUE,
    TOK_RETURN,
    TOK_PASS,
    TOK_MATCH,
    TOK_CASE,
    TOK_IN,
    TOK_AND,
    TOK_OR,
    TOK_NOT,
    TOK_TRUE,
    TOK_FALSE,
    TOK_NONE,
    TOK_IMPORT,
    TOK_FROM,
    TOK_AS,
    
    // Operators
    TOK_PLUS,           // +
    TOK_MINUS,          // -
    TOK_MULTIPLY,       // *
    TOK_DIVIDE,         // /
    TOK_MODULO,         // %
    TOK_FLOORDIV,       // //
    TOK_ASSIGN,         // =
    TOK_EQ,             // ==
    TOK_NE,             // !=
    TOK_LT,             // <
    TOK_LE,             // <=
    TOK_GT,             // >
    TOK_GE,             // >=
    TOK_ARROW,          // ->
    
    // Delimiters
    TOK_LPAREN,         // (
    TOK_RPAREN,         // )
    TOK_LBRACKET,       // [
    TOK_RBRACKET,       // ]
    TOK_LBRACE,         // {
    TOK_RBRACE,         // }
    TOK_COMMA,          // ,
    TOK_COLON,          // :
    TOK_SEMICOLON,      // ;
    TOK_DOT,            // .
    
    // Special
    TOK_NEWLINE,
    TOK_INDENT,
    TOK_DEDENT,
    TOK_EOF,
    TOK_ERROR
} TokenType;

typedef struct {
    TokenType type;
    char* value;
    int line;
    int column;
} Token;

typedef struct {
    Token* items;
    size_t count;
    size_t capacity;
    size_t current;  // Current position for parsing
} TokenArray;

typedef struct {
    const char* source;
    size_t position;
    size_t length;
    int line;
    int column;
    int* indent_stack;
    size_t indent_count;
    size_t indent_capacity;
    bool at_line_start;
    TokenArray* tokens;
} Lexer;

// Token management
Token token_new(TokenType type, const char* value, int line, int column);
void token_free(Token* token);
const char* token_type_name(TokenType type);

// Token array management
TokenArray* token_array_new(void);
void token_array_push(TokenArray* arr, Token token);
void token_array_free(TokenArray* arr);

// Lexer functions
Lexer* lexer_new(const char* source);
void lexer_free(Lexer* lexer);
TokenArray* lexer_tokenize(Lexer* lexer);

// Helper functions
bool is_keyword(const char* str);
TokenType keyword_token_type(const char* str);
bool is_identifier_start(char c);
bool is_identifier_char(char c);

#endif // LEXER_H