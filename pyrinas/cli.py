import argparse
import os
import subprocess
from pyrinas.parser import get_ast
from pyrinas.semantic import SemanticAnalyzer, ParentageVisitor
from pyrinas.codegen import CCodeGenerator
from pyrinas.module_resolver import ModuleResolver

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
    
    ParentageVisitor().visit(tree)
    
    # Create module resolver and semantic analyzer
    base_path = os.path.dirname(os.path.abspath(input_file))
    module_resolver = ModuleResolver(base_path)
    analyzer = SemanticAnalyzer(current_file=input_file, module_resolver=module_resolver)
    analyzer.visit(tree)
    
    generator = CCodeGenerator(analyzer.symbol_table, analyzer)
    c_code = generator.generate(tree)
    
    with open(output_file_c, 'w', encoding='utf-8') as f:
        f.write(c_code)
    print(f"Generated C code in {output_file_c}")

    # Compile the generated C code
    c_libraries = list(analyzer.c_libraries) if hasattr(analyzer, 'c_libraries') else []
    compile_c_code(output_file_c, output_executable, c_libraries)
    print(f"Compiled executable to {output_executable}")

def compile_c_code(input_file, output_file, c_libraries=None):
    """
    Compiles a C file into an executable.
    """
    if c_libraries is None:
        c_libraries = []
    
    # Build gcc command
    gcc_cmd = ['gcc', '-I', 'runtime', '-o', output_file, input_file, 'runtime/pyrinas.o']
    
    # Add math library by default for math functions
    gcc_cmd.append('-lm')
    
    # Add additional C libraries
    for lib in c_libraries:
        gcc_cmd.append(f'-l{lib}')
    
    try:
        subprocess.run(gcc_cmd, check=True)
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
