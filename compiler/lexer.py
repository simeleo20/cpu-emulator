import re
from enum import Enum, auto
from typing import List, Tuple


class TokenType(Enum):
    INT = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    VOID = auto()
    IDENT = auto()
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()
    ASSIGN = auto()
    SEMI = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    EOF = auto()


RESERVED_KEYWORDS = {
    'int': TokenType.INT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'return': TokenType.RETURN,
    'void': TokenType.VOID,
}


class Token:
    def __init__(self, type: TokenType, value, line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r})"


class LexerError(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if self.text else None
    
    def error(self, message: str):
        raise LexerError(message, self.line, self.column)
    
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            if self.current_char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.current_char = self.text[self.pos]
    
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\r\n':
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    break
                self.advance()
    
    def read_number(self):
        result = ''
        start_col = self.column
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, int(result), self.line, start_col)
    
    def read_ident(self):
        result = ''
        start_col = self.column
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        token_type = RESERVED_KEYWORDS.get(result, TokenType.IDENT)
        return Token(token_type, result, self.line, start_col)
    
    def read_operator(self):
        start_col = self.column
        c = self.current_char
        
        if c == '+':
            self.advance()
            return Token(TokenType.PLUS, '+', self.line, start_col)
        elif c == '-':
            self.advance()
            return Token(TokenType.MINUS, '-', self.line, start_col)
        elif c == '*':
            self.advance()
            return Token(TokenType.STAR, '*', self.line, start_col)
        elif c == '/':
            self.advance()
            return Token(TokenType.SLASH, '/', self.line, start_col)
        elif c == '%':
            self.advance()
            return Token(TokenType.PERCENT, '%', self.line, start_col)
        
        elif c == '=':
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.EQ, '==', self.line, start_col)
            return Token(TokenType.ASSIGN, '=', self.line, start_col)
        
        elif c == '!':
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.NEQ, '!=', self.line, start_col)
            self.error("Unexpected character '!' (did you mean '!='?)")
        
        elif c == '<':
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.LTE, '<=', self.line, start_col)
            return Token(TokenType.LT, '<', self.line, start_col)
        
        elif c == '>':
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.GTE, '>=', self.line, start_col)
            return Token(TokenType.GT, '>', self.line, start_col)
        
        elif c == ';':
            self.advance()
            return Token(TokenType.SEMI, ';', self.line, start_col)
        
        elif c == ',':
            self.advance()
            return Token(TokenType.COMMA, ',', self.line, start_col)
        
        elif c == '(':
            self.advance()
            return Token(TokenType.LPAREN, '(', self.line, start_col)
        
        elif c == ')':
            self.advance()
            return Token(TokenType.RPAREN, ')', self.line, start_col)
        
        elif c == '{':
            self.advance()
            return Token(TokenType.LBRACE, '{', self.line, start_col)
        
        elif c == '}':
            self.advance()
            return Token(TokenType.RBRACE, '}', self.line, start_col)
        
        self.error(f"Unexpected character '{c}'")
    
    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char in ' \t\r\n':
                self.skip_whitespace()
                continue
            
            if self.current_char == '/' and self.peek() in ['/', '*']:
                self.skip_comment()
                continue
            
            if self.current_char.isdigit():
                return self.read_number()
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_ident()
            
            return self.read_operator()
        
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


def tokenize(text: str) -> List[Token]:
    lexer = Lexer(text)
    return lexer.tokenize()
