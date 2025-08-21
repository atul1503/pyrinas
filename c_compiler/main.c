#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#include "lexer.h"
#include "parser.h"
#include "semantic.h"
#include "codegen.h"

void print_usage(const char* program_name) {
    printf("Usage: %s [options] <input_file>\n", program_name);
    printf("Options:\n");
    printf("  -o <output>    Output executable name (default: a.out)\n");
    printf("  -h, --help     Show this help message\n");
}

char* read_file(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return NULL;
    }
    
    // Get file size
    fseek(file, 0, SEEK_END);
    long size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    // Allocate buffer and read file
    char* content = malloc(size + 1);
    if (!content) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        fclose(file);
        return NULL;
    }
    
    size_t bytes_read = fread(content, 1, size, file);
    content[bytes_read] = '\0';
    
    fclose(file);
    return content;
}

bool write_file(const char* filename, const char* content) {
    FILE* file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "Error: Cannot create file '%s'\n", filename);
        return false;
    }
    
    fprintf(file, "%s", content);
    fclose(file);
    return true;
}

bool compile_c_code(const char* c_file, const char* output_file) {
    // Build gcc command
    char command[1024];
    snprintf(command, sizeof(command), 
             "gcc -I ../runtime -o %s %s ../runtime/pyrinas.o -lm", 
             output_file, c_file);
    
    printf("Compiling C code: %s\n", command);
    
    int result = system(command);
    if (result != 0) {
        fprintf(stderr, "Error: C compilation failed\n");
        return false;
    }
    
    return true;
}

int main(int argc, char* argv[]) {
    const char* input_file = NULL;
    const char* output_file = "a.out";
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0) {
            if (i + 1 >= argc) {
                fprintf(stderr, "Error: -o option requires an argument\n");
                return 1;
            }
            output_file = argv[++i];
        } else if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (argv[i][0] == '-') {
            fprintf(stderr, "Error: Unknown option '%s'\n", argv[i]);
            print_usage(argv[0]);
            return 1;
        } else {
            if (input_file) {
                fprintf(stderr, "Error: Multiple input files specified\n");
                return 1;
            }
            input_file = argv[i];
        }
    }
    
    if (!input_file) {
        fprintf(stderr, "Error: No input file specified\n");
        print_usage(argv[0]);
        return 1;
    }
    
    printf("Compiling Pyrinas file: %s\n", input_file);
    
    // Read source file
    char* source_code = read_file(input_file);
    if (!source_code) {
        return 1;
    }
    
    // Tokenize
    printf("Tokenizing...\n");
    Lexer* lexer = lexer_new(source_code);
    if (!lexer) {
        fprintf(stderr, "Error: Failed to create lexer\n");
        free(source_code);
        return 1;
    }
    
    TokenArray* tokens = lexer_tokenize(lexer);
    if (!tokens) {
        fprintf(stderr, "Error: Tokenization failed\n");
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    // Debug: Print tokens (optional)
    if (getenv("PYRINAS_DEBUG_TOKENS")) {
        printf("\nTokens:\n");
        for (size_t i = 0; i < tokens->count; i++) {
            Token* token = &tokens->items[i];
            printf("%s", token_type_name(token->type));
            if (token->value) {
                printf("('%s')", token->value);
            }
            printf(" ");
            if ((i + 1) % 10 == 0) printf("\n");
        }
        printf("\n\n");
    }
    
    // Parse
    printf("Parsing...\n");
    Parser* parser = parser_new(tokens);
    if (!parser) {
        fprintf(stderr, "Error: Failed to create parser\n");
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    ASTNode* ast = parser_parse(parser);
    if (!ast) {
        fprintf(stderr, "Error: Parsing failed");
        if (parser->has_error && parser->error_message) {
            fprintf(stderr, ": %s", parser->error_message);
        }
        fprintf(stderr, "\n");
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    // Debug: Print AST (optional)
    if (getenv("PYRINAS_DEBUG_AST")) {
        printf("\nAST:\n");
        ast_print(ast, 0);
        printf("\n");
    }
    
    // Semantic analysis
    printf("Analyzing semantics...\n");
    SemanticAnalyzer* analyzer = semantic_analyzer_new(input_file);
    if (!analyzer) {
        fprintf(stderr, "Error: Failed to create semantic analyzer\n");
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    if (!analyze_ast(analyzer, ast)) {
        fprintf(stderr, "Error: Semantic analysis failed");
        if (analyzer->has_error && analyzer->error_message) {
            fprintf(stderr, ": %s", analyzer->error_message);
        }
        fprintf(stderr, "\n");
        semantic_analyzer_free(analyzer);
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    // Code generation
    printf("Generating C code...\n");
    CodeGenerator* codegen = codegen_new(analyzer->symbol_table, analyzer);
    if (!codegen) {
        fprintf(stderr, "Error: Failed to create code generator\n");
        semantic_analyzer_free(analyzer);
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    char* c_code = codegen_generate(codegen, ast);
    if (!c_code) {
        fprintf(stderr, "Error: Code generation failed\n");
        codegen_free(codegen);
        semantic_analyzer_free(analyzer);
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    // Write C code to file
    char c_filename[256];
    strcpy(c_filename, input_file);
    char* dot = strrchr(c_filename, '.');
    if (dot) {
        strcpy(dot, ".c");
    } else {
        strcat(c_filename, ".c");
    }
    
    printf("Writing C code to: %s\n", c_filename);
    if (!write_file(c_filename, c_code)) {
        free(c_code);
        codegen_free(codegen);
        semantic_analyzer_free(analyzer);
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    // Debug: Print generated C code (optional)
    if (getenv("PYRINAS_DEBUG_CODEGEN")) {
        printf("\nGenerated C code:\n");
        printf("%s\n", c_code);
    }
    
    // Compile C code
    printf("Compiling to executable: %s\n", output_file);
    if (!compile_c_code(c_filename, output_file)) {
        free(c_code);
        codegen_free(codegen);
        semantic_analyzer_free(analyzer);
        ast_node_free(ast);
        parser_free(parser);
        lexer_free(lexer);
        free(source_code);
        return 1;
    }
    
    printf("Compilation successful!\n");
    
    // Cleanup
    free(c_code);
    codegen_free(codegen);
    semantic_analyzer_free(analyzer);
    ast_node_free(ast);
    parser_free(parser);
    lexer_free(lexer);
    free(source_code);
    
    return 0;
}