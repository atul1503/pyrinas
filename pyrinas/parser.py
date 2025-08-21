import ast

def get_ast(code: str):
    """
    Parses the given Python code and returns an AST.
    """
    return ast.parse(code)

if __name__ == '__main__':
    with open('examples/hello.pyr', 'r') as f:
        code = f.read()
    
    tree = get_ast(code)
    print(ast.dump(tree))
