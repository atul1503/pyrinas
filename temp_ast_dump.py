import ast
with open('examples/expressions.py', 'r') as f:
    code = f.read()
tree = ast.parse(code)
print(ast.dump(tree, indent=4))
