from abc import ABC, abstractmethod
from typing import List, Any


class ASTNode(ABC):
    @abstractmethod
    def __repr__(self):
        pass


class Program(ASTNode):
    def __init__(self, declarations: List[ASTNode]):
        self.declarations = declarations
    
    def __repr__(self):
        return f"Program({self.declarations})"


class FunctionDecl(ASTNode):
    def __init__(self, name: str, params: List[str], body: 'Compound'):
        self.name = name
        self.params = params
        self.body = body
    
    def __repr__(self):
        return f"FunctionDecl({self.name}, {self.params}, {self.body})"


class Compound(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements
    
    def __repr__(self):
        return f"Compound({self.statements})"


class VarDecl(ASTNode):
    def __init__(self, name: str, value: Any = None):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"VarDecl({self.name}, {self.value})"


class Assignment(ASTNode):
    def __init__(self, name: str, value: 'Expr'):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


class Return(ASTNode):
    def __init__(self, value: 'Expr'):
        self.value = value
    
    def __repr__(self):
        return f"Return({self.value})"


class If(ASTNode):
    def __init__(self, condition: 'Expr', then_branch: ASTNode, else_branch: ASTNode = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"


class While(ASTNode):
    def __init__(self, condition: 'Expr', body: ASTNode):
        self.condition = condition
        self.body = body
    
    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class For(ASTNode):
    def __init__(self, init: ASTNode, condition: 'Expr', update: ASTNode, body: ASTNode):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body
    
    def __repr__(self):
        return f"For({self.init}, {self.condition}, {self.update}, {self.body})"


class Expr(ABC):
    @abstractmethod
    def __repr__(self):
        pass


class BinaryOp(Expr):
    def __init__(self, op: str, left: Expr, right: Expr):
        self.op = op
        self.left = left
        self.right = right
    
    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


class UnaryOp(Expr):
    def __init__(self, op: str, operand: Expr):
        self.op = op
        self.operand = operand
    
    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class Var(Expr):
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Var({self.name})"


class Number(Expr):
    def __init__(self, value: int):
        self.value = value
    
    def __repr__(self):
        return f"Number({self.value})"


class FunctionCall(Expr):
    def __init__(self, name: str, args: List[Expr]):
        self.name = name
        self.args = args
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"
