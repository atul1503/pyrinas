import argparse
import os
import subprocess
from pyrinas.parser import get_ast
from pyrinas.semantic import SemanticAnalyzer
from pyrinas.codegen import CCodeGenerator

def compile_file(input_file, output_file_c, output_executable):
    """
    Compiles a single Pyrinas file.
    """
    with open(input_file, 'r') as f:
        code = f.read()
    
    tree = get_ast(code)
    import ast
    print("AST DUMP:")
    print(ast.dump(tree, indent=4))
    
    analyzer = SemanticAnalyzer()
    analyzer.visit(tree)
    
    generator = CCodeGenerator(analyzer.symbol_table)
    c_code = generator.generate(tree)
    
    with open(output_file_c, 'w', encoding='utf-8') as f:
        f.write(c_code)
    print(f"Generated C code in {output_file_c}")

    # Compile the generated C code
    compile_c_code(output_file_c, output_executable)
    print(f"Compiled executable to {output_executable}")

def compile_c_code(input_file, output_file):
    """
    Compiles a C file into an executable.
    """
    try:
        subprocess.run(['gcc', '-I', 'runtime', '-o', output_file, input_file, 'runtime/pyrinas.o'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during C compilation: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description='Pyrinas Compiler')
    parser.add_argument('input_file', help='The Pyrinas source file to compile.')
    parser.add_argument('-o', '--output', help='The output file name for the executable.', default='a.out')
    args = parser.parse_args()

    input_file = args.input_file
    output_file_c = os.path.splitext(input_file)[0] + '.c'
    
    compile_file(input_file, output_file_c, args.output)

if __name__ == '__main__':
    main()
