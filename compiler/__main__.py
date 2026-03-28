#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from codegen import CodeGen


def compile_c(source: str) -> str:
    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse()
    
    codegen = CodeGen()
    code = codegen.gen(ast)
    
    return code


def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source.c> [output.asm]")
        print("  or:  echo 'int main() { return 42; }' | python compiler.py")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        source = sys.stdin.read()
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = compile_c(source)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"Compiled to {output_file}")
        else:
            print(result)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
