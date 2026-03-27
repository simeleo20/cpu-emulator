import sys
import re

class Assembler:
    def __init__(self):
        self.labels = {}
        self.opcodes = {
            "nop": 0x0, "add": 0x1, "addc": 0x2, "subc": 0x3,
            "addi": 0x4, "subi": 0x5, "jump": 0x6, "ldi": 0x7,
            "ld": 0x8, "st": 0x9, "screen": 0xA, "ldso": 0xB,
            "stso": 0xC, "and": 0xD, "or": 0xE, "subop": 0xF
        }
        self.subopcodes = {
            "push": 0x0, "pop": 0x1, "sec": 0x2, "ret": 0x3,
            "call": 0x4, "shl": 0x5, "shr": 0x6, "not": 0x7, "cls": 0x8, "stop": 0x9
        }

    def clean_line(self, line):
        line = re.sub(r';.*', '', line) # Rimuove i commenti
        return line.strip()

    def reg(self, s): return int(s.strip().upper().replace('R', ''))
    
    def imm(self, s):
        # Se l'argomento è una label conosciuta (HI o LO), estrai il byte
        if s.startswith("HI("):
            label = s[3:-1]
            return (self.labels[label] >> 8) & 0xFF
        if s.startswith("LO("):
            label = s[3:-1]
            return self.labels[label] & 0xFF
        # Altrimenti converti numero normale (es: 10, 0xA)
        return int(s.strip(), 0)

    def assemble_file(self, filename):
        # --- PRIMA PASSATA: Calcolo indirizzi e Label ---
        address = 0
        raw_lines = []
        with open(filename, 'r') as f:
            for line in f:
                cleaned = self.clean_line(line)
                if not cleaned: continue # SALTA RIGHE VUOTE (Nessun NOP aggiunto)
                
                if cleaned.endswith(':'):
                    self.labels[cleaned[:-1]] = address
                else:
                    raw_lines.append((address, cleaned))
                    address += 2 # Ogni istruzione occupa 2 byte

        # --- SECONDA PASSATA: Generazione Byte ---
        binary = []
        for addr, line in raw_lines:
            parts = line.replace(',', ' ').split()
            mnemonic = parts[0].lower()
            args = parts[1:]

            inst = 0
            if mnemonic == "nop":
                inst = 0x0000
            elif mnemonic in self.opcodes and mnemonic != "subop":
                op = self.opcodes[mnemonic]
                if mnemonic in ["ldi", "ldso", "stso"]:
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.imm(args[1]) & 0xFF)
                elif mnemonic == "jump":
                    inst = (op << 12) | (self.imm(args[0]) << 8) | (self.reg(args[1]) << 4) | self.reg(args[2])
                elif len(args) == 3: # add, addc, ld, st, etc.
                    inst = (op << 12) | (self.reg(args[0]) << 8) | (self.reg(args[1]) << 4) | self.reg(args[2])
            
            elif mnemonic in self.subopcodes:
                sub = self.subopcodes[mnemonic]
                if mnemonic in ["push", "pop"]:
                    inst = (0xF << 12) | (sub << 8) | (self.reg(args[0]) << 4)
                elif mnemonic == "cls":
                    inst = (0xF << 12) | (sub << 8) | (self.imm(args[0]) & 0xFF)
                elif mnemonic in ["shl", "shr", "not", "call"]:
                    inst = (0xF << 12) | (sub << 8) | (self.reg(args[0]) << 4) | self.reg(args[1])
                elif mnemonic in ["sec", "ret", "stop"]:
                    inst = (0xF << 12) | (sub << 8)
            else:
                raise ValueError(f"Errore: Mnemonic '{mnemonic}' non riconosciuto all'indirizzo {addr}")

            binary.append((inst >> 8) & 0xFF)
            binary.append(inst & 0xFF)
        
        return binary

# Main execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python assembler.py programma.asm")
    else:
        asm = Assembler()
        bin_data = asm.assemble_file(sys.argv[1])
        print(f"// Label trovate: {asm.labels}")
        print("s8 myProgram[] = { " + ", ".join(f"0x{b:02X}" for b in bin_data) + " };")