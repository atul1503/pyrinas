import ast

class Symbol:
    def __init__(self, name, type, param_types=None, return_type=None):
        self.name = name
        self.type = type
        self.param_types = param_types
        self.return_type = return_type

class SymbolTable:
    def __init__(self):
        self._scopes = [{}] # List of dictionaries, each dict is a scope

    def push_scope(self):
        self._scopes.append({})

    def pop_scope(self):
        if len(self._scopes) > 1:
            self._scopes.pop()
        else:
            raise Exception("Cannot pop global scope.")

    def insert(self, symbol):
        self._scopes[-1][symbol.name] = symbol

    def lookup(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name):
        return self._scopes[-1].get(name)

class SemanticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_return_type = None

    def visit_Module(self, node):
        # Ensure 'main' function is defined
        main_found = False
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'main':
                main_found = True
                break
        if not main_found:
            raise NameError("main function not found.")
        
        # First pass: register all function definitions in the global scope
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                func_name = item.name
                return_type = item.returns.id if isinstance(item.returns, ast.Name) else None
                param_types = []
                for arg in item.args.args:
                    if not isinstance(arg.annotation, ast.Name):
                        raise TypeError(f"Parameter '{arg.arg}' must have a type annotation.")
                    param_types.append(arg.annotation.id)
                
                if self.symbol_table.lookup_current_scope(func_name):
                    raise NameError(f"Function '{func_name}' already defined.")
                self.symbol_table.insert(Symbol(func_name, 'function', param_types=param_types, return_type=return_type))

        # Second pass: visit all nodes for semantic analysis
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Set current function return type for return statement validation
        self.current_function_return_type = node.returns.id if isinstance(node.returns, ast.Name) else None

        # Push a new scope for function parameters and local variables
        self.symbol_table.push_scope()

        # Register parameters in the new scope
        for arg in node.args.args:
            var_name = arg.arg
            type_name = arg.annotation.id
            self.symbol_table.insert(Symbol(var_name, type_name))

        # Visit the function body
        for statement in node.body:
            self.visit(statement)

        # Pop the scope after visiting the body
        self.symbol_table.pop_scope()
        self.current_function_return_type = None # Reset

    def visit_AnnAssign(self, node):
        var_name = node.target.id
        type_name = node.annotation.id
        
        if self.symbol_table.lookup_current_scope(var_name):
            raise NameError(f"Variable '{var_name}' already declared in this scope.")
            
        self.symbol_table.insert(Symbol(var_name, type_name))
        
        if node.value:
            self.visit(node.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            symbol = self.symbol_table.lookup(node.id)
            if not symbol:
                raise NameError(f"Variable '{node.id}' not declared.")
            return symbol.type # Return the type of the variable
        self.generic_visit(node)

    def visit_BinOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Simple type promotion for now
        if left_type == 'float' or right_type == 'float':
            return 'float'
        elif left_type == 'int' and right_type == 'int':
            return 'int'
        else:
            raise TypeError(f"Unsupported binary operation between {left_type} and {right_type}")

    def visit_Compare(self, node):
        left_type = self.visit(node.left)
        # Assuming only one comparator for now
        right_type = self.visit(node.comparators[0])

        # Comparison operations always result in a boolean
        return 'bool'

    def visit_BoolOp(self, node):
        # All operands must be boolean
        for value in node.values:
            if self.visit(value) != 'bool':
                raise TypeError("Operands of boolean operations must be boolean.")
        return 'bool'

    def visit_If(self, node):
        test_type = self.visit(node.test)
        if test_type != 'bool':
            raise TypeError("If condition must be a boolean expression.")
        
        for statement in node.body:
            self.visit(statement)
        
        for statement in node.orelse:
            self.visit(statement)

    def visit_While(self, node):
        test_type = self.visit(node.test)
        if test_type != 'bool':
            raise TypeError("While condition must be a boolean expression.")
        
        for statement in node.body:
            self.visit(statement)

    def visit_For(self, node):
        # Assume loop variable is int for now
        loop_var_name = node.target.id
        if self.symbol_table.lookup_current_scope(loop_var_name):
            raise NameError(f"Variable '{loop_var_name}' already declared in this scope.")
        self.symbol_table.insert(Symbol(loop_var_name, 'int'))

        # Visit the iterable (e.g., range() call)
        self.visit(node.iter)

        # Visit the body of the loop
        for statement in node.body:
            self.visit(statement)

    def visit_UnaryOp(self, node):
        operand_type = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            if operand_type != 'bool': # Assuming 'bool' type for logical operations
                raise TypeError(f"Unsupported unary operation 'not' on type {operand_type}")
            return 'bool'
        else:
            raise NotImplementedError(f"Unary operator {type(node.op).__name__} not implemented.")

    def visit_Return(self, node):
        if not self.current_function_return_type:
            raise Exception("Return statement outside of function.")

        returned_type = self.visit(node.value)
        if returned_type != self.current_function_return_type:
            raise TypeError(f"Return type mismatch: expected {self.current_function_return_type}, got {returned_type}.")

    def visit_Constant(self, node):
        if isinstance(node.value, int):
            return 'int'
        elif isinstance(node.value, float):
            return 'float'
        elif isinstance(node.value, str):
            return 'str'
        elif isinstance(node.value, bool):
            return 'bool'
        else:
            raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name == 'print':
                # For print, we just visit the arguments to ensure they are semantically valid
                for arg in node.args:
                    self.visit(arg)
                return # print doesn't return a value we care about for type checking
            elif func_name == 'range':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, int):
                    raise TypeError("range() expects exactly one integer argument.")
                return 'range_object' # A special type to indicate it's a range object
            else:
                # Handle user-defined function calls
                func_symbol = self.symbol_table.lookup(func_name) # Use lookup for functions as they can be defined before use
                if not func_symbol or func_symbol.type != 'function':
                    raise NameError(f"Function '{func_name}' not defined.")
                
                # Validate argument count and types
                if len(node.args) != len(func_symbol.param_types):
                    raise TypeError(f"Function '{func_name}' expects {len(func_symbol.param_types)} arguments, but got {len(node.args)}.")
                
                for i, arg_node in enumerate(node.args):
                    arg_type = self.visit(arg_node)
                    expected_type = func_symbol.param_types[i]
                    if arg_type != expected_type:
                        raise TypeError(f"Argument {i+1} of function '{func_name}' has type {arg_type}, but expected {expected_type}.")
                
                return func_symbol.return_type
        else:
            raise NotImplementedError("Only direct function calls (e.g., func()) are supported.")

    def visit_Expr(self, node):
        # Visit the expression, but don't return its type
        self.visit(node.value)

if __name__ == '__main__':
    with open('examples/hello.py', 'r') as f:
        code = f.read()
    
    tree = ast.parse(code)
    analyzer = SemanticAnalyzer()
    analyzer.visit(tree)
    print("Semantic analysis successful!")