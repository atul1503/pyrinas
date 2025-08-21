import ast
import re

class CCodeGenerator(ast.NodeVisitor):
    def __init__(self, symbol_table, semantic_analyzer=None):
        self.main_code = []
        self.function_definitions = []
        self.struct_definitions = []
        self.symbol_table = symbol_table
        self.semantic_analyzer = semantic_analyzer
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
        # Get function symbol
        func_symbol = self.symbol_table.lookup(node.name)
        
        # Check if this is an external C function
        if func_symbol and hasattr(func_symbol, 'is_c_function') and func_symbol.is_c_function:
            # Skip generating definition for external C functions
            return
        
        if node.name == 'main':
            self.current_code_list = self.main_code
            self.main_code.append('int main() {')
        else:
            self.current_code_list = []
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
        class_name = node.name
        
        # Check if this class inherits from Enum
        is_enum = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'Enum':
                is_enum = True
                break
        
        if is_enum:
            # This is an enum - generate C enum definition
            self._generate_enum(node, class_name)
            return
        
        # Analyze the class to determine if it's an interface or struct
        has_fields = False
        has_method_implementations = False
        methods = {}
        
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                has_fields = True
            elif isinstance(stmt, ast.FunctionDef):
                method_name = stmt.name
                
                # Extract parameter types (skip 'self')
                param_types = []
                for arg in stmt.args.args[1:]:
                    if hasattr(arg.annotation, 'id'):
                        param_types.append(arg.annotation.id)
                    elif hasattr(arg.annotation, 'value'):
                        param_types.append(arg.annotation.value)
                
                # Extract return type
                return_type = None
                if stmt.returns:
                    if hasattr(stmt.returns, 'id'):
                        return_type = stmt.returns.id
                    elif hasattr(stmt.returns, 'value'):
                        return_type = stmt.returns.value
                
                methods[method_name] = (param_types, return_type)
                
                # Check if method has implementation
                if not (len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Pass)):
                    has_method_implementations = True
        
        if has_fields or has_method_implementations:
            # This is a struct - generate struct definition and method implementations
            self._generate_struct_with_methods(node, class_name, methods, has_method_implementations)
        else:
            # This is an interface - generate vtable typedef
            self._generate_interface_vtable(class_name, methods)

    def _generate_enum(self, node, enum_name):
        """Generate C enum definition"""
        self.struct_definitions.append(f'enum {enum_name} {{')
        
        # Parse enum members
        members = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                    member_name = stmt.targets[0].id
                    if isinstance(stmt.value, ast.Constant):
                        value = stmt.value.value
                        members.append(f'    {enum_name}_{member_name} = {value}')
        
        if members:
            # Add commas to all but the last member
            for i, member in enumerate(members):
                if i < len(members) - 1:
                    self.struct_definitions.append(member + ',')
                else:
                    self.struct_definitions.append(member)
        
        self.struct_definitions.append('};')
        self.struct_definitions.append('')  # Empty line for readability

    def _generate_interface_vtable(self, interface_name, methods):
        """Generate C vtable typedef for an interface"""
        # For simplicity, we won't generate vtables for now
        # Instead, we'll use direct method calls
        # This is a future enhancement for full polymorphism
        pass

    def _generate_struct_with_methods(self, node, struct_name, methods, has_implementations):
        """Generate C struct definition with method implementations"""
        
        self.struct_definitions.append(f'struct {struct_name} {{')
        
        # Add fields
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign):
                field_name = stmt.target.id
                # Handle both ast.Name and ast.Constant (string literal) annotations
                if isinstance(stmt.annotation, ast.Name):
                    field_type_name = stmt.annotation.id
                elif isinstance(stmt.annotation, ast.Constant) and isinstance(stmt.annotation.value, str):
                    field_type_name = stmt.annotation.value
                else:
                    field_type_name = 'int'  # Default fallback
                c_field_type = self._c_type_from_pyrinas_type(field_type_name)
                self.struct_definitions.append(f'    {c_field_type} {field_name};')
        
        self.struct_definitions.append('};')
        self.struct_definitions.append('')
        
        # Generate method implementations if this struct has them
        if has_implementations:
            self._generate_method_implementations(node, struct_name, methods)

    def _generate_method_implementations(self, node, struct_name, methods):
        """Generate C function implementations for struct methods"""
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and not (len(stmt.body) == 1 and isinstance(stmt.body[0], ast.Pass)):
                method_name = stmt.name
                
                # Generate method signature
                return_type = 'void'
                if stmt.returns:
                    if hasattr(stmt.returns, 'id'):
                        return_type = self._c_type_from_pyrinas_type(stmt.returns.id)
                    elif hasattr(stmt.returns, 'value') and stmt.returns.value is not None:
                        return_type = self._c_type_from_pyrinas_type(stmt.returns.value)
                
                # Parameters (self + others)
                params = [f'struct {struct_name}* self']
                for arg in stmt.args.args[1:]:  # Skip self
                    arg_type = 'int'  # Default
                    if hasattr(arg.annotation, 'id'):
                        arg_type = self._c_type_from_pyrinas_type(arg.annotation.id)
                    elif hasattr(arg.annotation, 'value'):
                        arg_type = self._c_type_from_pyrinas_type(arg.annotation.value)
                    params.append(f'{arg_type} {arg.arg}')
                
                params_str = ', '.join(params)
                
                # Generate function header
                func_name = f'{struct_name}_{method_name}'
                self.function_definitions.append(f'{return_type} {func_name}({params_str}) {{')
                
                # Generate function body
                old_indent = self.indent_level
                self.indent_level = 1
                old_code_list = self.current_code_list
                self.current_code_list = self.function_definitions
                
                for method_stmt in stmt.body:
                    self.visit(method_stmt)
                
                self.current_code_list = old_code_list
                self.indent_level = old_indent
                
                self.function_definitions.append('}')
                self.function_definitions.append('')

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
            elif annotation_name == 'Result':
                # Handle Result[success_type, error_type] annotations
                success_type_node = node.annotation.slice.elts[0]
                error_type_node = node.annotation.slice.elts[1]
                success_type = getattr(success_type_node, 'id', None)
                error_type = getattr(error_type_node, 'id', None)
                type_name = f'Result[{success_type},{error_type}]'
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
        # Check if this is enum member access (EnumName.MEMBER)
        if isinstance(node.value, ast.Name):
            enum_name = node.value.id
            # Check if this is an enum type (we can't easily access semantic info here,
            # so we'll use a naming convention - this is a simplification)
            # For now, we'll assume if it's a simple Name.attr pattern, it might be an enum
            # The semantic analyzer has already validated this is correct
            if enum_name[0].isupper():  # Enum names start with uppercase by convention
                member_name = node.attr
                return f'{enum_name}_{member_name}'
        
        var = self.visit(node.value)
        attr = node.attr
        
        # Use -> for pointer access (when var is 'self' in methods)
        if var == 'self':
            return f'{var}->{attr}'
        else:
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
        if isinstance(node.op, ast.Not):
            return f'(!{self.visit(node.operand)})'
        elif isinstance(node.op, ast.USub):
            return f'(-{self.visit(node.operand)})'
        elif isinstance(node.op, ast.UAdd):
            return f'(+{self.visit(node.operand)})'
        else:
            return self.visit(node.operand)

    def visit_Call(self, node):
        # Check if this is a method call (obj.method()) or function call (func())
        if isinstance(node.func, ast.Attribute):
            # Method call
            return self._visit_method_call(node)
        elif isinstance(node.func, ast.Name):
            # Function call
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
            elif node.func.id in ('is_ok', 'is_err'):
                arg_expr = self.visit(node.args[0])
                return f'{node.func.id}({arg_expr})'
            elif node.func.id.startswith('unwrap_or_'):
                result_expr = self.visit(node.args[0])
                default_expr = self.visit(node.args[1])
                return f'{node.func.id}({result_expr}, {default_expr})'
            elif node.func.id.startswith('unwrap_'):
                arg_expr = self.visit(node.args[0])
                return f'{node.func.id}({arg_expr})'
            elif node.func.id.startswith('expect_'):
                result_expr = self.visit(node.args[0])
                message_expr = self.visit(node.args[1])
                return f'{node.func.id}({result_expr}, {message_expr})'
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
        else:
            raise NotImplementedError(f"Unsupported function call type: {type(node.func).__name__}")

    def _visit_method_call(self, node):
        """Generate C code for method calls (obj.method())"""
        obj_node = node.func.value
        method_name = node.func.attr
        
        # Get the object expression
        obj_expr = self.visit(obj_node)
        
        # Get arguments
        args = [self.visit(arg) for arg in node.args]
        
        # For now, generate direct method calls using struct_method naming convention
        # In the future, this could use vtables for interface dispatch
        if isinstance(obj_node, ast.Name):
            obj_name = obj_node.id
            if obj_name in self.local_vars:
                obj_type = self.local_vars[obj_name]
                # Generate method call like: Rectangle_draw(&rect, args...)
                args_str = ', '.join([f'&{obj_expr}'] + args)
                return f'{obj_type}_{method_name}({args_str})'
        
        # Fallback: assume direct method call
        args_str = ', '.join([f'&{obj_expr}'] + args)
        return f'{method_name}({args_str})'
            
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
        elif type_str.startswith('Result[') and type_str.endswith(']'):
            # Result types map to the C Result struct
            return 'Result'
        else:
            c_type = {'int': 'int', 'float': 'float', 'bool': 'int', 'str': 'char*', 'void': 'void'}.get(type_str)
            if c_type:
                return c_type
            
            # Check if it's a user-defined type (enum or struct)
            symbol = self.symbol_table.lookup(type_str)
            if symbol:
                if symbol.type == 'enum':
                    return f'enum {type_str}'
                elif symbol.type == 'struct':
                    return f'struct {type_str}'
            
            # Assume it's a struct type if not found (backward compatibility)
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
        
        # Build the C code
        c_code = []
        
        # Add standard pyrinas header
        c_code.append('#include "pyrinas.h"')
        
        # Add C interop headers if available
        if self.semantic_analyzer and hasattr(self.semantic_analyzer, 'c_includes'):
            for header in sorted(self.semantic_analyzer.c_includes):
                c_code.append(f'#include <{header}>')
        
        c_code.append('')  # Empty line
        
        # Add struct definitions
        if self.struct_definitions:
            c_code.extend(self.struct_definitions)
            c_code.append('')
        
        # Add function definitions
        if self.function_definitions:
            c_code.extend(self.function_definitions)
            c_code.append('')
        
        # Add main code
        c_code.extend(self.main_code)
        
        return '\n'.join(c_code)