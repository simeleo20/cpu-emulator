from typing import List, Optional
from lexer import Lexer, Token, TokenType
from ast import *


class ParserError(Exception):
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"{message} at line {token.line}, column {token.column}")
        else:
            super().__init__(message)


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message: str):
        raise ParserError(message, self.current_token)
    
    def advance(self):
        self.current_token = self.lexer.get_next_token()
    
    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.advance()
        else:
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name}")
    
    def parse(self) -> Program:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type in (TokenType.INT, TokenType.VOID):
                declarations.append(self.parse_function())
            else:
                self.error(f"Unexpected token: {self.current_token.type.name}")
        return Program(declarations)
    
    def parse_function(self) -> FunctionDecl:
        if self.current_token.type == TokenType.VOID:
            self.advance()
            return_type = "void"
        else:
            self.eat(TokenType.INT)
            return_type = "int"
        
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        self.eat(TokenType.LPAREN)
        
        params = []
        if self.current_token.type == TokenType.INT:
            params = self.parse_params()
        
        self.eat(TokenType.RPAREN)
        body = self.parse_block()
        
        return FunctionDecl(name, params, body)
    
    def parse_params(self) -> List[str]:
        params = []
        while True:
            self.eat(TokenType.INT)
            param = self.current_token.value
            params.append(param)
            self.eat(TokenType.IDENT)
            if self.current_token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        return params
    
    def parse_block(self) -> Compound:
        self.eat(TokenType.LBRACE)
        statements = []
        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.parse_statement())
        self.eat(TokenType.RBRACE)
        return Compound(statements)
    
    def parse_statement(self) -> ASTNode:
        if self.current_token.type == TokenType.INT:
            return self.parse_var_decl()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return()
        elif self.current_token.type == TokenType.IDENT:
            if self.lexer.peek() == '=':
                return self.parse_assignment()
            else:
                return self.parse_expr_statement()
        elif self.current_token.type == TokenType.SEMI:
            self.advance()
            return Compound([])
        else:
            return self.parse_expr_statement()
    
    def parse_var_decl(self) -> VarDecl:
        self.eat(TokenType.INT)
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        value = None
        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()
        self.eat(TokenType.SEMI)
        return VarDecl(name, value)
    
    def parse_assignment(self) -> Assignment:
        name = self.current_token.value
        self.eat(TokenType.IDENT)
        self.eat(TokenType.ASSIGN)
        value = self.parse_expression()
        self.eat(TokenType.SEMI)
        return Assignment(name, value)
    
    def parse_if(self) -> If:
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        then_branch = self.parse_block()
        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            else_branch = self.parse_block()
        return If(condition, then_branch, else_branch)
    
    def parse_while(self) -> While:
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        body = self.parse_block()
        return While(condition, body)
    
    def parse_for(self) -> For:
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        
        if self.current_token.type == TokenType.INT:
            init = self.parse_var_decl()
        elif self.current_token.type == TokenType.IDENT:
            init = self.parse_assignment()
        else:
            self.eat(TokenType.SEMI)
            init = Compound([])
        
        condition = self.parse_expression()
        self.eat(TokenType.SEMI)
        
        update_name = self.current_token.value
        self.eat(TokenType.IDENT)
        self.eat(TokenType.ASSIGN)
        update_expr = self.parse_expression()
        update = Assignment(update_name, update_expr)
        
        self.eat(TokenType.RPAREN)
        body = self.parse_block()
        
        return For(init, condition, update, body)
    
    def parse_return(self) -> Return:
        self.eat(TokenType.RETURN)
        value = self.parse_expression()
        self.eat(TokenType.SEMI)
        return Return(value)
    
    def parse_expr_statement(self) -> ASTNode:
        expr = self.parse_expression()
        self.eat(TokenType.SEMI)
        return expr
    
    def parse_expression(self) -> Expr:
        return self.parse_comparison()
    
    def parse_comparison(self) -> Expr:
        left = self.parse_addition()
        
        while self.current_token.type in (TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE):
            op = self.current_token.value
            self.advance()
            right = self.parse_addition()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_addition(self) -> Expr:
        left = self.parse_multiplication()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_multiplication(self) -> Expr:
        left = self.parse_unary()
        
        while self.current_token.type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(op, left, right)
        
        return left
    
    def parse_unary(self) -> Expr:
        if self.current_token.type == TokenType.MINUS:
            self.advance()
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        return self.parse_primary()
    
    def parse_primary(self) -> Expr:
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return Number(value)
        
        if self.current_token.type == TokenType.IDENT:
            name = self.current_token.value
            self.advance()
            
            if self.current_token.type == TokenType.LPAREN:
                self.advance()
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.eat(TokenType.RPAREN)
                return FunctionCall(name, args)
            
            return Var(name)
        
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return expr
        
        self.error(f"Unexpected token in expression: {self.current_token.type.name}")


def parse(text: str) -> Program:
    lexer = Lexer(text)
    parser = Parser(lexer)
    return parser.parse()
