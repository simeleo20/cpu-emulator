from typing import Dict, Optional, List, Any


class Symbol:
    def __init__(self, name: str, var_type: str = "int", register: Optional[str] = None, offset: Optional[int] = None):
        self.name = name
        self.var_type = var_type
        self.register = register
        self.offset = offset


class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent
        self.next_register = 1
        self.next_stack_offset = 4
    
    def define(self, name: str, var_type: str = "int") -> Symbol:
        if name in self.symbols:
            raise Exception(f"Variable '{name}' already defined")
        
        if self.next_register <= 9:
            reg = f"r{self.next_register}"
            self.next_register += 1
            symbol = Symbol(name, var_type, register=reg)
        else:
            offset = self.next_stack_offset
            self.next_stack_offset += 2
            symbol = Symbol(name, var_type, offset=offset)
        
        self.symbols[name] = symbol
        return symbol
    
    def lookup(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def get_register(self, name: str) -> str:
        symbol = self.lookup(name)
        if symbol is None:
            raise Exception(f"Undefined variable '{name}'")
        if symbol.register is None:
            raise Exception(f"Variable '{name}' is on stack, need different access")
        return symbol.register
    
    def get_offset(self, name: str) -> int:
        symbol = self.lookup(name)
        if symbol is None:
            raise Exception(f"Undefined variable '{name}'")
        if symbol.offset is None:
            raise Exception(f"Variable '{name}' is in register, need different access")
        return symbol.offset
    
    def is_defined(self, name: str) -> bool:
        return self.lookup(name) is not None
    
    def create_child(self) -> 'SymbolTable':
        child = SymbolTable(self)
        return child
    
    def get_all_variables(self) -> List[str]:
        vars = list(self.symbols.keys())
        if self.parent:
            vars.extend(self.parent.get_all_variables())
        return vars


class FunctionInfo:
    def __init__(self, name: str, params: List[str], local_vars: List[str]):
        self.name = name
        self.params = params
        self.local_vars = local_vars
        self.symbol_table: Optional[SymbolTable] = None


class FunctionTable:
    def __init__(self):
        self.functions: Dict[str, FunctionInfo] = {}
    
    def define(self, name: str, params: List[str], local_vars: List[str]) -> FunctionInfo:
        if name in self.functions:
            raise Exception(f"Function '{name}' already defined")
        info = FunctionInfo(name, params, local_vars)
        self.functions[name] = info
        return info
    
    def lookup(self, name: str) -> Optional[FunctionInfo]:
        return self.functions.get(name)
    
    def get_current_function(self) -> Optional[FunctionInfo]:
        return None
