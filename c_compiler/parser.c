#include "parser.h"

// Parser management
Parser* parser_new(TokenArray* tokens) {
    Parser* parser = malloc(sizeof(Parser));
    if (!parser) return NULL;
    
    parser->tokens = tokens;
    parser->current = 0;
    parser->has_error = false;
    parser->error_message = NULL;
    
    return parser;
}

void parser_free(Parser* parser) {
    if (parser) {
        free(parser->error_message);
        free(parser);
    }
}

// Token utilities
Token* current_token(Parser* parser) {
    if (parser->current >= parser->tokens->count) {
        return NULL;
    }
    return &parser->tokens->items[parser->current];
}

Token* peek_token(Parser* parser) {
    if (parser->current + 1 >= parser->tokens->count) {
        return NULL;
    }
    return &parser->tokens->items[parser->current + 1];
}

bool match_token(Parser* parser, TokenType type) {
    Token* token = current_token(parser);
    return token && token->type == type;
}

bool consume_token(Parser* parser, TokenType type) {
    if (match_token(parser, type)) {
        advance_token(parser);
        return true;
    }
    return false;
}

void advance_token(Parser* parser) {
    if (parser->current < parser->tokens->count) {
        parser->current++;
    }
}

bool at_end(Parser* parser) {
    Token* token = current_token(parser);
    return !token || token->type == TOK_EOF;
}

// Error handling
void parser_error(Parser* parser, const char* message) {
    parser->has_error = true;
    free(parser->error_message);
    parser->error_message = strdup(message);
}

// Skip newlines and comments
static void skip_newlines(Parser* parser) {
    while (match_token(parser, TOK_NEWLINE)) {
        advance_token(parser);
    }
}

// Main parsing function
ASTNode* parser_parse(Parser* parser) {
    NodeArray* body = node_array_new();
    
    skip_newlines(parser);
    
    while (!at_end(parser)) {
        ASTNode* stmt = parse_statement(parser);
        if (stmt) {
            node_array_push(body, stmt);
        }
        
        if (parser->has_error) {
            node_array_free(body);
            return NULL;
        }
        
        skip_newlines(parser);
    }
    
    return ast_module_new(body);
}

// Statement parsing
ASTNode* parse_statement(Parser* parser) {
    skip_newlines(parser);
    
    Token* token = current_token(parser);
    if (!token) return NULL;
    
    switch (token->type) {
        case TOK_DEF:
            return parse_function_def(parser);
        case TOK_CLASS:
            return parse_class_def(parser);
        case TOK_IF:
            return parse_if_statement(parser);
        case TOK_WHILE:
            return parse_while_statement(parser);
        case TOK_FOR:
            return parse_for_statement(parser);
        case TOK_RETURN:
            return parse_return_statement(parser);
        case TOK_BREAK:
            advance_token(parser);
            return ast_break_new(NULL);
        case TOK_CONTINUE:
            advance_token(parser);
            return ast_continue_new(NULL);
        case TOK_PASS:
            advance_token(parser);
            return ast_pass_new();
        case TOK_IDENTIFIER:
            // Could be assignment or expression statement
            return parse_assign_statement(parser);
        default:
            return parse_expression_statement(parser);
    }
}

ASTNode* parse_function_def(Parser* parser) {
    if (!consume_token(parser, TOK_DEF)) {
        parser_error(parser, "Expected 'def'");
        return NULL;
    }
    
    Token* name_token = current_token(parser);
    if (!match_token(parser, TOK_IDENTIFIER)) {
        parser_error(parser, "Expected function name");
        return NULL;
    }
    char* name = strdup(name_token->value);
    advance_token(parser);
    
    if (!consume_token(parser, TOK_LPAREN)) {
        parser_error(parser, "Expected '(' after function name");
        free(name);
        return NULL;
    }
    
    ASTNode* args = parse_arguments(parser);
    
    if (!consume_token(parser, TOK_RPAREN)) {
        parser_error(parser, "Expected ')' after parameters");
        free(name);
        ast_node_free(args);
        return NULL;
    }
    
    ASTNode* returns = NULL;
    if (consume_token(parser, TOK_ARROW)) {
        returns = parse_type_annotation(parser);
    }
    
    if (!consume_token(parser, TOK_COLON)) {
        parser_error(parser, "Expected ':' after function signature");
        free(name);
        ast_node_free(args);
        ast_node_free(returns);
        return NULL;
    }
    
    skip_newlines(parser);
    
    if (!consume_token(parser, TOK_INDENT)) {
        parser_error(parser, "Expected indented block after ':'");
        free(name);
        ast_node_free(args);
        ast_node_free(returns);
        return NULL;
    }
    
    NodeArray* body = parse_statement_list(parser);
    
    if (!consume_token(parser, TOK_DEDENT)) {
        parser_error(parser, "Expected dedent after function body");
        free(name);
        ast_node_free(args);
        ast_node_free(returns);
        node_array_free(body);
        return NULL;
    }
    
    ASTNode* function = ast_function_def_new(name, args, returns, body, NULL);
    free(name);
    return function;
}

ASTNode* parse_class_def(Parser* parser) {
    if (!consume_token(parser, TOK_CLASS)) {
        parser_error(parser, "Expected 'class'");
        return NULL;
    }
    
    Token* name_token = current_token(parser);
    if (!match_token(parser, TOK_IDENTIFIER)) {
        parser_error(parser, "Expected class name");
        return NULL;
    }
    char* name = strdup(name_token->value);
    advance_token(parser);
    
    NodeArray* bases = node_array_new();
    
    // Handle inheritance (optional)
    if (consume_token(parser, TOK_LPAREN)) {
        if (!match_token(parser, TOK_RPAREN)) {
            do {
                ASTNode* base = parse_expression(parser);
                if (base) {
                    node_array_push(bases, base);
                }
            } while (consume_token(parser, TOK_COMMA));
        }
        
        if (!consume_token(parser, TOK_RPAREN)) {
            parser_error(parser, "Expected ')' after base classes");
            free(name);
            node_array_free(bases);
            return NULL;
        }
    }
    
    if (!consume_token(parser, TOK_COLON)) {
        parser_error(parser, "Expected ':' after class name");
        free(name);
        node_array_free(bases);
        return NULL;
    }
    
    skip_newlines(parser);
    
    if (!consume_token(parser, TOK_INDENT)) {
        parser_error(parser, "Expected indented block after ':'");
        free(name);
        node_array_free(bases);
        return NULL;
    }
    
    NodeArray* body = parse_statement_list(parser);
    
    if (!consume_token(parser, TOK_DEDENT)) {
        parser_error(parser, "Expected dedent after class body");
        free(name);
        node_array_free(bases);
        node_array_free(body);
        return NULL;
    }
    
    ASTNode* class_def = ast_class_def_new(name, bases, body);
    free(name);
    return class_def;
}

ASTNode* parse_if_statement(Parser* parser) {
    if (!consume_token(parser, TOK_IF)) {
        parser_error(parser, "Expected 'if'");
        return NULL;
    }
    
    ASTNode* test = parse_expression(parser);
    if (!test) {
        parser_error(parser, "Expected condition after 'if'");
        return NULL;
    }
    
    if (!consume_token(parser, TOK_COLON)) {
        parser_error(parser, "Expected ':' after if condition");
        ast_node_free(test);
        return NULL;
    }
    
    skip_newlines(parser);
    
    if (!consume_token(parser, TOK_INDENT)) {
        parser_error(parser, "Expected indented block after ':'");
        ast_node_free(test);
        return NULL;
    }
    
    NodeArray* body = parse_statement_list(parser);
    
    if (!consume_token(parser, TOK_DEDENT)) {
        parser_error(parser, "Expected dedent after if body");
        ast_node_free(test);
        node_array_free(body);
        return NULL;
    }
    
    NodeArray* orelse = node_array_new();
    
    // Handle else clause
    if (match_token(parser, TOK_ELSE)) {
        advance_token(parser);
        if (!consume_token(parser, TOK_COLON)) {
            parser_error(parser, "Expected ':' after 'else'");
            ast_node_free(test);
            node_array_free(body);
            node_array_free(orelse);
            return NULL;
        }
        
        skip_newlines(parser);
        
        if (!consume_token(parser, TOK_INDENT)) {
            parser_error(parser, "Expected indented block after ':'");
            ast_node_free(test);
            node_array_free(body);
            node_array_free(orelse);
            return NULL;
        }
        
        NodeArray* else_body = parse_statement_list(parser);
        
        if (!consume_token(parser, TOK_DEDENT)) {
            parser_error(parser, "Expected dedent after else body");
            ast_node_free(test);
            node_array_free(body);
            node_array_free(orelse);
            node_array_free(else_body);
            return NULL;
        }
        
        // Move statements from else_body to orelse
        for (size_t i = 0; i < else_body->count; i++) {
            node_array_push(orelse, else_body->items[i]);
        }
        free(else_body->items);
        free(else_body);
    }
    
    return ast_if_new(test, body, orelse);
}

ASTNode* parse_while_statement(Parser* parser) {
    if (!consume_token(parser, TOK_WHILE)) {
        parser_error(parser, "Expected 'while'");
        return NULL;
    }
    
    ASTNode* test = parse_expression(parser);
    if (!test) {
        parser_error(parser, "Expected condition after 'while'");
        return NULL;
    }
    
    if (!consume_token(parser, TOK_COLON)) {
        parser_error(parser, "Expected ':' after while condition");
        ast_node_free(test);
        return NULL;
    }
    
    skip_newlines(parser);
    
    if (!consume_token(parser, TOK_INDENT)) {
        parser_error(parser, "Expected indented block after ':'");
        ast_node_free(test);
        return NULL;
    }
    
    NodeArray* body = parse_statement_list(parser);
    
    if (!consume_token(parser, TOK_DEDENT)) {
        parser_error(parser, "Expected dedent after while body");
        ast_node_free(test);
        node_array_free(body);
        return NULL;
    }
    
    return ast_while_new(test, body);
}

ASTNode* parse_for_statement(Parser* parser) {
    if (!consume_token(parser, TOK_FOR)) {
        parser_error(parser, "Expected 'for'");
        return NULL;
    }
    
    ASTNode* target = parse_expression(parser);
    if (!target) {
        parser_error(parser, "Expected variable after 'for'");
        return NULL;
    }
    
    if (!consume_token(parser, TOK_IN)) {
        parser_error(parser, "Expected 'in' after for variable");
        ast_node_free(target);
        return NULL;
    }
    
    ASTNode* iter = parse_expression(parser);
    if (!iter) {
        parser_error(parser, "Expected iterable after 'in'");
        ast_node_free(target);
        return NULL;
    }
    
    if (!consume_token(parser, TOK_COLON)) {
        parser_error(parser, "Expected ':' after for clause");
        ast_node_free(target);
        ast_node_free(iter);
        return NULL;
    }
    
    skip_newlines(parser);
    
    if (!consume_token(parser, TOK_INDENT)) {
        parser_error(parser, "Expected indented block after ':'");
        ast_node_free(target);
        ast_node_free(iter);
        return NULL;
    }
    
    NodeArray* body = parse_statement_list(parser);
    
    if (!consume_token(parser, TOK_DEDENT)) {
        parser_error(parser, "Expected dedent after for body");
        ast_node_free(target);
        ast_node_free(iter);
        node_array_free(body);
        return NULL;
    }
    
    return ast_for_new(target, iter, body);
}

ASTNode* parse_return_statement(Parser* parser) {
    if (!consume_token(parser, TOK_RETURN)) {
        parser_error(parser, "Expected 'return'");
        return NULL;
    }
    
    ASTNode* value = NULL;
    if (!match_token(parser, TOK_NEWLINE) && !at_end(parser)) {
        value = parse_expression(parser);
    }
    
    return ast_return_new(value);
}

ASTNode* parse_assign_statement(Parser* parser) {
    // Save current position in case this is not an assignment
    size_t saved_pos = parser->current;
    
    ASTNode* target = parse_expression(parser);
    if (!target) {
        return NULL;
    }
    
    // Check for type annotation
    if (match_token(parser, TOK_COLON)) {
        advance_token(parser);
        ASTNode* annotation = parse_type_annotation(parser);
        
        ASTNode* value = NULL;
        if (consume_token(parser, TOK_ASSIGN)) {
            value = parse_expression(parser);
        }
        
        return ast_ann_assign_new(target, annotation, value);
    }
    
    // Check for regular assignment
    if (match_token(parser, TOK_ASSIGN)) {
        advance_token(parser);
        ASTNode* value = parse_expression(parser);
        
        NodeArray* targets = node_array_new();
        node_array_push(targets, target);
        
        return ast_assign_new(targets, value);
    }
    
    // Not an assignment, treat as expression statement
    return ast_expr_stmt_new(target);
}

ASTNode* parse_expression_statement(Parser* parser) {
    ASTNode* expr = parse_expression(parser);
    if (!expr) {
        return NULL;
    }
    return ast_expr_stmt_new(expr);
}

// Expression parsing (operator precedence climbing)
ASTNode* parse_expression(Parser* parser) {
    return parse_or_expression(parser);
}

ASTNode* parse_or_expression(Parser* parser) {
    ASTNode* left = parse_and_expression(parser);
    
    while (match_token(parser, TOK_OR)) {
        advance_token(parser);
        ASTNode* right = parse_and_expression(parser);
        
        NodeArray* values = node_array_new();
        node_array_push(values, left);
        node_array_push(values, right);
        
        left = ast_boolop_new(BOOLOP_OR, values);
    }
    
    return left;
}

ASTNode* parse_and_expression(Parser* parser) {
    ASTNode* left = parse_not_expression(parser);
    
    while (match_token(parser, TOK_AND)) {
        advance_token(parser);
        ASTNode* right = parse_not_expression(parser);
        
        NodeArray* values = node_array_new();
        node_array_push(values, left);
        node_array_push(values, right);
        
        left = ast_boolop_new(BOOLOP_AND, values);
    }
    
    return left;
}

ASTNode* parse_not_expression(Parser* parser) {
    if (match_token(parser, TOK_NOT)) {
        advance_token(parser);
        ASTNode* operand = parse_not_expression(parser);
        return ast_unaryop_new(UNARYOP_NOT, operand);
    }
    
    return parse_comparison(parser);
}

ASTNode* parse_comparison(Parser* parser) {
    ASTNode* left = parse_arithmetic_expression(parser);
    
    if (match_token(parser, TOK_EQ) || match_token(parser, TOK_NE) ||
        match_token(parser, TOK_LT) || match_token(parser, TOK_LE) ||
        match_token(parser, TOK_GT) || match_token(parser, TOK_GE)) {
        
        CompareOpType op;
        Token* op_token = current_token(parser);
        advance_token(parser);
        
        switch (op_token->type) {
            case TOK_EQ: op = CMP_EQ; break;
            case TOK_NE: op = CMP_NOTEQ; break;
            case TOK_LT: op = CMP_LT; break;
            case TOK_LE: op = CMP_LTE; break;
            case TOK_GT: op = CMP_GT; break;
            case TOK_GE: op = CMP_GTE; break;
            default: op = CMP_EQ; break;
        }
        
        ASTNode* right = parse_arithmetic_expression(parser);
        
        CompareOpType* ops = malloc(sizeof(CompareOpType));
        ops[0] = op;
        
        NodeArray* comparators = node_array_new();
        node_array_push(comparators, right);
        
        return ast_compare_new(left, ops, comparators, 1);
    }
    
    return left;
}

ASTNode* parse_arithmetic_expression(Parser* parser) {
    ASTNode* left = parse_term(parser);
    
    while (match_token(parser, TOK_PLUS) || match_token(parser, TOK_MINUS)) {
        BinOpType op = match_token(parser, TOK_PLUS) ? BINOP_ADD : BINOP_SUB;
        advance_token(parser);
        ASTNode* right = parse_term(parser);
        left = ast_binop_new(left, op, right);
    }
    
    return left;
}

ASTNode* parse_term(Parser* parser) {
    ASTNode* left = parse_factor(parser);
    
    while (match_token(parser, TOK_MULTIPLY) || match_token(parser, TOK_DIVIDE) ||
           match_token(parser, TOK_MODULO) || match_token(parser, TOK_FLOORDIV)) {
        
        BinOpType op;
        Token* op_token = current_token(parser);
        advance_token(parser);
        
        switch (op_token->type) {
            case TOK_MULTIPLY: op = BINOP_MULT; break;
            case TOK_DIVIDE: op = BINOP_DIV; break;
            case TOK_MODULO: op = BINOP_MOD; break;
            case TOK_FLOORDIV: op = BINOP_FLOORDIV; break;
            default: op = BINOP_MULT; break;
        }
        
        ASTNode* right = parse_factor(parser);
        left = ast_binop_new(left, op, right);
    }
    
    return left;
}

ASTNode* parse_factor(Parser* parser) {
    if (match_token(parser, TOK_MINUS)) {
        advance_token(parser);
        ASTNode* operand = parse_factor(parser);
        return ast_unaryop_new(UNARYOP_USUB, operand);
    }
    
    if (match_token(parser, TOK_PLUS)) {
        advance_token(parser);
        ASTNode* operand = parse_factor(parser);
        return ast_unaryop_new(UNARYOP_UADD, operand);
    }
    
    return parse_primary(parser);
}

ASTNode* parse_primary(Parser* parser) {
    Token* token = current_token(parser);
    if (!token) return NULL;
    
    ASTNode* node = NULL;
    
    switch (token->type) {
        case TOK_NUMBER: {
            // Determine if it's int or float
            if (strchr(token->value, '.')) {
                double value = atof(token->value);
                node = ast_constant_float_new(value);
            } else {
                int value = atoi(token->value);
                node = ast_constant_int_new(value);
            }
            advance_token(parser);
            break;
        }
        
        case TOK_STRING:
            node = ast_constant_string_new(token->value);
            advance_token(parser);
            break;
            
        case TOK_TRUE:
            node = ast_constant_bool_new(true);
            advance_token(parser);
            break;
            
        case TOK_FALSE:
            node = ast_constant_bool_new(false);
            advance_token(parser);
            break;
            
        case TOK_NONE:
            node = ast_constant_none_new();
            advance_token(parser);
            break;
            
        case TOK_IDENTIFIER:
            node = ast_name_new(token->value, CTX_LOAD);
            advance_token(parser);
            break;
            
        case TOK_LPAREN:
            advance_token(parser);
            node = parse_expression(parser);
            if (!consume_token(parser, TOK_RPAREN)) {
                parser_error(parser, "Expected ')' after expression");
                ast_node_free(node);
                return NULL;
            }
            break;
            
        default:
            parser_error(parser, "Unexpected token in expression");
            return NULL;
    }
    
    // Handle postfix operators (calls, attributes, subscripts)
    while (node && (match_token(parser, TOK_LPAREN) || 
                    match_token(parser, TOK_DOT) || 
                    match_token(parser, TOK_LBRACKET))) {
        
        if (match_token(parser, TOK_LPAREN)) {
            node = parse_call(parser, node);
        } else if (match_token(parser, TOK_DOT)) {
            node = parse_attribute(parser, node);
        } else if (match_token(parser, TOK_LBRACKET)) {
            node = parse_subscript(parser, node);
        }
    }
    
    return node;
}

ASTNode* parse_call(Parser* parser, ASTNode* func) {
    if (!consume_token(parser, TOK_LPAREN)) {
        return func;
    }
    
    NodeArray* args = node_array_new();
    
    if (!match_token(parser, TOK_RPAREN)) {
        do {
            ASTNode* arg = parse_expression(parser);
            if (arg) {
                node_array_push(args, arg);
            }
        } while (consume_token(parser, TOK_COMMA));
    }
    
    if (!consume_token(parser, TOK_RPAREN)) {
        parser_error(parser, "Expected ')' after arguments");
        node_array_free(args);
        return func;
    }
    
    return ast_call_new(func, args);
}

ASTNode* parse_attribute(Parser* parser, ASTNode* value) {
    if (!consume_token(parser, TOK_DOT)) {
        return value;
    }
    
    Token* attr_token = current_token(parser);
    if (!match_token(parser, TOK_IDENTIFIER)) {
        parser_error(parser, "Expected attribute name after '.'");
        return value;
    }
    
    char* attr = strdup(attr_token->value);
    advance_token(parser);
    
    ASTNode* result = ast_attribute_new(value, attr, CTX_LOAD);
    free(attr);
    return result;
}

ASTNode* parse_subscript(Parser* parser, ASTNode* value) {
    if (!consume_token(parser, TOK_LBRACKET)) {
        return value;
    }
    
    ASTNode* slice = parse_expression(parser);
    if (!slice) {
        parser_error(parser, "Expected expression after '['");
        return value;
    }
    
    if (!consume_token(parser, TOK_RBRACKET)) {
        parser_error(parser, "Expected ']' after subscript");
        ast_node_free(slice);
        return value;
    }
    
    return ast_subscript_new(value, slice, CTX_LOAD);
}

// Utility functions
ASTNode* parse_arguments(Parser* parser) {
    NodeArray* args = node_array_new();
    
    if (!match_token(parser, TOK_RPAREN)) {
        do {
            Token* name_token = current_token(parser);
            if (!match_token(parser, TOK_IDENTIFIER)) {
                parser_error(parser, "Expected parameter name");
                node_array_free(args);
                return NULL;
            }
            
            char* arg_name = strdup(name_token->value);
            advance_token(parser);
            
            ASTNode* annotation = NULL;
            if (consume_token(parser, TOK_COLON)) {
                annotation = parse_type_annotation(parser);
            }
            
            ASTNode* arg = ast_arg_new(arg_name, annotation);
            node_array_push(args, arg);
            free(arg_name);
            
        } while (consume_token(parser, TOK_COMMA));
    }
    
    return ast_arguments_new(args);
}

NodeArray* parse_parameter_list(Parser* parser) {
    NodeArray* params = node_array_new();
    
    if (!match_token(parser, TOK_RPAREN)) {
        do {
            ASTNode* param = parse_expression(parser);
            if (param) {
                node_array_push(params, param);
            }
        } while (consume_token(parser, TOK_COMMA));
    }
    
    return params;
}

NodeArray* parse_statement_list(Parser* parser) {
    NodeArray* statements = node_array_new();
    
    while (!match_token(parser, TOK_DEDENT) && !at_end(parser)) {
        ASTNode* stmt = parse_statement(parser);
        if (stmt) {
            node_array_push(statements, stmt);
        }
        
        if (parser->has_error) {
            break;
        }
        
        skip_newlines(parser);
    }
    
    return statements;
}

ASTNode* parse_type_annotation(Parser* parser) {
    Token* token = current_token(parser);
    if (!token) return NULL;
    
    if (match_token(parser, TOK_IDENTIFIER)) {
        ASTNode* name = ast_name_new(token->value, CTX_LOAD);
        advance_token(parser);
        
        // Check for subscript-style types like array[int, 5]
        if (match_token(parser, TOK_LBRACKET)) {
            advance_token(parser); // consume '['
            
            // Parse the slice - for array[int, 5], we need to handle the comma
            // For now, let's create a simple comma-separated list
            ASTNode* slice = NULL;
            Token* token = current_token(parser);
            if (token && token->type == TOK_IDENTIFIER) {
                // First element (type name)
                slice = ast_name_new(token->value, CTX_LOAD);
                advance_token(parser);
                
                // Check for comma and second element (size)
                if (match_token(parser, TOK_COMMA)) {
                    advance_token(parser); // consume comma
                    token = current_token(parser);
                    if (token && token->type == TOK_NUMBER) {
                        // For now, just ignore the size - we have the type
                        advance_token(parser);
                    }
                }
            } else {
                // Fallback to expression parsing
                slice = parse_expression(parser);
            }
            
            if (!slice) {
                ast_node_free(name);
                return NULL;
            }
            
            if (!match_token(parser, TOK_RBRACKET)) {
                ast_node_free(name);
                ast_node_free(slice);
                return NULL;
            }
            advance_token(parser); // consume ']'
            
            // Create subscript node  
            ASTNode* subscript = ast_subscript_new(name, slice, CTX_LOAD);
            if (!subscript) {
                ast_node_free(name);
                ast_node_free(slice);
                return NULL;
            }
            
            return subscript;
        }
        
        return name;
    } else if (match_token(parser, TOK_STRING)) {
        ASTNode* str = ast_constant_string_new(token->value);
        advance_token(parser);
        return str;
    }
    
    return NULL;
}