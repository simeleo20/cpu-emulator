#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASM_FILE="$SCRIPT_DIR/test.asm"
PROGRAM_FILE="$SCRIPT_DIR/src/program.c"
BUILD_DIR="$SCRIPT_DIR/build"

echo "=== Assembling $ASM_FILE ==="
python3 "$SCRIPT_DIR/assembler.py" "$ASM_FILE" > /tmp/asm_output.txt

echo "=== Labels ==="
grep "^// Labels" /tmp/asm_output.txt || true

echo "=== Updating program.c ==="
{
    echo "#include \"program.h\""
    echo ""
    
    # Extract code data
    CODE_LINE=$(grep "^const s8 codeData" /tmp/asm_output.txt)
    echo "$CODE_LINE"
    
    CODE_SIZE=$(grep "^const u16 codeSize" /tmp/asm_output.txt)
    echo "$CODE_SIZE"
    
    # Extract static data
    DATA_LINE=$(grep "^const s8 staticData" /tmp/asm_output.txt)
    echo "$DATA_LINE"
    
    DATA_SIZE=$(grep "^const u16 staticDataSize" /tmp/asm_output.txt)
    echo "$DATA_SIZE"
    
    DATA_ADDR=$(grep "^const u16 staticDataAddr" /tmp/asm_output.txt)
    echo "$DATA_ADDR"
} > "$PROGRAM_FILE"

echo "=== Building ==="
cd "$BUILD_DIR"
cmake .. > /dev/null 2>&1
make

echo "=== Running ==="
./CPUEmulator
