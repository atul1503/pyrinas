#include "codegen.h"
#include <stdio.h>

// Code generator management
CodeGenerator* codegen_new(SymbolTable* symbol_table, SemanticAnalyzer* analyzer) {
    CodeGenerator* codegen = malloc(sizeof(CodeGenerator));
    if (!codegen) return NULL;
    
    codegen->main_code = string_new("");
    codegen->function_definitions = string_new("");
    codegen->struct_definitions = string_new("");
    codegen->includes = string_new("#include \"../runtime/pyrinas.h\"\n");
    codegen->current_output = codegen->main_code;  // Default to main code
    codegen->symbol_table = symbol_table;
    codegen->semantic_analyzer = analyzer;
    codegen->indent_level = 0;
    
    if (!codegen->main_code || !codegen->function_definitions || 
        !codegen->struct_definitions || !codegen->includes) {
        codegen_free(codegen);
        return NULL;
    }
    
    return codegen;
}

void codegen_free(CodeGenerator* codegen) {
    if (codegen) {
        string_free(codegen->main_code);
        string_free(codegen->function_definitions);
        string_free(codegen->struct_definitions);
        string_free(codegen->includes);
        free(codegen);
    }
}

// Utility functions
void generate_indent(CodeGenerator* codegen, String* output) {
    for (int i = 0; i < codegen->indent_level; i++) {
        string_append(output, "    ");
    }
}

char* c_type_from_pyrinas_type(const char* pyrinas_type) {
    if (!pyrinas_type) return strdup("void");
    
    if (strcmp(pyrinas_type, "int") == 0) return strdup("int");
    if (strcmp(pyrinas_type, "float") == 0) return strdup("float");
    if (strcmp(pyrinas_type, "bool") == 0) return strdup("int");
    if (strcmp(pyrinas_type, "str") == 0) return strdup("char*");
    if (strcmp(pyrinas_type, "void") == 0) return strdup("void");
    
    if (is_pointer_type(pyrinas_type)) {
        char* base_type = extract_pointer_base_type(pyrinas_type);
        char* c_base = c_type_from_pyrinas_type(base_type);
        char* result = malloc(strlen(c_base) + 2);
        sprintf(result, "%s*", c_base);
        free(base_type);
        free(c_base);
        return result;
    }
    
    if (is_array_type(pyrinas_type)) {
        char* base_type = NULL;
        parse_array_type(pyrinas_type, &base_type, NULL);
        char* c_base = c_type_from_pyrinas_type(base_type);
        char* result = malloc(strlen(c_base) + 2);
        sprintf(result, "%s*", c_base);  // Arrays become pointers in function params
        free(base_type);
        free(c_base);
        return result;
    }
    
    if (is_result_type(pyrinas_type)) {
        return strdup("Result");
    }
    
    // Assume it's a user-defined type (struct/enum)
    char* result = malloc(strlen(pyrinas_type) + 8);
    sprintf(result, "struct %s", pyrinas_type);
    return result;
}

// Main generation function
char* codegen_generate(CodeGenerator* codegen, ASTNode* ast) {
    if (!codegen || !ast || ast->type != AST_MODULE) return NULL;
    
    // Generate struct definitions first
    if (codegen->symbol_table && codegen->symbol_table->global_scope) {
        Scope* scope = codegen->symbol_table->global_scope;
        for (size_t i = 0; i < scope->count; i++) {
            Symbol* symbol = scope->symbols[i];
            if (symbol->type == SYM_STRUCT) {
                generate_struct_definition(codegen, symbol);
            } else if (symbol->type == SYM_ENUM) {
                generate_enum_definition(codegen, symbol);
            }
        }
    }
    
    // Generate function definitions and main
    for (size_t i = 0; i < ast->module.body->count; i++) {
        ASTNode* item = ast->module.body->items[i];
        if (item->type == AST_FUNCTION_DEF) {
            if (strcmp(item->function_def.name, "main") == 0) {
                // Generate main function
                string_append(codegen->main_code, "int main() {\n");
                codegen->indent_level = 1;
                
                for (size_t j = 0; j < item->function_def.body->count; j++) {
                    generate_statement(codegen, item->function_def.body->items[j]);
                }
                
                codegen->indent_level = 0;
                string_append(codegen->main_code, "}\n");
            } else {
                generate_function_def(codegen, item);
            }
        }
    }
    
    // Combine all parts
    String* result = string_new("");
    string_append(result, string_cstr(codegen->includes));
    string_append(result, "\n");
    
    if (string_cstr(codegen->struct_definitions)[0] != '\0') {
        string_append(result, string_cstr(codegen->struct_definitions));
        string_append(result, "\n");
    }
    
    if (string_cstr(codegen->function_definitions)[0] != '\0') {
        string_append(result, string_cstr(codegen->function_definitions));
        string_append(result, "\n");
    }
    
    string_append(result, string_cstr(codegen->main_code));
    
    char* final_result = strdup(string_cstr(result));
    string_free(result);
    return final_result;
}

void generate_struct_definition(CodeGenerator* codegen, Symbol* struct_symbol) {
    string_append(codegen->struct_definitions, "struct ");
    string_append(codegen->struct_definitions, struct_symbol->name);
    string_append(codegen->struct_definitions, " {\n");
    
    for (size_t i = 0; i < struct_symbol->fields.field_count; i++) {
        char* c_type = c_type_from_pyrinas_type(struct_symbol->fields.field_types[i]);
        string_append(codegen->struct_definitions, "    ");
        string_append(codegen->struct_definitions, c_type);
        string_append(codegen->struct_definitions, " ");
        string_append(codegen->struct_definitions, struct_symbol->fields.field_names[i]);
        string_append(codegen->struct_definitions, ";\n");
        free(c_type);
    }
    
    string_append(codegen->struct_definitions, "};\n\n");
}

void generate_enum_definition(CodeGenerator* codegen, Symbol* enum_symbol) {
    string_append(codegen->struct_definitions, "enum ");
    string_append(codegen->struct_definitions, enum_symbol->name);
    string_append(codegen->struct_definitions, " {\n");
    
    for (size_t i = 0; i < enum_symbol->enum_members.member_count; i++) {
        string_append(codegen->struct_definitions, "    ");
        string_append(codegen->struct_definitions, enum_symbol->name);
        string_append(codegen->struct_definitions, "_");
        string_append(codegen->struct_definitions, enum_symbol->enum_members.member_names[i]);
        string_append(codegen->struct_definitions, " = ");
        
        char value_str[32];
        sprintf(value_str, "%d", enum_symbol->enum_members.member_values[i]);
        string_append(codegen->struct_definitions, value_str);
        
        if (i < enum_symbol->enum_members.member_count - 1) {
            string_append(codegen->struct_definitions, ",");
        }
        string_append(codegen->struct_definitions, "\n");
    }
    
    string_append(codegen->struct_definitions, "};\n\n");
}

void generate_function_def(CodeGenerator* codegen, ASTNode* node) {
    if (!node || node->type != AST_FUNCTION_DEF) return;
    
    Symbol* func_symbol = symbol_table_lookup(codegen->symbol_table, node->function_def.name);
    if (!func_symbol) return;
    
    char* return_type = c_type_from_pyrinas_type(func_symbol->return_type);
    string_append(codegen->function_definitions, return_type);
    string_append(codegen->function_definitions, " ");
    string_append(codegen->function_definitions, node->function_def.name);
    string_append(codegen->function_definitions, "(");
    
    // Generate parameters
    if (node->function_def.args && node->function_def.args->type == AST_ARGUMENTS) {
        NodeArray* args = node->function_def.args->arguments.args;
        
        for (size_t i = 0; i < args->count; i++) {
            if (i > 0) string_append(codegen->function_definitions, ", ");
            
            ASTNode* arg = args->items[i];
            if (arg->type == AST_ARG) {
                char* param_type_name = get_type_name(arg->arg.annotation);
                char* c_param_type = c_type_from_pyrinas_type(param_type_name);
                
                string_append(codegen->function_definitions, c_param_type);
                string_append(codegen->function_definitions, " ");
                string_append(codegen->function_definitions, arg->arg.arg);
                
                free(param_type_name);
                free(c_param_type);
            }
        }
    }
    
    string_append(codegen->function_definitions, ") {\n");
    
    // Switch output target to function definitions
    String* saved_output = codegen->current_output;
    codegen->current_output = codegen->function_definitions;
    
    codegen->indent_level = 1;
    for (size_t i = 0; i < node->function_def.body->count; i++) {
        generate_statement(codegen, node->function_def.body->items[i]);
    }
    codegen->indent_level = 0;
    
    // Restore output target
    codegen->current_output = saved_output;
    
    string_append(codegen->function_definitions, "}\n\n");
    
    free(return_type);
}

void generate_statement(CodeGenerator* codegen, ASTNode* node) {
    if (!node) return;
    
    switch (node->type) {
        case AST_ANN_ASSIGN:
            generate_ann_assign(codegen, node);
            break;
        case AST_ASSIGN:
            generate_assign(codegen, node);
            break;
        case AST_IF:
            generate_if(codegen, node);
            break;
        case AST_WHILE:
            generate_while(codegen, node);
            break;
        case AST_FOR:
            generate_for(codegen, node);
            break;
        case AST_RETURN:
            generate_return(codegen, node);
            break;
        case AST_EXPR_STMT:
            generate_expr_stmt(codegen, node);
            break;
        case AST_BREAK:
            generate_indent(codegen, codegen->main_code);
            string_append(codegen->main_code, "break;\n");
            break;
        case AST_CONTINUE:
            generate_indent(codegen, codegen->main_code);
            string_append(codegen->main_code, "continue;\n");
            break;
        case AST_PASS:
            // No-op
            break;
        default:
            break;
    }
}

void generate_ann_assign(CodeGenerator* codegen, ASTNode* node) {
    if (!node || node->type != AST_ANN_ASSIGN) return;
    
    char* var_name = node->ann_assign.target->name.id;
    char* type_name = get_type_name(node->ann_assign.annotation);
    char* c_type = c_type_from_pyrinas_type(type_name);
    
    generate_indent(codegen, codegen->main_code);
    string_append(codegen->main_code, c_type);
    string_append(codegen->main_code, " ");
    string_append(codegen->main_code, var_name);
    
    if (node->ann_assign.value) {
        string_append(codegen->main_code, " = ");
        generate_expression(codegen, node->ann_assign.value, codegen->main_code);
    }
    
    string_append(codegen->main_code, ";\n");
    
    free(type_name);
    free(c_type);
}

void generate_assign(CodeGenerator* codegen, ASTNode* node) {
    if (!node || node->type != AST_ASSIGN) return;
    
    generate_indent(codegen, codegen->main_code);
    
    // Generate target
    if (node->assign.targets->count > 0) {
        generate_expression(codegen, node->assign.targets->items[0], codegen->main_code);
    }
    
    string_append(codegen->main_code, " = ");
    generate_expression(codegen, node->assign.value, codegen->main_code);
    string_append(codegen->main_code, ";\n");
}

void generate_return(CodeGenerator* codegen, ASTNode* node) {
    if (!node || node->type != AST_RETURN) return;
    
    generate_indent(codegen, codegen->current_output);
    string_append(codegen->current_output, "return");
    
    if (node->return_stmt.value) {
        string_append(codegen->current_output, " ");
        generate_expression(codegen, node->return_stmt.value, codegen->current_output);
    }
    
    string_append(codegen->current_output, ";\n");
}

void generate_expr_stmt(CodeGenerator* codegen, ASTNode* node) {
    if (!node || node->type != AST_EXPR_STMT) return;
    
    generate_indent(codegen, codegen->main_code);
    generate_expression(codegen, node->expr_stmt.value, codegen->main_code);
    string_append(codegen->main_code, ";\n");
}

void generate_expression(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node) return;
    
    switch (node->type) {
        case AST_NAME:
            generate_name(codegen, node, output);
            break;
        case AST_CONSTANT:
            generate_constant(codegen, node, output);
            break;
        case AST_BINOP:
            generate_binop(codegen, node, output);
            break;
        case AST_UNARYOP:
            generate_unaryop(codegen, node, output);
            break;
        case AST_COMPARE:
            generate_compare(codegen, node, output);
            break;
        case AST_BOOLOP:
            generate_boolop(codegen, node, output);
            break;
        case AST_CALL:
            generate_call(codegen, node, output);
            break;
        case AST_ATTRIBUTE:
            generate_attribute(codegen, node, output);
            break;
        case AST_SUBSCRIPT:
            generate_subscript(codegen, node, output);
            break;
        default:
            break;
    }
}

void generate_name(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_NAME) return;
    string_append(output, node->name.id);
}

void generate_constant(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_CONSTANT) return;
    
    switch (node->constant.value.type) {
        case CONST_INT: {
            char buf[32];
            sprintf(buf, "%d", node->constant.value.int_val);
            string_append(output, buf);
            break;
        }
        case CONST_FLOAT: {
            char buf[32];
            sprintf(buf, "%f", node->constant.value.float_val);
            string_append(output, buf);
            break;
        }
        case CONST_STRING:
            string_append(output, "\"");
            string_append(output, node->constant.value.str_val);
            string_append(output, "\"");
            break;
        case CONST_BOOL:
            string_append(output, node->constant.value.bool_val ? "1" : "0");
            break;
        case CONST_NONE:
            string_append(output, "NULL");
            break;
    }
}

void generate_binop(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_BINOP) return;
    
    string_append(output, "(");
    generate_expression(codegen, node->binop.left, output);
    
    switch (node->binop.op) {
        case BINOP_ADD: string_append(output, " + "); break;
        case BINOP_SUB: string_append(output, " - "); break;
        case BINOP_MULT: string_append(output, " * "); break;
        case BINOP_DIV: string_append(output, " / "); break;
        case BINOP_MOD: string_append(output, " % "); break;
        case BINOP_FLOORDIV: string_append(output, " / "); break;
    }
    
    generate_expression(codegen, node->binop.right, output);
    string_append(output, ")");
}

void generate_call(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_CALL) return;
    
    if (node->call.func->type == AST_NAME) {
        char* func_name = node->call.func->name.id;
        
        // Handle special built-in functions
        if (strcmp(func_name, "print") == 0) {
            string_append(output, "printf(");
            
            if (node->call.args->count > 0) {
                ASTNode* arg = node->call.args->items[0];
                
                // Determine format specifier based on argument type
                if (arg->type == AST_CONSTANT) {
                    switch (arg->constant.value.type) {
                        case CONST_INT:
                            string_append(output, "\"%d\\n\", ");
                            break;
                        case CONST_FLOAT:
                            string_append(output, "\"%f\\n\", ");
                            break;
                        case CONST_STRING:
                            string_append(output, "\"%s\\n\", ");
                            break;
                        case CONST_BOOL:
                            string_append(output, "\"%d\\n\", ");
                            break;
                        default:
                            string_append(output, "\"%s\\n\", ");
                            break;
                    }
                } else if (arg->type == AST_NAME) {
                    // Look up the variable's type
                    Symbol* symbol = symbol_table_lookup(codegen->symbol_table, arg->name.id);
                    if (symbol && symbol->value_type) {
                        if (strcmp(symbol->value_type, "float") == 0) {
                            string_append(output, "\"%f\\n\", ");
                        } else if (strcmp(symbol->value_type, "str") == 0) {
                            string_append(output, "\"%s\\n\", ");
                        } else if (strcmp(symbol->value_type, "bool") == 0) {
                            string_append(output, "\"%d\\n\", ");
                        } else {
                            string_append(output, "\"%d\\n\", ");  // Default to int
                        }
                    } else {
                        string_append(output, "\"%d\\n\", ");  // Default fallback
                    }
                } else if (arg->type == AST_ATTRIBUTE) {
                    // For struct field access, we need to look up the field type
                    if (arg->attribute.value->type == AST_NAME) {
                        char* var_name = arg->attribute.value->name.id;
                        Symbol* struct_symbol = symbol_table_lookup(codegen->symbol_table, var_name);
                        if (struct_symbol && struct_symbol->value_type) {
                            // Look up the struct definition
                            Symbol* type_symbol = symbol_table_lookup(codegen->symbol_table, struct_symbol->value_type);
                            if (type_symbol && type_symbol->type == SYM_STRUCT) {
                                // Find the field type
                                char* field_name = arg->attribute.attr;
                                for (size_t i = 0; i < type_symbol->fields.field_count; i++) {
                                    if (strcmp(type_symbol->fields.field_names[i], field_name) == 0) {
                                        char* field_type = type_symbol->fields.field_types[i];
                                        if (strcmp(field_type, "float") == 0) {
                                            string_append(output, "\"%f\\n\", ");
                                        } else if (strcmp(field_type, "str") == 0) {
                                            string_append(output, "\"%s\\n\", ");
                                        } else if (strcmp(field_type, "bool") == 0) {
                                            string_append(output, "\"%d\\n\", ");
                                        } else {
                                            string_append(output, "\"%d\\n\", ");  // Default to int
                                        }
                                        goto format_found;
                                    }
                                }
                            }
                        }
                    }
                    // Default fallback for attributes
                    string_append(output, "\"%d\\n\", ");
                    format_found:;
                } else {
                    // Default to %d for other expressions
                    string_append(output, "\"%d\\n\", ");
                }
                
                generate_expression(codegen, arg, output);
            }
            
            string_append(output, ")");
            return;
        }
    }
    
    // Regular function call
    generate_expression(codegen, node->call.func, output);
    string_append(output, "(");
    
    for (size_t i = 0; i < node->call.args->count; i++) {
        if (i > 0) string_append(output, ", ");
        generate_expression(codegen, node->call.args->items[i], output);
    }
    
    string_append(output, ")");
}

void generate_attribute(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_ATTRIBUTE) return;
    
    // Generate the object being accessed
    generate_expression(codegen, node->attribute.value, output);
    string_append(output, ".");
    string_append(output, node->attribute.attr);
}

void generate_subscript(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_SUBSCRIPT) return;
    
    // Generate array[index]
    generate_expression(codegen, node->subscript.value, output);
    string_append(output, "[");
    generate_expression(codegen, node->subscript.slice, output);
    string_append(output, "]");
}

// Placeholder implementations for remaining functions
void generate_if(CodeGenerator* codegen, ASTNode* node) { }
void generate_while(CodeGenerator* codegen, ASTNode* node) { }
void generate_for(CodeGenerator* codegen, ASTNode* node) { }
void generate_unaryop(CodeGenerator* codegen, ASTNode* node, String* output) { }
void generate_compare(CodeGenerator* codegen, ASTNode* node, String* output) {
    if (!node || node->type != AST_COMPARE) return;
    
    // Generate left operand
    generate_expression(codegen, node->compare.left, output);
    
    // For simple comparisons, assume single operator and comparator
    if (node->compare.comparators && node->compare.comparators->count > 0) {
        string_append(output, " ");
        
        // For now, use a simple mapping - we need to check the actual structure
        string_append(output, "==");  // Default operator
        
        string_append(output, " ");
        generate_expression(codegen, node->compare.comparators->items[0], output);
    }
}
void generate_boolop(CodeGenerator* codegen, ASTNode* node, String* output) { }