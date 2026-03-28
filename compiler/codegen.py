from typing import Dict, List, Tuple, Optional, Set
from ast import *
from symbol_table import SymbolTable, FunctionTable


class LabelManager:
    def __init__(self):
        self.counter = 0
        self.labels_used = set()
    
    def new_label(self, prefix: str = "lbl") -> str:
        base = f"{prefix}{self.counter}"
        label = base
        while label in self.labels_used:
            self.counter += 1
            label = f"{prefix}{self.counter}"
        self.labels_used.add(label)
        self.counter += 1
        return label


COND_MAP = {
    '==': '=',
    '!=': '!=',
    '<': '<',
    '>': '>',
    '<=': '<=',
    '>=': '>=',
}


SAVED_REGS = ["r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11"]


class CodeGen:
    def __init__(self):
        self.labels = LabelManager()
        self.output: List[str] = []
        self.symbol_table = SymbolTable()
        self.function_table = FunctionTable()
        self.current_function: Optional[FunctionInfo] = None
        self.label_manager = LabelManager()
    
    def emit(self, line: str = ""):
        self.output.append(line)
    
    def gen(self, node: ASTNode, skip_final_return: bool = False) -> str:
        if isinstance(node, Program):
            return self.gen_program(node)
        elif isinstance(node, FunctionDecl):
            return self.gen_function(node)
        elif isinstance(node, Compound):
            return self.gen_compound(node, skip_final_return)
        elif isinstance(node, VarDecl):
            return self.gen_var_decl(node)
        elif isinstance(node, Assignment):
            return self.gen_assignment(node)
        elif isinstance(node, Return):
            return self.gen_return(node)
        elif isinstance(node, If):
            return self.gen_if(node)
        elif isinstance(node, While):
            return self.gen_while(node)
        elif isinstance(node, For):
            return self.gen_for(node)
        elif isinstance(node, Expr):
            return self.gen_expr(node)
        return ""
    
    def gen_program(self, node: Program) -> str:
        self.emit("; ===== GENERATED CODE =====")
        self.emit("")
        
        main_func = None
        other_funcs = []
        
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                if decl.name == "main":
                    main_func = decl
                else:
                    other_funcs.append(decl)
                self.function_table.define(decl.name, decl.params, [])
        
        if main_func:
            self.gen(main_func)
        
        for func in other_funcs:
            self.gen(func)
        
        return "\n".join(self.output)
    
    def gen_function(self, node: FunctionDecl):
        self.emit(f"{node.name}:")
        
        self.symbol_table = SymbolTable()
        existing = self.function_table.lookup(node.name)
        if existing:
            self.current_function = existing
        else:
            self.current_function = self.function_table.define(node.name, node.params, [])
        self.current_function.symbol_table = self.symbol_table
        
        for i, param in enumerate(node.params):
            symbol = self.symbol_table.define(param)
            symbol.offset = i * 2
        
        local_vars = []
        for stmt in node.body.statements if isinstance(node.body, Compound) else [node.body]:
            if isinstance(stmt, VarDecl):
                symbol = self.symbol_table.define(stmt.name)
                symbol.offset = len(node.params) * 2 + len(local_vars) * 2
                local_vars.append(stmt.name)
        
        stmts = node.body.statements if isinstance(node.body, Compound) else [node.body]
        has_return = stmts and isinstance(stmts[-1], Return)
        
        if has_return:
            for stmt in stmts[:-1]:
                self.gen(stmt)
            self.gen(stmts[-1])
        else:
            for stmt in stmts:
                self.gen(stmt)
            if node.name == "main":
                self.emit("    stop")
            else:
                self.emit("    ret")
        
        self.emit("")
    
    def gen_compound(self, node: Compound, skip_final_return: bool = False):
        stmts = node.statements
        if skip_final_return and stmts and isinstance(stmts[-1], Return):
            stmts = stmts[:-1]
        for stmt in stmts:
            self.gen(stmt)
    
    def gen_var_decl(self, node: VarDecl):
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            symbol = self.symbol_table.define(node.name)
        
        if node.value:
            result = self.gen_expr(node.value)
            self.emit(f"    stso {result}, {symbol.offset}")
    
    def gen_assignment(self, node: Assignment):
        symbol = self.symbol_table.lookup(node.name)
        if symbol is None:
            raise Exception(f"Undefined variable: {node.name}")
        
        result = self.gen_expr(node.value)
        self.emit(f"    stso {result}, {symbol.offset}")
    
    def gen_return(self, node: Return):
        result = self.gen_expr(node.value)
        if result != "r12":
            self.emit(f"    add r12, {result}, r0")
        self.emit("    ret")
    
    def gen_if(self, node: If):
        end_label = self.labels.new_label("endif")
        else_label = self.labels.new_label("else") if node.else_branch else None
        
        result = self.gen_expr(node.condition)
        
        jump_cond = self.get_jump_cond(node.condition)
        jump_cond = self.invert_cond(jump_cond)
        
        if else_label:
            self.emit(f"    jump {jump_cond}, OF({else_label})")
            self.gen(node.then_branch)
            self.emit(f"    jump OF({end_label})")
            self.emit(f"{else_label}:")
            self.gen(node.else_branch)
        else:
            self.emit(f"    jump {jump_cond}, OF({end_label})")
            self.gen(node.then_branch)
        
        self.emit(f"{end_label}:")
    
    def gen_while(self, node: While):
        start_label = self.labels.new_label("while")
        end_label = self.labels.new_label("endwhile")
        
        self.emit(f"{start_label}:")
        
        result = self.gen_expr(node.condition)
        jump_cond = self.get_jump_cond(node.condition)
        jump_cond = self.invert_cond(jump_cond)
        self.emit(f"    jump {jump_cond}, OF({end_label})")
        
        self.gen(node.body)
        self.emit(f"    jump OF({start_label})")
        self.emit(f"{end_label}:")
    
    def gen_for(self, node: For):
        start_label = self.labels.new_label("for")
        end_label = self.labels.new_label("endfor")
        
        if isinstance(node.init, VarDecl):
            self.gen_var_decl(node.init)
        elif isinstance(node.init, Assignment):
            self.gen_assignment(node.init)
        
        self.emit(f"{start_label}:")
        
        result = self.gen_expr(node.condition)
        jump_cond = self.get_jump_cond(node.condition)
        jump_cond = self.invert_cond(jump_cond)
        self.emit(f"    jump {jump_cond}, OF({end_label})")
        
        self.gen(node.body)
        
        if isinstance(node.update, Assignment):
            self.gen_assignment(node.update)
        
        self.emit(f"    jump OF({start_label})")
        self.emit(f"{end_label}:")
    
    def gen_expr(self, node: Expr) -> str:
        if isinstance(node, Number):
            return self.load_immediate(node.value)
        elif isinstance(node, Var):
            return self.load_var(node.name)
        elif isinstance(node, BinaryOp):
            return self.gen_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.gen_unary_op(node)
        elif isinstance(node, FunctionCall):
            return self.gen_function_call(node)
        return "r0"
    
    def load_immediate(self, value: int) -> str:
        self.emit(f"    ldi r14, {value}")
        return "r14"
    
    def load_var(self, name: str) -> str:
        symbol = self.symbol_table.lookup(name)
        if symbol is None:
            raise Exception(f"Undefined variable: {name}")
        
        self.emit(f"    ldso r14, {symbol.offset}")
        return "r14"
    
    def gen_binary_op(self, node: BinaryOp) -> str:
        left = self.gen_expr(node.left)
        
        if node.op == '*':
            self.emit(f"    add r13, {left}, r0")
            right = self.gen_expr(node.right)
            self.emit(f"    push {right}")
            self.emit(f"    push r13")
            self.emit(f"    ldi r14, hi(mult)")
            self.emit(f"    ldi r15, lo(mult)")
            self.emit(f"    call r14, r15")
            self.emit(f"    pop r0")
            self.emit(f"    pop r0")
            return "r12"
        elif node.op == '/':
            self.emit(f"    push {left}")
            right = self.gen_expr(node.right)
            self.emit(f"    push {right}")
            self.emit(f"    ldi r14, hi(div)")
            self.emit(f"    ldi r15, lo(div)")
            self.emit(f"    call r14, r15")
            self.emit(f"    pop r0")
            self.emit(f"    pop r0")
            return "r12"
        elif node.op == '%':
            self.emit(f"    push {left}")
            right = self.gen_expr(node.right)
            self.emit(f"    push {right}")
            self.emit(f"    ldi r14, hi(mod)")
            self.emit(f"    ldi r15, lo(mod)")
            self.emit(f"    call r14, r15")
            self.emit(f"    pop r0")
            self.emit(f"    pop r0")
            return "r12"
        else:
            self.emit(f"    push {left}")
            right = self.gen_expr(node.right)
            self.emit(f"    pop r15")
            
            if node.op == '+':
                self.emit(f"    add r12, r15, {right}")
                return "r12"
            elif node.op == '-':
                self.emit(f"    sec")
                self.emit(f"    subc r12, r15, {right}")
                return "r12"
            elif node.op in ('==', '!=', '<', '>', '<=', '>='):
                self.emit(f"    sec")
                self.emit(f"    subc r14, r15, {right}")
                return "r14"
        
        return "r0"
    
    def gen_unary_op(self, node: UnaryOp) -> str:
        operand = self.gen_expr(node.operand)
        if node.op == '-':
            self.emit(f"    subc r14, r0, {operand}")
            self.emit(f"    sec")
            self.emit(f"    subc r14, r0, r14")
            return "r14"
        return operand
    
    def gen_mult(self, left_node, right_node) -> str:
        left = self.gen_expr(left_node)
        right = self.gen_expr(right_node)
        self.emit(f"    push {left}")
        self.emit(f"    push {right}")
        self.emit(f"    ldi r14, hi(mult)")
        self.emit(f"    ldi r15, lo(mult)")
        self.emit(f"    call r14, r15")
        self.emit(f"    pop r0")
        self.emit(f"    pop r0")
        return "r12"
    
    def gen_div(self, left_node, right_node) -> str:
        left = self.gen_expr(left_node)
        right = self.gen_expr(right_node)
        self.emit(f"    push {left}")
        self.emit(f"    push {right}")
        self.emit(f"    ldi r14, hi(div)")
        self.emit(f"    ldi r15, lo(div)")
        self.emit(f"    call r14, r15")
        self.emit(f"    pop r0")
        self.emit(f"    pop r0")
        return "r12"
    
    def gen_mod(self, left_node, right_node) -> str:
        left = self.gen_expr(left_node)
        right = self.gen_expr(right_node)
        self.emit(f"    push {left}")
        self.emit(f"    push {right}")
        self.emit(f"    ldi r14, hi(mod)")
        self.emit(f"    ldi r15, lo(mod)")
        self.emit(f"    call r14, r15")
        self.emit(f"    pop r0")
        self.emit(f"    pop r0")
        return "r12"
    
    def gen_compare(self, op: str, left: str, right: str) -> str:
        self.emit(f"    sec")
        self.emit(f"    subc r14, {left}, {right}")
        return "r14"
    
    def gen_function_call(self, node: FunctionCall) -> str:
        func = self.function_table.lookup(node.name)
        if func is None:
            raise Exception(f"Undefined function: {node.name}")
        
        for arg in node.args:
            result = self.gen_expr(arg)
            self.emit(f"    push {result}")
        
        self.emit(f"    ldi r14, hi({node.name})")
        self.emit(f"    ldi r15, lo({node.name})")
        self.emit(f"    call r14, r15")
        
        num_args = len(node.args)
        for _ in range(num_args):
            self.emit(f"    pop r0")
        
        return "r12"
    
    def get_jump_cond(self, node: Expr) -> str:
        if isinstance(node, BinaryOp) and node.op in COND_MAP:
            return COND_MAP[node.op]
        if isinstance(node, Var):
            return '!='
        return '='
    
    def invert_cond(self, cond: str) -> str:
        invert_map = {
            '=': '!=',
            '!=': '=',
            '<': '>=',
            '>': '<=',
            '<=': '>',
            '>=': '<',
        }
        return invert_map.get(cond, cond)


def generate(node: ASTNode) -> str:
    codegen = CodeGen()
    return codegen.gen(node)
