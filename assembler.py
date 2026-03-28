import sys
import re

class AssemblerError(Exception):
    pass

class Assembler:
    def __init__(self):
        self.labels = {}
        self.defines = {}
        self.default_defines = {
            "BLACK": 0,
            "BLUE": 4,
            "GREEN": 2,
            "CYAN": 6,
            "RED": 1,
            "MAGENTA": 5,
            "YELLOW": 3,
            "WHITE": 7,
            "COND_ALWAYS": 0,
            "COND_OVERFLOW": 1,
            "COND_NEGATIVE": 2,
            "COND_ZERO": 3,
        }
        self.opcodes = {
            "nop": (0x0, 0), "add": (0x1, 3), "addc": (0x2, 3), "subc": (0x3, 3),
            "addi": (0x4, 3), "subi": (0x5, 3), "jump": (0x6, 3), "ldi": (0x7, 2),
            "ld": (0x8, 3), "st": (0x9, 3), "screen": (0xA, 3), "ldso": (0xB, 2),
            "stso": (0xC, 2), "and": (0xD, 3), "or": (0xE, 3), "subop": (0xF, 0)
        }
        self.subopcodes = {
            "push": (0x0, 1), "pop": (0x1, 1), "sec": (0x2, 0), "ret": (0x3, 0),
            "call": (0x4, 2), "shl": (0x5, 2), "shr": (0x6, 2), "not": (0x7, 2), 
            "cls": (0x8, 1), "stop": (0x9, 0)
        }
        self.current_section = "code"
        self.code_address = 0
        self.data_address = 0x8000
        self.code_binary = []
        self.data_binary = []
        self.data_section_start = 0

    def apply_defines(self, line):
        for name, value in self.defines.items():
            pattern = r'\b' + re.escape(name) + r'\b'
            line = re.sub(pattern, str(value), line)
        return line

    def process_defines(self, filename):
        defines = dict(self.default_defines)
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                cleaned = self.clean_line(line)
                if not cleaned:
                    continue
                if cleaned.startswith('#define'):
                    parts = cleaned.split(None, 2)
                    if len(parts) < 3:
                        raise AssemblerError(f"#define richiede nome e valore alla riga {line_num}")
                    name = parts[1]
                    value = parts[2]
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                        raise AssemblerError(f"Nome '#define' '{name}' non valido alla riga {line_num}")
                    if name in self.default_defines:
                        raise AssemblerError(f"#define '{name}' è gia una costante predefinita")
                    if name in defines:
                        raise AssemblerError(f"#define '{name}' già definito alla riga {line_num}")
                    
                    value_upper = value.strip().upper()
                    if value_upper.startswith('R') and len(value_upper) >= 2:
                        try:
                            reg_num = int(value_upper[1:])
                            if 0 <= reg_num <= 15:
                                defines[name] = f'R{reg_num}'
                                continue
                        except ValueError:
                            pass
                    
                    try:
                        val = int(value, 0)
                        defines[name] = val
                    except ValueError:
                        if value in defines:
                            defines[name] = defines[value]
                        else:
                            raise AssemblerError(f"Valore '#define {name} {value}' non valido alla riga {line_num}")
        return defines

    def clean_line(self, line):
        line = re.sub(r';.*', '', line)
        return line.strip()

    def reg(self, s): 
        s = s.strip()
        if s.upper() in {x.upper() for x in self.defines.values() if isinstance(x, str)}:
            for name, value in self.defines.items():
                if isinstance(value, str) and value.upper() == s.upper():
                    s = value
                    break
        
        s = s.strip().upper()
        if not s.startswith('R'):
            raise AssemblerError(f"Registro '{s}' non valido (deve iniziare con r)")
        try:
            val = int(s[1:])
            if val < 0 or val > 15:
                raise AssemblerError(f"Registro {s} non valido (deve essere r0-r15)")
            return val
        except ValueError:
            raise AssemblerError(f"Registro '{s}' non valido")
    
    def imm(self, s):
        s = s.strip()
        if s.startswith("HI("):
            if not s.endswith(")"):
                raise AssemblerError(f"HI() richiede parentesi di chiusura: {s}")
            label = s[3:-1]
            if label not in self.labels:
                raise AssemblerError(f"Label '{label}' non definita per HI()")
            return (self.labels[label] >> 8) & 0xFF
        if s.startswith("LO("):
            if not s.endswith(")"):
                raise AssemblerError(f"LO() richiede parentesi di chiusura: {s}")
            label = s[3:-1]
            if label not in self.labels:
                raise AssemblerError(f"Label '{label}' non definita per LO()")
            return self.labels[label] & 0xFF
        try:
            return int(s, 0)
        except ValueError:
            raise AssemblerError(f"Valore immediato '{s}' non valido")

    def handle_directive(self, directive, args, line_num):
        directive = directive.lower()
        
        if directive == ".code":
            if self.current_section != "code":
                self.current_section = "code"
            return True
            
        elif directive == ".data":
            if self.current_section != "data":
                self.data_section_start = len(self.data_binary)
                self.current_section = "data"
            return True
            
        elif directive == ".byte":
            if not args:
                raise AssemblerError(f"'.byte' richiede almeno un valore alla riga {line_num}")
            values = [v.strip() for v in args.split(',')]
            for val_str in values:
                try:
                    val = int(val_str, 0)
                except ValueError:
                    raise AssemblerError(f"Valore '{val_str}' non valido per '.byte' alla riga {line_num}")
                if val < -128 or val > 255:
                    raise AssemblerError(f"Valore '{val}' fuori range per '.byte' (-128..255) alla riga {line_num}")
                self.data_binary.append(val & 0xFF)
                self.data_address += 1
            return True
            
        elif directive == ".space":
            if not args:
                raise AssemblerError(f"'.space' richiede una dimensione alla riga {line_num}")
            try:
                count = int(args.strip(), 0)
            except ValueError:
                raise AssemblerError(f"Dimensione '{args}' non valida per '.space' alla riga {line_num}")
            if count <= 0 or count > 65535:
                raise AssemblerError(f"Dimensione {count} non valida per '.space' (1..65535) alla riga {line_num}")
            for _ in range(count):
                self.data_binary.append(0)
                self.data_address += 1
            return True
            
        return False

    def assemble_file(self, filename):
        self.defines = self.process_defines(filename)
        raw_lines = []
        
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                cleaned = self.clean_line(line)
                if not cleaned:
                    continue
                
                if cleaned.startswith('#define'):
                    continue
                
                cleaned = self.apply_defines(cleaned)
                
                if ':' in cleaned:
                    colon_pos = cleaned.index(':')
                    label_part = cleaned[:colon_pos]
                    rest = cleaned[colon_pos+1:].strip()
                    
                    if not label_part:
                        raise AssemblerError(f"Label vuota alla riga {line_num}")
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', label_part):
                        raise AssemblerError(f"Label '{label_part}' non valida alla riga {line_num}")
                    
                    if self.current_section == "code":
                        if label_part in self.labels:
                            raise AssemblerError(f"Label '{label_part}' già definita alla riga {line_num}")
                        self.labels[label_part] = self.code_address
                    else:
                        if label_part in self.labels:
                            raise AssemblerError(f"Label '{label_part}' già definita alla riga {line_num}")
                        self.labels[label_part] = self.data_address
                    
                    if rest:
                        if rest.startswith('.'):
                            parts = rest.split(None, 1)
                            directive = parts[0]
                            args = parts[1] if len(parts) > 1 else ""
                            if not self.handle_directive(directive, args, line_num):
                                raise AssemblerError(f"Direttiva '{directive}' non riconosciuta alla riga {line_num}")
                        else:
                            if self.current_section == "data":
                                raise AssemblerError(f"Istruzioni non ammesse nella sezione .data alla riga {line_num}")
                            raw_lines.append((self.code_address, rest, line_num))
                            self.code_address += 2
                        
                elif cleaned.startswith('.'):
                    parts = cleaned.split(None, 1)
                    directive = parts[0]
                    args = parts[1] if len(parts) > 1 else ""
                    
                    if self.handle_directive(directive, args, line_num):
                        continue
                    else:
                        raise AssemblerError(f"Direttiva '{directive}' non riconosciuta alla riga {line_num}")
                        
                else:
                    if self.current_section == "code":
                        raw_lines.append((self.code_address, cleaned, line_num))
                        self.code_address += 2
                    else:
                        raise AssemblerError(f"Istruzioni non ammesse nella sezione .data alla riga {line_num}")
        
        for addr, line, line_num in raw_lines:
            parts = re.split(r'[,\s]+', line)
            parts = [p for p in parts if p]
            mnemonic = parts[0].lower()
            args = parts[1:]

            inst = 0
            if mnemonic == "nop":
                if len(args) != 0:
                    raise AssemblerError(f"'nop' non richiede argomenti alla riga {line_num}")
                inst = 0x0000
                
            elif mnemonic in self.opcodes:
                op, expected_args = self.opcodes[mnemonic]
                if len(args) != expected_args:
                    raise AssemblerError(f"'{mnemonic}' richiede {expected_args} argomenti, trovati {len(args)} alla riga {line_num}")
                
                if mnemonic in ["ldi", "ldso", "stso"]:
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.imm(args[1]) & 0xFF)
                elif mnemonic in ["addi", "subi"]:
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.reg(args[1]) << 4) | (self.imm(args[2]) & 0xFF)
                elif mnemonic == "jump":
                    inst = (op << 12) | (self.imm(args[0]) << 8) | (self.reg(args[1]) << 4) | self.reg(args[2])
                elif mnemonic == "screen":
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.reg(args[1]) << 4) | (self.imm(args[2]) & 0xFF)
                elif len(args) == 3:
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.reg(args[1]) << 4) | self.reg(args[2])
            
            elif mnemonic in self.subopcodes:
                sub, expected_args = self.subopcodes[mnemonic]
                if len(args) != expected_args:
                    raise AssemblerError(f"'{mnemonic}' richiede {expected_args} argomenti, trovati {len(args)} alla riga {line_num}")
                
                if mnemonic == "push" or mnemonic == "pop":
                    inst = (0xF << 12) | (sub << 8) | (self.reg(args[0]) << 4)
                elif mnemonic == "cls":
                    inst = (0xF << 12) | (sub << 8) | (self.imm(args[0]) & 0xFF)
                elif mnemonic == "call":
                    inst = (0xF << 12) | (sub << 8) | (self.reg(args[0]) << 4) | self.reg(args[1])
                elif mnemonic in ["shl", "shr", "not"]:
                    inst = (0xF << 12) | (sub << 8) | (self.reg(args[0]) << 4) | self.reg(args[1])
                elif mnemonic in ["sec", "ret", "stop"]:
                    inst = (0xF << 12) | (sub << 8)
            else:
                raise AssemblerError(f"Mnemonic '{mnemonic}' non riconosciuto alla riga {line_num}")

            self.code_binary.append((inst >> 8) & 0xFF)
            self.code_binary.append(inst & 0xFF)
        
        return self.code_binary, self.data_binary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python assembler.py programma.asm")
    else:
        try:
            asm = Assembler()
            code, data = asm.assemble_file(sys.argv[1])
            
            print(f"// Defines: {asm.defines}")
            print(f"// Labels: {asm.labels}")
            
            if code:
                print(f"const s8 codeData[] = {{ {', '.join(f'0x{b:02X}' for b in code)} }};")
                print(f"const u16 codeSize = sizeof(codeData);")
            else:
                print(f"const s8 codeData[] = {{ 0 }};")
                print(f"const u16 codeSize = 0;")
            
            if data:
                print(f"const s8 staticData[] = {{ {', '.join(f'0x{b:02X}' for b in data)} }};")
                print(f"const u16 staticDataSize = sizeof(staticData);")
                print(f"const u16 staticDataAddr = 0x8000;")
            else:
                print(f"const s8 staticData[] = {{ 0 }};")
                print(f"const u16 staticDataSize = 0;")
                print(f"const u16 staticDataAddr = 0x8000;")
                
        except AssemblerError as e:
            print(f"ERRORE: {e}")
            sys.exit(1)
