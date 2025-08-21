#include "ast.h"

// String implementation
String* string_new(const char* initial) {
    String* str = malloc(sizeof(String));
    if (!str) return NULL;
    
    size_t len = initial ? strlen(initial) : 0;
    str->capacity = len + 16;  // Initial capacity
    str->data = malloc(str->capacity);
    if (!str->data) {
        free(str);
        return NULL;
    }
    
    if (initial) {
        strcpy(str->data, initial);
        str->length = len;
    } else {
        str->data[0] = '\0';
        str->length = 0;
    }
    
    return str;
}

void string_append(String* str, const char* to_append) {
    if (!str || !to_append) return;
    
    size_t append_len = strlen(to_append);
    size_t new_len = str->length + append_len;
    
    if (new_len >= str->capacity) {
        size_t new_capacity = (new_len + 1) * 2;
        char* new_data = realloc(str->data, new_capacity);
        if (!new_data) return;
        str->data = new_data;
        str->capacity = new_capacity;
    }
    
    strcpy(str->data + str->length, to_append);
    str->length = new_len;
}

void string_free(String* str) {
    if (str) {
        free(str->data);
        free(str);
    }
}

char* string_cstr(String* str) {
    return str ? str->data : NULL;
}

// NodeArray implementation
NodeArray* node_array_new(void) {
    NodeArray* arr = malloc(sizeof(NodeArray));
    if (!arr) return NULL;
    
    arr->capacity = 8;
    arr->items = malloc(sizeof(ASTNode*) * arr->capacity);
    if (!arr->items) {
        free(arr);
        return NULL;
    }
    arr->count = 0;
    return arr;
}

void node_array_push(NodeArray* arr, ASTNode* node) {
    if (!arr || !node) return;
    
    if (arr->count >= arr->capacity) {
        size_t new_capacity = arr->capacity * 2;
        ASTNode** new_items = realloc(arr->items, sizeof(ASTNode*) * new_capacity);
        if (!new_items) return;
        arr->items = new_items;
        arr->capacity = new_capacity;
    }
    
    arr->items[arr->count++] = node;
}

void node_array_free(NodeArray* arr) {
    if (arr) {
        if (arr->items) {
            for (size_t i = 0; i < arr->count; i++) {
                ast_node_free(arr->items[i]);
            }
            free(arr->items);
        }
        free(arr);
    }
}

// StringArray implementation
StringArray* string_array_new(void) {
    StringArray* arr = malloc(sizeof(StringArray));
    if (!arr) return NULL;
    
    arr->capacity = 8;
    arr->items = malloc(sizeof(char*) * arr->capacity);
    if (!arr->items) {
        free(arr);
        return NULL;
    }
    arr->count = 0;
    return arr;
}

void string_array_push(StringArray* arr, const char* str) {
    if (!arr || !str) return;
    
    if (arr->count >= arr->capacity) {
        size_t new_capacity = arr->capacity * 2;
        char** new_items = realloc(arr->items, sizeof(char*) * new_capacity);
        if (!new_items) return;
        arr->items = new_items;
        arr->capacity = new_capacity;
    }
    
    arr->items[arr->count] = strdup(str);
    arr->count++;
}

void string_array_free(StringArray* arr) {
    if (arr) {
        if (arr->items) {
            for (size_t i = 0; i < arr->count; i++) {
                free(arr->items[i]);
            }
            free(arr->items);
        }
        free(arr);
    }
}

// AST Node constructors
ASTNode* ast_module_new(NodeArray* body) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_MODULE;
    node->line_no = 0;
    node->module.body = body;
    return node;
}

ASTNode* ast_function_def_new(const char* name, ASTNode* args, ASTNode* returns, NodeArray* body, NodeArray* decorators) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_FUNCTION_DEF;
    node->line_no = 0;
    node->function_def.name = name ? strdup(name) : NULL;
    node->function_def.args = args;
    node->function_def.returns = returns;
    node->function_def.body = body;
    node->function_def.decorator_list = decorators;
    return node;
}

ASTNode* ast_class_def_new(const char* name, NodeArray* bases, NodeArray* body) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CLASS_DEF;
    node->line_no = 0;
    node->class_def.name = name ? strdup(name) : NULL;
    node->class_def.bases = bases;
    node->class_def.body = body;
    return node;
}

ASTNode* ast_assign_new(NodeArray* targets, ASTNode* value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_ASSIGN;
    node->line_no = 0;
    node->assign.targets = targets;
    node->assign.value = value;
    return node;
}

ASTNode* ast_ann_assign_new(ASTNode* target, ASTNode* annotation, ASTNode* value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_ANN_ASSIGN;
    node->line_no = 0;
    node->ann_assign.target = target;
    node->ann_assign.annotation = annotation;
    node->ann_assign.value = value;
    return node;
}

ASTNode* ast_if_new(ASTNode* test, NodeArray* body, NodeArray* orelse) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_IF;
    node->line_no = 0;
    node->if_stmt.test = test;
    node->if_stmt.body = body;
    node->if_stmt.orelse = orelse;
    return node;
}

ASTNode* ast_while_new(ASTNode* test, NodeArray* body) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_WHILE;
    node->line_no = 0;
    node->while_stmt.test = test;
    node->while_stmt.body = body;
    return node;
}

ASTNode* ast_for_new(ASTNode* target, ASTNode* iter, NodeArray* body) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_FOR;
    node->line_no = 0;
    node->for_stmt.target = target;
    node->for_stmt.iter = iter;
    node->for_stmt.body = body;
    return node;
}

ASTNode* ast_break_new(const char* label) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_BREAK;
    node->line_no = 0;
    node->break_continue.label = label ? strdup(label) : NULL;
    return node;
}

ASTNode* ast_continue_new(const char* label) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONTINUE;
    node->line_no = 0;
    node->break_continue.label = label ? strdup(label) : NULL;
    return node;
}

ASTNode* ast_return_new(ASTNode* value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_RETURN;
    node->line_no = 0;
    node->return_stmt.value = value;
    return node;
}

ASTNode* ast_expr_stmt_new(ASTNode* value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_EXPR_STMT;
    node->line_no = 0;
    node->expr_stmt.value = value;
    return node;
}

ASTNode* ast_pass_new(void) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_PASS;
    node->line_no = 0;
    return node;
}

ASTNode* ast_match_new(ASTNode* subject, NodeArray* cases) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_MATCH;
    node->line_no = 0;
    node->match_stmt.subject = subject;
    node->match_stmt.cases = cases;
    return node;
}

ASTNode* ast_match_case_new(ASTNode* pattern, NodeArray* body) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_MATCH_CASE;
    node->line_no = 0;
    node->match_case.pattern = pattern;
    node->match_case.body = body;
    return node;
}

ASTNode* ast_name_new(const char* id, ExprContext ctx) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_NAME;
    node->line_no = 0;
    node->name.id = id ? strdup(id) : NULL;
    node->name.ctx = ctx;
    return node;
}

ASTNode* ast_constant_int_new(int value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONSTANT;
    node->line_no = 0;
    node->constant.value.type = CONST_INT;
    node->constant.value.int_val = value;
    return node;
}

ASTNode* ast_constant_float_new(double value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONSTANT;
    node->line_no = 0;
    node->constant.value.type = CONST_FLOAT;
    node->constant.value.float_val = value;
    return node;
}

ASTNode* ast_constant_string_new(const char* value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONSTANT;
    node->line_no = 0;
    node->constant.value.type = CONST_STRING;
    node->constant.value.str_val = value ? strdup(value) : NULL;
    return node;
}

ASTNode* ast_constant_bool_new(bool value) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONSTANT;
    node->line_no = 0;
    node->constant.value.type = CONST_BOOL;
    node->constant.value.bool_val = value;
    return node;
}

ASTNode* ast_constant_none_new(void) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CONSTANT;
    node->line_no = 0;
    node->constant.value.type = CONST_NONE;
    return node;
}

ASTNode* ast_binop_new(ASTNode* left, BinOpType op, ASTNode* right) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_BINOP;
    node->line_no = 0;
    node->binop.left = left;
    node->binop.op = op;
    node->binop.right = right;
    return node;
}

ASTNode* ast_unaryop_new(UnaryOpType op, ASTNode* operand) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_UNARYOP;
    node->line_no = 0;
    node->unaryop.op = op;
    node->unaryop.operand = operand;
    return node;
}

ASTNode* ast_compare_new(ASTNode* left, CompareOpType* ops, NodeArray* comparators, size_t ops_count) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_COMPARE;
    node->line_no = 0;
    node->compare.left = left;
    node->compare.ops = ops;
    node->compare.comparators = comparators;
    node->compare.ops_count = ops_count;
    return node;
}

ASTNode* ast_boolop_new(BoolOpType op, NodeArray* values) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_BOOLOP;
    node->line_no = 0;
    node->boolop.op = op;
    node->boolop.values = values;
    return node;
}

ASTNode* ast_call_new(ASTNode* func, NodeArray* args) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_CALL;
    node->line_no = 0;
    node->call.func = func;
    node->call.args = args;
    return node;
}

ASTNode* ast_attribute_new(ASTNode* value, const char* attr, ExprContext ctx) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_ATTRIBUTE;
    node->line_no = 0;
    node->attribute.value = value;
    node->attribute.attr = attr ? strdup(attr) : NULL;
    node->attribute.ctx = ctx;
    return node;
}

ASTNode* ast_subscript_new(ASTNode* value, ASTNode* slice, ExprContext ctx) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_SUBSCRIPT;
    node->line_no = 0;
    node->subscript.value = value;
    node->subscript.slice = slice;
    node->subscript.ctx = ctx;
    return node;
}

ASTNode* ast_arg_new(const char* arg, ASTNode* annotation) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_ARG;
    node->line_no = 0;
    node->arg.arg = arg ? strdup(arg) : NULL;
    node->arg.annotation = annotation;
    return node;
}

ASTNode* ast_arguments_new(NodeArray* args) {
    ASTNode* node = malloc(sizeof(ASTNode));
    if (!node) return NULL;
    
    node->type = AST_ARGUMENTS;
    node->line_no = 0;
    node->arguments.args = args;
    return node;
}

// Memory management
void ast_node_free(ASTNode* node) {
    if (!node) return;
    
    switch (node->type) {
        case AST_MODULE:
            node_array_free(node->module.body);
            break;
            
        case AST_FUNCTION_DEF:
            free(node->function_def.name);
            ast_node_free(node->function_def.args);
            ast_node_free(node->function_def.returns);
            node_array_free(node->function_def.body);
            node_array_free(node->function_def.decorator_list);
            break;
            
        case AST_CLASS_DEF:
            free(node->class_def.name);
            node_array_free(node->class_def.bases);
            node_array_free(node->class_def.body);
            break;
            
        case AST_ASSIGN:
            node_array_free(node->assign.targets);
            ast_node_free(node->assign.value);
            break;
            
        case AST_ANN_ASSIGN:
            ast_node_free(node->ann_assign.target);
            ast_node_free(node->ann_assign.annotation);
            ast_node_free(node->ann_assign.value);
            break;
            
        case AST_IF:
            ast_node_free(node->if_stmt.test);
            node_array_free(node->if_stmt.body);
            node_array_free(node->if_stmt.orelse);
            break;
            
        case AST_WHILE:
            ast_node_free(node->while_stmt.test);
            node_array_free(node->while_stmt.body);
            break;
            
        case AST_FOR:
            ast_node_free(node->for_stmt.target);
            ast_node_free(node->for_stmt.iter);
            node_array_free(node->for_stmt.body);
            break;
            
        case AST_BREAK:
        case AST_CONTINUE:
            free(node->break_continue.label);
            break;
            
        case AST_RETURN:
            ast_node_free(node->return_stmt.value);
            break;
            
        case AST_EXPR_STMT:
            ast_node_free(node->expr_stmt.value);
            break;
            
        case AST_MATCH:
            ast_node_free(node->match_stmt.subject);
            node_array_free(node->match_stmt.cases);
            break;
            
        case AST_MATCH_CASE:
            ast_node_free(node->match_case.pattern);
            node_array_free(node->match_case.body);
            break;
            
        case AST_NAME:
            free(node->name.id);
            break;
            
        case AST_CONSTANT:
            if (node->constant.value.type == CONST_STRING) {
                free(node->constant.value.str_val);
            }
            break;
            
        case AST_BINOP:
            ast_node_free(node->binop.left);
            ast_node_free(node->binop.right);
            break;
            
        case AST_UNARYOP:
            ast_node_free(node->unaryop.operand);
            break;
            
        case AST_COMPARE:
            ast_node_free(node->compare.left);
            free(node->compare.ops);
            node_array_free(node->compare.comparators);
            break;
            
        case AST_BOOLOP:
            node_array_free(node->boolop.values);
            break;
            
        case AST_CALL:
            ast_node_free(node->call.func);
            node_array_free(node->call.args);
            break;
            
        case AST_ATTRIBUTE:
            ast_node_free(node->attribute.value);
            free(node->attribute.attr);
            break;
            
        case AST_SUBSCRIPT:
            ast_node_free(node->subscript.value);
            ast_node_free(node->subscript.slice);
            break;
            
        case AST_ARG:
            free(node->arg.arg);
            ast_node_free(node->arg.annotation);
            break;
            
        case AST_ARGUMENTS:
            node_array_free(node->arguments.args);
            break;
            
        case AST_PASS:
            // Nothing to free
            break;
    }
    
    free(node);
}

// Utility functions
const char* ast_node_type_name(ASTNodeType type) {
    switch (type) {
        case AST_MODULE: return "Module";
        case AST_FUNCTION_DEF: return "FunctionDef";
        case AST_CLASS_DEF: return "ClassDef";
        case AST_ASSIGN: return "Assign";
        case AST_ANN_ASSIGN: return "AnnAssign";
        case AST_IF: return "If";
        case AST_WHILE: return "While";
        case AST_FOR: return "For";
        case AST_BREAK: return "Break";
        case AST_CONTINUE: return "Continue";
        case AST_RETURN: return "Return";
        case AST_EXPR_STMT: return "Expr";
        case AST_PASS: return "Pass";
        case AST_MATCH: return "Match";
        case AST_MATCH_CASE: return "MatchCase";
        case AST_NAME: return "Name";
        case AST_CONSTANT: return "Constant";
        case AST_BINOP: return "BinOp";
        case AST_UNARYOP: return "UnaryOp";
        case AST_COMPARE: return "Compare";
        case AST_BOOLOP: return "BoolOp";
        case AST_CALL: return "Call";
        case AST_ATTRIBUTE: return "Attribute";
        case AST_SUBSCRIPT: return "Subscript";
        case AST_ARG: return "arg";
        case AST_ARGUMENTS: return "arguments";
        default: return "Unknown";
    }
}

void ast_print(ASTNode* node, int indent) {
    if (!node) return;
    
    for (int i = 0; i < indent; i++) {
        printf("  ");
    }
    
    printf("%s", ast_node_type_name(node->type));
    
    switch (node->type) {
        case AST_NAME:
            printf("(id='%s')", node->name.id);
            break;
        case AST_CONSTANT:
            switch (node->constant.value.type) {
                case CONST_INT:
                    printf("(value=%d)", node->constant.value.int_val);
                    break;
                case CONST_FLOAT:
                    printf("(value=%f)", node->constant.value.float_val);
                    break;
                case CONST_STRING:
                    printf("(value='%s')", node->constant.value.str_val);
                    break;
                case CONST_BOOL:
                    printf("(value=%s)", node->constant.value.bool_val ? "True" : "False");
                    break;
                case CONST_NONE:
                    printf("(value=None)");
                    break;
            }
            break;
        case AST_FUNCTION_DEF:
            printf("(name='%s')", node->function_def.name);
            break;
        case AST_CLASS_DEF:
            printf("(name='%s')", node->class_def.name);
            break;
        default:
            break;
    }
    
    printf("\n");
    
    // Print children based on node type
    switch (node->type) {
        case AST_MODULE:
            if (node->module.body) {
                for (size_t i = 0; i < node->module.body->count; i++) {
                    ast_print(node->module.body->items[i], indent + 1);
                }
            }
            break;
        case AST_FUNCTION_DEF:
            if (node->function_def.args) {
                ast_print(node->function_def.args, indent + 1);
            }
            if (node->function_def.returns) {
                ast_print(node->function_def.returns, indent + 1);
            }
            if (node->function_def.body) {
                for (size_t i = 0; i < node->function_def.body->count; i++) {
                    ast_print(node->function_def.body->items[i], indent + 1);
                }
            }
            break;
        // Add other cases as needed...
        default:
            break;
    }
}