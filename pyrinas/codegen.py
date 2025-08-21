import ast
import re

class CCodeGenerator(ast.NodeVisitor):
    def __init__(self, symbol_table):
        self.main_code = []
        self.function_definitions = []
        self.struct_definitions = []
        self.symbol_table = symbol_table
        self.indent_level = 0
        self.current_code_list = None
        self.local_vars = {}  # Track variable types as we encounter them
        self.loop_labels = []

    def _indent(self):
        return "    " * self.indent_level

    def visit_Module(self, node):
        # First, generate code for all struct definitions
        for item in node.body:
            if isinstance(item, ast.ClassDef):
                self.visit(item)

        # Then, generate code for all functions
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
            return_type_str = func_symbol.return_type
            
            # Handle functions without return types
            if return_type_str is None:
                return_type = 'void'
            # Handle Result return types
            elif return_type_str.startswith('Result['):
                return_type = 'Result'
            else:
                return_type = self._c_type_from_pyrinas_type(return_type_str)
                
            params = [f'{self._c_type_from_pyrinas_type(func_symbol.param_types[i])} {arg.arg}' for i, arg in enumerate(node.args.args)]
            param_str = ', '.join(params)
            self.current_code_list.append(f'{return_type} {node.name}({param_str}) {{')

        self.indent_level += 1
        for statement in node.body:
            self.visit(statement)
        self.indent_level -= 1
        self.current_code_list.append('}')

        if node.name != 'main':
            self.function_definitions.extend(self.current_code_list)

    def visit_ClassDef(self, node):
        struct_name = node.name
        self.struct_definitions.append(f'struct {struct_name} {{')
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                field_name = stmt.target.id
                field_type_name = stmt.annotation.id # Simplified
                c_field_type = self._c_type_from_pyrinas_type(field_type_name)
                self.struct_definitions.append(f'    {c_field_type} {field_name};')
        self.struct_definitions.append('};')

    def visit_AnnAssign(self, node):
        var_name = node.target.id
        type_name = None
        is_immutable = False

        if isinstance(node.annotation, ast.Name):
            type_name = node.annotation.id
        elif isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            type_name = node.annotation.value
        elif isinstance(node.annotation, ast.Subscript):
            annotation_name = getattr(node.annotation.value, 'id', None)
            
            if annotation_name == 'Final':
                # Handle Final[type] for immutable variables
                is_immutable = True
                inner_annotation = node.annotation.slice
                
                if isinstance(inner_annotation, ast.Name):
                    type_name = inner_annotation.id
                elif isinstance(inner_annotation, ast.Constant) and isinstance(inner_annotation.value, str):
                    type_name = inner_annotation.value
                else:
                    raise TypeError("Final annotation must contain a simple type.")
                    
            elif annotation_name == 'array':
                # Handle array[type, size] annotations
                base_type_node = node.annotation.slice.elts[0]
                size_node = node.annotation.slice.elts[1]
                base_type = getattr(base_type_node, 'id', None)
                size = size_node.value
                type_name = f'array[{base_type},{size}]'
            else:
                raise TypeError(f"Unsupported subscript annotation: {annotation_name}")
        else:
            raise TypeError("Unsupported type annotation for code generation.")

        # Special handling for array declarations
        if type_name.startswith('array['):
            match = re.match(r'array\[(\w+),\s*(\d+)\]', type_name)
            base_type, size = match.groups()
            c_base_type = self._c_type_from_pyrinas_type(base_type)
            const_prefix = 'const ' if is_immutable else ''
            self.current_code_list.append(f'{self._indent()}{const_prefix}{c_base_type} {var_name}[{size}];')
            self.local_vars[var_name] = type_name
            return

        c_type = self._c_type_from_pyrinas_type(type_name)
        const_prefix = 'const ' if is_immutable else ''
        
        # Track the variable type for print statements
        self.local_vars[var_name] = type_name
        
        if node.value:
            self.current_code_list.append(f'{self._indent()}{const_prefix}{c_type} {var_name} = {self.visit(node.value)};')
        else:
            self.current_code_list.append(f'{self._indent()}{const_prefix}{c_type} {var_name};')

    def visit_Assign(self, node):
        target = self.visit(node.targets[0])
        value = self.visit(node.value)
        self.current_code_list.append(f'{self._indent()}{target} = {value};')

    def visit_Attribute(self, node):
        var = self.visit(node.value)
        attr = node.attr
        return f'{var}.{attr}'

    def visit_Subscript(self, node):
        var = self.visit(node.value)
        idx = self.visit(node.slice)
        return f'{var}[{idx}]'
    
    def visit_Expr(self, node):
        # Handle expression statements (like standalone function calls)
        expr_result = self.visit(node.value)
        if expr_result:  # Only add to code if there's a result
            # If it's a function call that doesn't return anything (like print or assign),
            # it will have been added to current_code_list already, so don't add it again
            if not expr_result.strip().endswith(';'):
                self.current_code_list.append(f'{self._indent()}{expr_result};')

    def visit_Match(self, node):
        subject = self.visit(node.subject)
        self.current_code_list.append(f'{self._indent()}if ({subject}.type == OK) {{')
        self.indent_level += 1
        
        # Handle the Ok case
        ok_case = node.cases[0]
        ok_var_name = ok_case.pattern.name
        # This is a simplification; we need to know the type of the value
        self.current_code_list.append(f'{self._indent()}int {ok_var_name} = {subject}.value.int_val;')
        for stmt in ok_case.body:
            self.visit(stmt)
        
        self.indent_level -= 1
        self.current_code_list.append(f'{self._indent()}}} else {{')
        self.indent_level += 1

        # Handle the Err case
        err_case = node.cases[1]
        err_var_name = err_case.pattern.name
        # This is a simplification; we need to know the type of the value
        self.current_code_list.append(f'{self._indent()}char* {err_var_name} = {subject}.value.str_val;')
        for stmt in err_case.body:
            self.visit(stmt)

        self.indent_level -= 1
        self.current_code_list.append(f'{self._indent()}}}')

    def visit_Name(self, node):
        return node.id
        
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value) if not isinstance(node.value, bool) else ('1' if node.value else '0')

    def visit_BinOp(self, node):
        op_map = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.Mod: '%', ast.FloorDiv: '/'}
        return f'({self.visit(node.left)} {op_map[type(node.op)]} {self.visit(node.right)})'

    def visit_Compare(self, node):
        op_map = {ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>='}
        return f'({self.visit(node.left)} {op_map[type(node.ops[0])]} {self.visit(node.comparators[0])})'

    def visit_BoolOp(self, node):
        op_map = {ast.And: '&&', ast.Or: '||'}
        return f'({op_map[type(node.op)].join([self.visit(v) for v in node.values])})'

    def visit_Break(self, node):
        label = self._get_preceding_label(node)
        if label:
            self.current_code_list.append(f'{self._indent()}goto {label}_break;')
        else:
            self.current_code_list.append(f'{self._indent()}break;')

    def visit_Continue(self, node):
        label = self._get_preceding_label(node)
        if label:
            self.current_code_list.append(f'{self._indent()}goto {label}_continue;')
        else:
            self.current_code_list.append(f'{self._indent()}continue;')

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
        label = self._get_preceding_label(node)
        if label:
            self.current_code_list.append(f'{self._indent()}{label}:')
            self.loop_labels.append(label)

        self.current_code_list.append(f'{self._indent()}while ({self.visit(node.test)}) {{')
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        
        if label:
            self.current_code_list.append(f'{self._indent()}{label}_continue:;')
        
        self.current_code_list.append(f'{self._indent()}}}')

        if label:
            self.current_code_list.append(f'{self._indent()}{label}_break:;')
            self.loop_labels.pop()

    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and node.iter.func.id == 'range':
            limit = node.iter.args[0].value
            loop_var = node.target.id
            
            label = self._get_preceding_label(node)
            if label:
                self.current_code_list.append(f'{self._indent()}{label}:')
                self.loop_labels.append(label)

            self.current_code_list.append(f'{self._indent()}for (int {loop_var} = 0; {loop_var} < {limit}; {loop_var}++) {{')
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            
            if label:
                self.current_code_list.append(f'{self._indent()}{label}_continue:;')
            
            self.current_code_list.append(f'{self._indent()}}}')
            
            if label:
                self.current_code_list.append(f'{self._indent()}{label}_break:;')
                self.loop_labels.pop()

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
            elif isinstance(arg, ast.Attribute):
                # It's a struct field access, e.g., p.x
                var_name = getattr(arg.value, 'id', None)
                if var_name in self.local_vars:
                    struct_type_name = self.local_vars[var_name]
                    struct_symbol = self.symbol_table.lookup(struct_type_name)
                    if struct_symbol and struct_symbol.type == 'struct':
                        field_name = arg.attr
                        if field_name in struct_symbol.fields:
                            arg_type = struct_symbol.fields[field_name]
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
            elif arg_type.startswith('ptr['):
                format_specifier = '%p' # Pointers are printed as memory addresses
            else:  # int
                format_specifier = '%d'
            
            self.current_code_list.append(f'{self._indent()}printf("{format_specifier}\\n", {expr_code});')
            return ""
        elif node.func.id == 'addr':
            return f'&{self.visit(node.args[0])}'
        elif node.func.id == 'deref':
            return f'(*{self.visit(node.args[0])})'
        elif node.func.id == 'assign':
            ptr = self.visit(node.args[0])
            val = self.visit(node.args[1])
            self.current_code_list.append(f'{self._indent()}*({ptr}) = {val};')
            return "" # assign is a statement, not an expression
        elif node.func.id == 'sizeof':
            type_str = node.args[0].value
            c_type = self._c_type_from_pyrinas_type(type_str)
            return f'sizeof({c_type})'
        elif node.func.id == 'malloc':
            size = self.visit(node.args[0])
            return f'malloc({size})'
        elif node.func.id == 'free':
            ptr = self.visit(node.args[0])
            self.current_code_list.append(f'{self._indent()}free({ptr});')
            return "" # free is a statement, not an expression
        elif node.func.id in ('Ok', 'Err'):
            # These are handled in visit_Return, here we just visit the value
            return self.visit(node.args[0])
        elif node.func.id in ('int', 'float', 'str', 'bool'):
            # Type conversion functions
            if len(node.args) != 1:
                raise TypeError(f"{node.func.id}() expects exactly one argument.")
            arg_expr = self.visit(node.args[0])
            # Convert to C-style type casts
            c_type = self._c_type_from_pyrinas_type(node.func.id)
            return f'({c_type}){arg_expr}'
        else:
            # Check if this is a struct constructor call
            struct_symbol = self.symbol_table.lookup(node.func.id)
            if struct_symbol and struct_symbol.type == 'struct':
                # This is a struct constructor - initialize with zero values
                return f'{{0}}'  # C struct zero initializer
            else:
                # Regular function call
                args_str = ', '.join([self.visit(arg) for arg in node.args])
                return f'{node.func.id}({args_str})'
            
    def visit_Return(self, node):
        if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', None) in ('Ok', 'Err'):
            call = node.value
            is_ok = call.func.id == 'Ok'
            val = self.visit(call.args[0])

            # This part is still simplified. We need to know the type of the value
            # to pick the right field in the union.
            # For now, we'll make a guess based on the AST node type.
            val_type = 'int'
            if isinstance(call.args[0], ast.Constant):
                if isinstance(call.args[0].value, str):
                    val_type = 'str'

            if is_ok:
                self.current_code_list.append(f'{self._indent()}return (Result){{ .type = OK, .value = {{ .int_val = {val} }} }};')
            else: # is_err
                self.current_code_list.append(f'{self._indent()}return (Result){{ .type = ERR, .value = {{ .str_val = {val} }} }};')
        else:
            return_val = self.visit(node.value)
            self.current_code_list.append(f'{self._indent()}return {return_val};')

    def _c_type_from_pyrinas_type(self, type_str):
        if type_str.startswith('ptr[') and type_str.endswith(']'):
            base_type = type_str[4:-1]
            return self._c_type_from_pyrinas_type(base_type) + '*'
        elif type_str.startswith('array[') and type_str.endswith(']'):
            # For function parameters, arrays are passed as pointers in C
            match = re.match(r'array\[(\w+),\s*(\d+)\]', type_str)
            if match:
                base_type = match.group(1)
                return self._c_type_from_pyrinas_type(base_type) + '*'
            else:
                raise TypeError(f"Invalid array type format: {type_str}")
        else:
            c_type = {'int': 'int', 'float': 'float', 'bool': 'int', 'str': 'char*', 'void': 'void'}.get(type_str)
            if c_type:
                return c_type
            # Assume it's a struct type if not a primitive
            return f'struct {type_str}'

    def _get_preceding_label(self, loop_node):
        # This is a bit of a hack. We need to find the label
        # that immediately precedes the loop in the AST.
        if hasattr(loop_node, 'parent'):
            body = loop_node.parent.body
            idx = body.index(loop_node)
            if idx > 0 and isinstance(body[idx - 1], ast.Expr) and isinstance(body[idx - 1].value, ast.Constant) and isinstance(body[idx - 1].value.value, str):
                return body[idx - 1].value.value
        return None

    def generate(self, tree):
        self.visit(tree)
        return '#include "pyrinas.h"\n\n' + '\n'.join(self.struct_definitions) + '\n\n' + '\n'.join(self.function_definitions) + '\n\n' + '\n'.join(self.main_code)