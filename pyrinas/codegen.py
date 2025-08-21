import ast

class CCodeGenerator(ast.NodeVisitor):
    def __init__(self, symbol_table):
        self.main_code = []
        self.function_definitions = []
        self.symbol_table = symbol_table
        self.indent_level = 0
        self.current_code_list = None
        self.local_vars = {}  # Track variable types as we encounter them

    def _indent(self):
        return "    " * self.indent_level

    def visit_Module(self, node):
        # First, generate code for all functions
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name != 'main':
                self.visit(item)

        # Then, generate code for the main function
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'main':
                self.visit(item)

    def visit_FunctionDef(self, node):
        if node.name == 'main':
            self.current_code_list = self.main_code
            self.main_code.append('int main() {')
        else:
            self.current_code_list = []
            func_symbol = self.symbol_table.lookup(node.name)
            return_type = func_symbol.return_type
            params = [f'{func_symbol.param_types[i]} {arg.arg}' for i, arg in enumerate(node.args.args)]
            param_str = ', '.join(params)
            self.current_code_list.append(f'{return_type} {node.name}({param_str}) {{')

        self.indent_level += 1
        for statement in node.body:
            self.visit(statement)
        self.indent_level -= 1
        self.current_code_list.append('}')

        if node.name != 'main':
            self.function_definitions.extend(self.current_code_list)

    def visit_AnnAssign(self, node):
        var_name = node.target.id
        type_name = node.annotation.id
        c_type = {'int': 'int', 'float': 'float', 'bool': 'int'}.get(type_name)
        
        # Track the variable type for print statements
        self.local_vars[var_name] = type_name
        
        if node.value:
            self.current_code_list.append(f'{self._indent()}{c_type} {var_name} = {self.visit(node.value)};')
        else:
            self.current_code_list.append(f'{self._indent()}{c_type} {var_name};')

    def visit_Assign(self, node):
        target = self.visit(node.targets[0])
        value = self.visit(node.value)
        self.current_code_list.append(f'{self._indent()}{target} = {value};')

    def visit_Name(self, node):
        return node.id
        
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value) if not isinstance(node.value, bool) else ('1' if node.value else '0')

    def visit_BinOp(self, node):
        op_map = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}
        return f'({self.visit(node.left)} {op_map[type(node.op)]} {self.visit(node.right)})'

    def visit_Compare(self, node):
        op_map = {ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>='}
        return f'({self.visit(node.left)} {op_map[type(node.ops[0])]} {self.visit(node.comparators[0])})'

    def visit_BoolOp(self, node):
        op_map = {ast.And: '&&', ast.Or: '||'}
        return f'({op_map[type(node.op)].join([self.visit(v) for v in node.values])})'

    def visit_If(self, node):
        self.current_code_list.append(f'{self._indent()}if ({self.visit(node.test)}) {{')
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.current_code_list.append(f'{self._indent()}}}')
        if node.orelse:
            self.current_code_list.append(f'{self._indent()}else {{')
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.current_code_list.append(f'{self._indent()}}}')

    def visit_While(self, node):
        self.current_code_list.append(f'{self._indent()}while ({self.visit(node.test)}) {{')
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.current_code_list.append(f'{self._indent()}}}')

    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            limit = node.iter.args[0].value
            loop_var = node.target.id
            self.current_code_list.append(f'{self._indent()}for (int {loop_var} = 0; {loop_var} < {limit}; {loop_var}++) {{')
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.current_code_list.append(f'{self._indent()}}}')

    def visit_UnaryOp(self, node):
        return f'(!{self.visit(node.operand)})' if isinstance(node.op, ast.Not) else self.visit(node.operand)

    def visit_Call(self, node):
        if node.func.id == 'print':
            arg = node.args[0]
            expr_code = self.visit(arg)
            
            # Determine the type of the argument
            arg_type = 'int'  # default
            format_specifier = '%d'
            
            if isinstance(arg, ast.Name):
                # It's a variable, look it up in our local tracking
                if arg.id in self.local_vars:
                    arg_type = self.local_vars[arg.id]
            elif isinstance(arg, ast.Constant):
                # It's a literal constant
                if isinstance(arg.value, str):
                    arg_type = 'string'
                elif isinstance(arg.value, float):
                    arg_type = 'float'
                elif isinstance(arg.value, bool):
                    arg_type = 'bool'
                else:
                    arg_type = 'int'
            
            # Set the appropriate format specifier
            if arg_type == 'float':
                format_specifier = '%f'
            elif arg_type == 'string':
                format_specifier = '%s'
            elif arg_type == 'bool':
                format_specifier = '%d'  # booleans are printed as 0/1
            else:  # int
                format_specifier = '%d'
            
            self.current_code_list.append(f'{self._indent()}printf("{format_specifier}\\n", {expr_code});')
            return ""
        else:
            args_str = ', '.join([self.visit(arg) for arg in node.args])
            return f'{node.func.id}({args_str})'
            
    def visit_Return(self, node):
        self.current_code_list.append(f'{self._indent()}return {self.visit(node.value)};')

    def generate(self, tree):
        self.visit(tree)
        return '#include "pyrinas.h"\n\n' + '\n'.join(self.function_definitions) + '\n\n' + '\n'.join(self.main_code)