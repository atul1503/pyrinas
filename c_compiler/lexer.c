#include "lexer.h"

// Keywords table
static const struct {
    const char* keyword;
    TokenType type;
} keywords[] = {
    {"def", TOK_DEF},
    {"class", TOK_CLASS},
    {"if", TOK_IF},
    {"else", TOK_ELSE},
    {"elif", TOK_ELIF},
    {"while", TOK_WHILE},
    {"for", TOK_FOR},
    {"break", TOK_BREAK},
    {"continue", TOK_CONTINUE},
    {"return", TOK_RETURN},
    {"pass", TOK_PASS},
    {"match", TOK_MATCH},
    {"case", TOK_CASE},
    {"in", TOK_IN},
    {"and", TOK_AND},
    {"or", TOK_OR},
    {"not", TOK_NOT},
    {"True", TOK_TRUE},
    {"False", TOK_FALSE},
    {"None", TOK_NONE},
    {"import", TOK_IMPORT},
    {"from", TOK_FROM},
    {"as", TOK_AS},
    {NULL, 0}
};

// Token management
Token token_new(TokenType type, const char* value, int line, int column) {
    Token token;
    token.type = type;
    token.value = value ? strdup(value) : NULL;
    token.line = line;
    token.column = column;
    return token;
}

void token_free(Token* token) {
    if (token && token->value) {
        free(token->value);
        token->value = NULL;
    }
}

const char* token_type_name(TokenType type) {
    switch (type) {
        case TOK_NUMBER: return "NUMBER";
        case TOK_STRING: return "STRING";
        case TOK_IDENTIFIER: return "IDENTIFIER";
        case TOK_DEF: return "DEF";
        case TOK_CLASS: return "CLASS";
        case TOK_IF: return "IF";
        case TOK_ELSE: return "ELSE";
        case TOK_ELIF: return "ELIF";
        case TOK_WHILE: return "WHILE";
        case TOK_FOR: return "FOR";
        case TOK_BREAK: return "BREAK";
        case TOK_CONTINUE: return "CONTINUE";
        case TOK_RETURN: return "RETURN";
        case TOK_PASS: return "PASS";
        case TOK_MATCH: return "MATCH";
        case TOK_CASE: return "CASE";
        case TOK_IN: return "IN";
        case TOK_AND: return "AND";
        case TOK_OR: return "OR";
        case TOK_NOT: return "NOT";
        case TOK_TRUE: return "TRUE";
        case TOK_FALSE: return "FALSE";
        case TOK_NONE: return "NONE";
        case TOK_IMPORT: return "IMPORT";
        case TOK_FROM: return "FROM";
        case TOK_AS: return "AS";
        case TOK_PLUS: return "PLUS";
        case TOK_MINUS: return "MINUS";
        case TOK_MULTIPLY: return "MULTIPLY";
        case TOK_DIVIDE: return "DIVIDE";
        case TOK_MODULO: return "MODULO";
        case TOK_FLOORDIV: return "FLOORDIV";
        case TOK_ASSIGN: return "ASSIGN";
        case TOK_EQ: return "EQ";
        case TOK_NE: return "NE";
        case TOK_LT: return "LT";
        case TOK_LE: return "LE";
        case TOK_GT: return "GT";
        case TOK_GE: return "GE";
        case TOK_ARROW: return "ARROW";
        case TOK_LPAREN: return "LPAREN";
        case TOK_RPAREN: return "RPAREN";
        case TOK_LBRACKET: return "LBRACKET";
        case TOK_RBRACKET: return "RBRACKET";
        case TOK_LBRACE: return "LBRACE";
        case TOK_RBRACE: return "RBRACE";
        case TOK_COMMA: return "COMMA";
        case TOK_COLON: return "COLON";
        case TOK_SEMICOLON: return "SEMICOLON";
        case TOK_DOT: return "DOT";
        case TOK_NEWLINE: return "NEWLINE";
        case TOK_INDENT: return "INDENT";
        case TOK_DEDENT: return "DEDENT";
        case TOK_EOF: return "EOF";
        case TOK_ERROR: return "ERROR";
        default: return "UNKNOWN";
    }
}

// Token array management
TokenArray* token_array_new(void) {
    TokenArray* arr = malloc(sizeof(TokenArray));
    if (!arr) return NULL;
    
    arr->capacity = 64;
    arr->items = malloc(sizeof(Token) * arr->capacity);
    if (!arr->items) {
        free(arr);
        return NULL;
    }
    arr->count = 0;
    arr->current = 0;
    return arr;
}

void token_array_push(TokenArray* arr, Token token) {
    if (!arr) return;
    
    if (arr->count >= arr->capacity) {
        size_t new_capacity = arr->capacity * 2;
        Token* new_items = realloc(arr->items, sizeof(Token) * new_capacity);
        if (!new_items) return;
        arr->items = new_items;
        arr->capacity = new_capacity;
    }
    
    arr->items[arr->count++] = token;
}

void token_array_free(TokenArray* arr) {
    if (arr) {
        if (arr->items) {
            for (size_t i = 0; i < arr->count; i++) {
                token_free(&arr->items[i]);
            }
            free(arr->items);
        }
        free(arr);
    }
}

// Lexer functions
Lexer* lexer_new(const char* source) {
    Lexer* lexer = malloc(sizeof(Lexer));
    if (!lexer) return NULL;
    
    lexer->source = source;
    lexer->position = 0;
    lexer->length = strlen(source);
    lexer->line = 1;
    lexer->column = 1;
    lexer->at_line_start = true;
    
    // Initialize indent stack
    lexer->indent_capacity = 16;
    lexer->indent_stack = malloc(sizeof(int) * lexer->indent_capacity);
    if (!lexer->indent_stack) {
        free(lexer);
        return NULL;
    }
    lexer->indent_stack[0] = 0;  // Base indentation
    lexer->indent_count = 1;
    
    lexer->tokens = token_array_new();
    if (!lexer->tokens) {
        free(lexer->indent_stack);
        free(lexer);
        return NULL;
    }
    
    return lexer;
}

void lexer_free(Lexer* lexer) {
    if (lexer) {
        free(lexer->indent_stack);
        token_array_free(lexer->tokens);
        free(lexer);
    }
}

// Helper functions
bool is_keyword(const char* str) {
    for (int i = 0; keywords[i].keyword; i++) {
        if (strcmp(str, keywords[i].keyword) == 0) {
            return true;
        }
    }
    return false;
}

TokenType keyword_token_type(const char* str) {
    for (int i = 0; keywords[i].keyword; i++) {
        if (strcmp(str, keywords[i].keyword) == 0) {
            return keywords[i].type;
        }
    }
    return TOK_IDENTIFIER;
}

bool is_identifier_start(char c) {
    return isalpha(c) || c == '_';
}

bool is_identifier_char(char c) {
    return isalnum(c) || c == '_';
}

// Lexer helper functions
static char lexer_current_char(Lexer* lexer) {
    if (lexer->position >= lexer->length) {
        return '\0';
    }
    return lexer->source[lexer->position];
}

static char lexer_peek_char(Lexer* lexer) {
    if (lexer->position + 1 >= lexer->length) {
        return '\0';
    }
    return lexer->source[lexer->position + 1];
}

static void lexer_advance(Lexer* lexer) {
    if (lexer->position < lexer->length) {
        if (lexer->source[lexer->position] == '\n') {
            lexer->line++;
            lexer->column = 1;
            lexer->at_line_start = true;
        } else {
            lexer->column++;
            lexer->at_line_start = false;
        }
        lexer->position++;
    }
}

static void lexer_skip_whitespace(Lexer* lexer) {
    while (lexer_current_char(lexer) == ' ' || lexer_current_char(lexer) == '\t') {
        lexer_advance(lexer);
        lexer->at_line_start = false;
    }
}

static void lexer_skip_comment(Lexer* lexer) {
    if (lexer_current_char(lexer) == '#') {
        while (lexer_current_char(lexer) != '\n' && lexer_current_char(lexer) != '\0') {
            lexer_advance(lexer);
        }
    }
}

static void lexer_handle_indentation(Lexer* lexer) {
    if (!lexer->at_line_start) return;
    
    int indent_level = 0;
    while (lexer_current_char(lexer) == ' ' || lexer_current_char(lexer) == '\t') {
        if (lexer_current_char(lexer) == ' ') {
            indent_level++;
        } else {  // tab
            indent_level += 8;  // Treat tab as 8 spaces
        }
        lexer_advance(lexer);
    }
    
    // Skip empty lines and comments - but don't return early, we need to process indentation
    if (lexer_current_char(lexer) == '\n' || lexer_current_char(lexer) == '#') {
        lexer->at_line_start = false;  // Mark that we've processed this line start
        return;
    }
    
    lexer->at_line_start = false;
    
    int current_indent = lexer->indent_stack[lexer->indent_count - 1];
    
    if (indent_level > current_indent) {
        // Increase indentation
        if (lexer->indent_count >= lexer->indent_capacity) {
            lexer->indent_capacity *= 2;
            lexer->indent_stack = realloc(lexer->indent_stack, sizeof(int) * lexer->indent_capacity);
        }
        lexer->indent_stack[lexer->indent_count++] = indent_level;
        Token token = token_new(TOK_INDENT, NULL, lexer->line, lexer->column);
        token_array_push(lexer->tokens, token);
    } else if (indent_level < current_indent) {
        // Decrease indentation - may need multiple DEDENTs
        while (lexer->indent_count > 1 && lexer->indent_stack[lexer->indent_count - 1] > indent_level) {
            lexer->indent_count--;
            Token token = token_new(TOK_DEDENT, NULL, lexer->line, lexer->column);
            token_array_push(lexer->tokens, token);
        }
        
        // Check for indentation error
        if (lexer->indent_stack[lexer->indent_count - 1] != indent_level) {
            Token token = token_new(TOK_ERROR, "IndentationError", lexer->line, lexer->column);
            token_array_push(lexer->tokens, token);
        }
    }
}

static Token lexer_read_number(Lexer* lexer) {
    size_t start = lexer->position;
    int line = lexer->line;
    int column = lexer->column;
    
    bool has_dot = false;
    
    while (isdigit(lexer_current_char(lexer)) || 
           (lexer_current_char(lexer) == '.' && !has_dot)) {
        if (lexer_current_char(lexer) == '.') {
            has_dot = true;
        }
        lexer_advance(lexer);
    }
    
    size_t length = lexer->position - start;
    char* value = malloc(length + 1);
    strncpy(value, lexer->source + start, length);
    value[length] = '\0';
    
    Token token = token_new(TOK_NUMBER, value, line, column);
    free(value);
    return token;
}

static Token lexer_read_string(Lexer* lexer) {
    int line = lexer->line;
    int column = lexer->column;
    char quote_char = lexer_current_char(lexer);
    
    lexer_advance(lexer);  // Skip opening quote
    
    char* value = malloc(256);  // Initial buffer
    size_t capacity = 256;
    size_t length = 0;
    
    while (lexer_current_char(lexer) != quote_char && lexer_current_char(lexer) != '\0') {
        if (length >= capacity - 1) {
            capacity *= 2;
            value = realloc(value, capacity);
        }
        
        if (lexer_current_char(lexer) == '\\' && lexer_peek_char(lexer) != '\0') {
            lexer_advance(lexer);  // Skip backslash
            char escape = lexer_current_char(lexer);
            switch (escape) {
                case 'n': value[length++] = '\n'; break;
                case 't': value[length++] = '\t'; break;
                case 'r': value[length++] = '\r'; break;
                case '\\': value[length++] = '\\'; break;
                case '"': value[length++] = '"'; break;
                case '\'': value[length++] = '\''; break;
                default: 
                    value[length++] = '\\';
                    value[length++] = escape;
                    break;
            }
        } else {
            value[length++] = lexer_current_char(lexer);
        }
        lexer_advance(lexer);
    }
    
    if (lexer_current_char(lexer) == quote_char) {
        lexer_advance(lexer);  // Skip closing quote
    }
    
    value[length] = '\0';
    Token token = token_new(TOK_STRING, value, line, column);
    free(value);
    return token;
}

static Token lexer_read_identifier(Lexer* lexer) {
    size_t start = lexer->position;
    int line = lexer->line;
    int column = lexer->column;
    
    while (is_identifier_char(lexer_current_char(lexer))) {
        lexer_advance(lexer);
    }
    
    size_t length = lexer->position - start;
    char* value = malloc(length + 1);
    strncpy(value, lexer->source + start, length);
    value[length] = '\0';
    
    TokenType type = is_keyword(value) ? keyword_token_type(value) : TOK_IDENTIFIER;
    Token token = token_new(type, value, line, column);
    free(value);
    return token;
}

TokenArray* lexer_tokenize(Lexer* lexer) {
    while (lexer->position < lexer->length) {
        // Handle indentation at the start of lines
        if (lexer->at_line_start) {
            lexer_handle_indentation(lexer);
            continue;
        }
        
        // Skip whitespace (but not at line start for indentation)
        lexer_skip_whitespace(lexer);
        
        // Skip comments
        if (lexer_current_char(lexer) == '#') {
            lexer_skip_comment(lexer);
            continue;
        }
        
        char current = lexer_current_char(lexer);
        
        if (current == '\0') {
            break;
        }
        
        Token token;
        int line = lexer->line;
        int column = lexer->column;
        
        // Handle newlines
        if (current == '\n') {
            token = token_new(TOK_NEWLINE, NULL, line, column);
            lexer_advance(lexer);
            token_array_push(lexer->tokens, token);
            continue;
        }
        
        // Handle numbers
        if (isdigit(current)) {
            token = lexer_read_number(lexer);
            token_array_push(lexer->tokens, token);
            continue;
        }
        
        // Handle strings
        if (current == '"' || current == '\'') {
            token = lexer_read_string(lexer);
            token_array_push(lexer->tokens, token);
            continue;
        }
        
        // Handle identifiers and keywords
        if (is_identifier_start(current)) {
            token = lexer_read_identifier(lexer);
            token_array_push(lexer->tokens, token);
            continue;
        }
        
        // Handle operators and delimiters
        switch (current) {
            case '+':
                token = token_new(TOK_PLUS, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '-':
                if (lexer_peek_char(lexer) == '>') {
                    token = token_new(TOK_ARROW, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_MINUS, NULL, line, column);
                    lexer_advance(lexer);
                }
                break;
            case '*':
                token = token_new(TOK_MULTIPLY, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '/':
                if (lexer_peek_char(lexer) == '/') {
                    token = token_new(TOK_FLOORDIV, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_DIVIDE, NULL, line, column);
                    lexer_advance(lexer);
                }
                break;
            case '%':
                token = token_new(TOK_MODULO, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '=':
                if (lexer_peek_char(lexer) == '=') {
                    token = token_new(TOK_EQ, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_ASSIGN, NULL, line, column);
                    lexer_advance(lexer);
                }
                break;
            case '!':
                if (lexer_peek_char(lexer) == '=') {
                    token = token_new(TOK_NE, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_ERROR, "Unexpected character", line, column);
                    lexer_advance(lexer);
                }
                break;
            case '<':
                if (lexer_peek_char(lexer) == '=') {
                    token = token_new(TOK_LE, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_LT, NULL, line, column);
                    lexer_advance(lexer);
                }
                break;
            case '>':
                if (lexer_peek_char(lexer) == '=') {
                    token = token_new(TOK_GE, NULL, line, column);
                    lexer_advance(lexer);
                    lexer_advance(lexer);
                } else {
                    token = token_new(TOK_GT, NULL, line, column);
                    lexer_advance(lexer);
                }
                break;
            case '(':
                token = token_new(TOK_LPAREN, NULL, line, column);
                lexer_advance(lexer);
                break;
            case ')':
                token = token_new(TOK_RPAREN, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '[':
                token = token_new(TOK_LBRACKET, NULL, line, column);
                lexer_advance(lexer);
                break;
            case ']':
                token = token_new(TOK_RBRACKET, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '{':
                token = token_new(TOK_LBRACE, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '}':
                token = token_new(TOK_RBRACE, NULL, line, column);
                lexer_advance(lexer);
                break;
            case ',':
                token = token_new(TOK_COMMA, NULL, line, column);
                lexer_advance(lexer);
                break;
            case ':':
                token = token_new(TOK_COLON, NULL, line, column);
                lexer_advance(lexer);
                break;
            case ';':
                token = token_new(TOK_SEMICOLON, NULL, line, column);
                lexer_advance(lexer);
                break;
            case '.':
                token = token_new(TOK_DOT, NULL, line, column);
                lexer_advance(lexer);
                break;
            default:
                token = token_new(TOK_ERROR, "Unexpected character", line, column);
                lexer_advance(lexer);
                break;
        }
        
        token_array_push(lexer->tokens, token);
    }
    
    // Add final DEDENTs if needed
    while (lexer->indent_count > 1) {
        lexer->indent_count--;
        Token token = token_new(TOK_DEDENT, NULL, lexer->line, lexer->column);
        token_array_push(lexer->tokens, token);
    }
    
    // Add EOF token
    Token eof_token = token_new(TOK_EOF, NULL, lexer->line, lexer->column);
    token_array_push(lexer->tokens, eof_token);
    
    return lexer->tokens;
}