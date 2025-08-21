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
        self.loop_depth = 0
        self.loop_labels = []

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
        
        type_name = None
        if isinstance(node.annotation, ast.Name):
            type_name = node.annotation.id
        elif isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            type_str = node.annotation.value
            if type_str.startswith('ptr[') and type_str.endswith(']'):
                type_name = type_str  # Keep the full 'ptr[...]' string as the type
            else:
                raise TypeError(f"Invalid string annotation for pointer type: {type_str}")
        elif isinstance(node.annotation, ast.Subscript):
            if getattr(node.annotation.value, 'id', None) != 'array':
                raise TypeError("Only 'array' is supported for subscript type annotations.")
            
            # The slice for an array annotation should be a tuple of (type, size)
            if not isinstance(node.annotation.slice, ast.Tuple) or len(node.annotation.slice.elts) != 2:
                raise TypeError("Array annotation requires a tuple of [type, size].")
            
            base_type_node = node.annotation.slice.elts[0]
            size_node = node.annotation.slice.elts[1]
            
            base_type = getattr(base_type_node, 'id', None)
            if not isinstance(size_node, ast.Constant) or not isinstance(size_node.value, int):
                raise TypeError("Array size must be an integer literal.")
            size = size_node.value

            type_name = f'array[{base_type},{size}]'
        else:
            raise TypeError("Type annotation must be a name, a pointer string, or an array annotation.")

        if self.symbol_table.lookup_current_scope(var_name):
            raise NameError(f"Variable '{var_name}' already declared in this scope.")
            
        self.symbol_table.insert(Symbol(var_name, type_name))
        
        if node.value:
            value_type = self.visit(node.value)
            # Allow assigning ptr[void] (from malloc) to any other pointer type
            if value_type == 'ptr[void]' and type_name.startswith('ptr['):
                pass # This is a valid assignment
            elif value_type != type_name and not (type_name == 'bool' and value_type == 'int'):
                raise TypeError(f"Type mismatch assigning to '{var_name}': expected {type_name}, got {value_type}")

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

    def visit_Subscript(self, node):
        var_name = getattr(node.value, 'id', None)
        symbol = self.symbol_table.lookup(var_name)
        if not symbol or not symbol.type.startswith('array['):
            raise TypeError(f"Variable '{var_name}' is not an array and cannot be subscripted.")
        
        # Check that the index is an integer
        index_type = self.visit(node.slice)
        if index_type != 'int':
            raise TypeError(f"Array index must be an integer, but got {index_type}.")
            
        # Return the base type of the array
        import re
        match = re.match(r'array\[(\w+),(\d+)\]', symbol.type)
        return match.group(1) if match else None

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
        
        self.loop_depth += 1
        # Check for a label preceding the loop
        label = self._get_preceding_label(node)
        if label:
            self.loop_labels.append(label)

        for statement in node.body:
            self.visit(statement)
        
        if label:
            self.loop_labels.pop()
        self.loop_depth -= 1

    def visit_For(self, node):
        # Assume loop variable is int for now
        loop_var_name = node.target.id
        if self.symbol_table.lookup_current_scope(loop_var_name):
            raise NameError(f"Variable '{loop_var_name}' already declared in this scope.")
        self.symbol_table.insert(Symbol(loop_var_name, 'int'))

        # Visit the iterable (e.g., range() call)
        self.visit(node.iter)

        # Visit the body of the loop
        self.loop_depth += 1
        # Check for a label preceding the loop
        label = self._get_preceding_label(node)
        if label:
            self.loop_labels.append(label)

        for statement in node.body:
            self.visit(statement)

        if label:
            self.loop_labels.pop()
        self.loop_depth -= 1

    def visit_UnaryOp(self, node):
        operand_type = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            if operand_type != 'bool': # Assuming 'bool' type for logical operations
                raise TypeError(f"Unsupported unary operation 'not' on type {operand_type}")
            return 'bool'
        else:
            raise NotImplementedError(f"Unary operator {type(node.op).__name__} not implemented.")

    def visit_Break(self, node):
        if self.loop_depth == 0:
            raise SyntaxError("'break' outside loop")
        label = self._get_preceding_label(node)
        if label and label not in self.loop_labels:
            raise NameError(f"Label '{label}' not found.")

    def visit_Continue(self, node):
        if self.loop_depth == 0:
            raise SyntaxError("'continue' outside loop")
        label = self._get_preceding_label(node)
        if label and label not in self.loop_labels:
            raise NameError(f"Label '{label}' not found.")

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
            elif func_name == 'addr':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Name):
                    raise TypeError("addr() expects a single variable name as an argument.")
                var_name = node.args[0].id
                symbol = self.symbol_table.lookup(var_name)
                if not symbol:
                    raise NameError(f"Variable '{var_name}' not declared.")
                return f'ptr[{symbol.type}]'
            elif func_name == 'deref':
                if len(node.args) != 1:
                    raise TypeError("deref() expects a single argument.")
                ptr_type = self.visit(node.args[0])
                if not ptr_type.startswith('ptr[') or not ptr_type.endswith(']'):
                    raise TypeError(f"Cannot dereference non-pointer type: {ptr_type}")
                return ptr_type[4:-1] # Extract the inner type, e.g., 'int' from 'ptr[int]'
            elif func_name == 'assign':
                if len(node.args) != 2:
                    raise TypeError("assign() expects two arguments: a pointer and a value.")
                ptr_type = self.visit(node.args[0])
                if not ptr_type.startswith('ptr[') or not ptr_type.endswith(']'):
                    raise TypeError(f"First argument to assign() must be a pointer, got {ptr_type}")
                
                value_type = self.visit(node.args[1])
                expected_type = ptr_type[4:-1]
                if value_type != expected_type:
                    raise TypeError(f"Type mismatch in assign(): pointer is {ptr_type}, but value is {value_type}")
                return None # assign does not return a value
            elif func_name == 'sizeof':
                if len(node.args) != 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                    raise TypeError("sizeof() expects a single string literal argument representing a type.")
                return 'int' # sizeof always returns an integer
            elif func_name == 'malloc':
                if len(node.args) != 1:
                    raise TypeError("malloc() expects a single integer argument (size).")
                size_type = self.visit(node.args[0])
                if size_type != 'int':
                    raise TypeError(f"Argument to malloc() must be an integer, but got {size_type}.")
                return 'ptr[void]' # malloc returns a generic pointer
            elif func_name == 'free':
                if len(node.args) != 1:
                    raise TypeError("free() expects a single pointer argument.")
                arg_type = self.visit(node.args[0])
                if not arg_type.startswith('ptr['):
                    raise TypeError(f"Argument to free() must be a pointer, but got {arg_type}.")
                return None # free does not return a value
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

    def _get_preceding_label(self, loop_node):
        # This is a bit of a hack. We need to find the label
        # that immediately precedes the loop in the AST.
        if hasattr(loop_node, 'parent'):
            body = loop_node.parent.body
            idx = body.index(loop_node)
            if idx > 0 and isinstance(body[idx - 1], ast.Expr) and isinstance(body[idx - 1].value, ast.Constant) and isinstance(body[idx - 1].value.value, str):
                return body[idx - 1].value.value
        return None

class ParentageVisitor(ast.NodeVisitor):
    def visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
        self.generic_visit(node)

if __name__ == '__main__':
    with open('examples/hello.py', 'r') as f:
        code = f.read()
    
    tree = ast.parse(code)
    ParentageVisitor().visit(tree)
    analyzer = SemanticAnalyzer()
    analyzer.visit(tree)
    print("Semantic analysis successful!")