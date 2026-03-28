#include "core.h"
#include "graphics.h"
#include "type.h"

u8 overflow = 0;
u8 negative = 0;
u8 zero = 0;
u8 carry = 0;
u8 stackPointer = 0;
u16 programCounter = 0;
u8 running = 1;


// r0 sempre nullo
// r14 tmp1
// r15 tmp2
s8 registerFile[16];

// code 0x0000
// data 0x8000
// stack 0xFF00-0xFFFF
s8 ram[65536];


void printRF()
{
    printf("---------\n");
    for (int i=0;i<15;i+=2)
    {
        printf("%2d:%4d %2d:%4d \n", i, registerFile[i], i+1, registerFile[i+1]);
    }
    printf("---------\n");
    printf("o:%d n:%d z:%d c:%d\n",overflow,negative,zero,carry);
}


s8 readRam(u16 addr){
    return ram[addr];
}
void writeRam(u16 addr, s8 imm){
    ram[addr] = imm;
}

s8 readStack(u8 addr)
{
    return readRam(0xffff-addr);
}
void writeStack(u8 addr, s8 imm)
{
    writeRam(0xffff-addr,imm);
}
void pushStack(s8 imm)
{
    writeStack(stackPointer, imm);
    stackPointer++;
}
s8 popStack()
{
    stackPointer--;
    s8 out = readStack(stackPointer);
    return out;
}


s8 readReg(u8 rs1)
{
    if (rs1 == 0) return 0;
    else if (rs1>15) printf("Errore registro inesistente troppo alto");
    return registerFile[rs1];
}

s8* getRegisters(void) {
    return registerFile;
}

u8* getFlags(void) {
    static u8 flags[4];
    flags[0] = overflow;
    flags[1] = negative;
    flags[2] = zero;
    flags[3] = carry;
    return flags;
}

u16* getProgramCounter(void) {
    return &programCounter;
}

u8* getStackPointer(void) {
    return &stackPointer;
}

s8* getRam(void) {
    return ram;
}

void writeReg(u8 rd, s8 imm)
{
    if (rd == 0) return;
    registerFile[rd] = imm;
}

void loadProgram(const s8* program, u16 size)
{
    for (u16 i=0;i<size;i++)
    {
        writeRam(i, program[i]);
    }
}

void loadStaticData(const s8* data, u16 size, u16 baseAddr)
{
    for (u16 i=0;i<size;i++)
    {
        writeRam(baseAddr + i, data[i]);
    }
}

void step()
{
    u16 highByte = (u8)readRam(programCounter);
    u16 lowByte  = (u8)readRam(programCounter + 1);
    u16 instruction = (highByte << 8) | lowByte;

    programCounter += 2;
    u8 opcode = (instruction >> 12) & 0xf;
    switch (opcode)
    {
        case 0x0: nope(); break;
        case 0x1: add((instruction >> 8) & 0xf, (instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x2: addc((instruction >> 8) & 0xf, (instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x3: subc((instruction >> 8) & 0xf, (instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x4: addi((instruction >> 8) & 0xf, (instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x5: subi((instruction >> 8) & 0xf, (instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x6: jump((instruction >> 8) & 0xf, (instruction) & 0xff); break;
        case 0x7: ldi((instruction >> 8) & 0xf, instruction & 0xff); break;
        case 0x8: ld((instruction >> 8) & 0xf, (instruction >>4) & 0xf, instruction&0xf); break;
        case 0x9: st((instruction >>8) & 0xf, (instruction>>4)&0xf, instruction&0xf); break;
        case 0xa: screen((instruction >> 8) & 0xf, (instruction >>4) & 0xf, instruction&0xf); break;
        case 0xb: ldso((instruction >> 8) & 0xf, instruction & 0xff); break;
        case 0xc: stso((instruction >> 8) & 0xf, instruction & 0xff); break;
        case 0xd: and((instruction >> 8) & 0xf, (instruction >>4) & 0xf, instruction&0xf); break;
        case 0xe: or((instruction >> 8) & 0xf, (instruction >>4) & 0xf, instruction&0xf); break;
        case 0xf: subopcodes(instruction); break;
        default: printf("Istruzione sconosciuta: 0x%04X\n", instruction); break;
    }

}   

void subopcodes(u16 instruction)
{
    u8 subopcode = (instruction >> 8) & 0xf;
    switch (subopcode)
    {
        case 0x0: push((instruction >> 4) & 0xf); break;
        case 0x1: pop((instruction >> 4) & 0xf); break;
        case 0x2: sec(); break;
        case 0x3: ret(); break;
        case 0x4: call((instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x5: shl((instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x6: shr((instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x7: not((instruction >> 4) & 0xf, instruction & 0xf); break;
        case 0x8: cls(instruction & 0xff); break;
        case 0x9: stop(); break;
        default: printf("Sub-istruzione sconosciuta: 0x%04X\n", instruction); break;
    }
}

void loop()
{
    while (running)
    {
        step();
    }
}

void checkAluFlags(int sum)
{
    s8 result8 = (s8)sum;

    zero = (result8 == 0);
    negative = (result8 < 0);
    
    overflow = (sum < -128 || sum > 127);

    carry = ((sum & 0x100) != 0);
}

void nope()
{
    // Non fa nulla, istruzione NOP
}

void add(u8 rd, u8 rs1, u8 rs2)
{
    int sum = readReg(rs1) + readReg(rs2);
    checkAluFlags(sum);
    writeReg(rd,(s8)sum);
}
void addc(u8 rd, u8 rs1, u8 rs2)
{
    int sum = readReg(rs1) + readReg(rs2) + carry;
    checkAluFlags(sum);
    writeReg(rd,(s8)sum);
}
void subc(u8 rd, u8 rs1, u8 rs2)
{
    int val1 = (u8)readReg(rs1);
    int val2 = (u8)readReg(rs2);
    int borrow = 1 - carry;
    int diff = val1 - val2 - borrow;

    checkAluFlags(diff);
    // Nota: Il carry per la sottrazione di solito è l'inverso del borrow
    carry = (diff >= 0); 
    writeReg(rd, (s8)diff);
}
void addi(u8 rd, u8 rs1, s8 imm)
{
    int sum = readReg(rs1) + (imm & 0xf);
    checkAluFlags(sum);
    writeReg(rd,(s8)sum);
}
void subi(u8 rd, u8 rs1, s8 imm)
{
    int sum = readReg(rs1) - (imm & 0xf);
    checkAluFlags(sum);
    writeReg(rd,(s8)sum);
}

// se offset è zero salto ad indirizzo contenuto in r14 e r15,
// altrimenti salto a pc+offset
void jump(u8 cond, s8 offset)
{
    if (
        (cond == 0)
        ||
        (cond == 1 && overflow==1)
        ||
        (cond == 2 && negative==1) // <0
        ||
        (cond == 3 && zero==1) // ==0
        ||
        (cond == 4 && negative==0 && zero==0) // >0
        ||
        (cond == 5 && zero==0) // !=0
        ||
        (cond == 6 && negative==0) // >=0
        ||
        (cond == 7 && carry==0) // NC
        ||
        (cond == 8 && carry==1) // C
        ||
        (cond == 9 && (negative==1 || zero==1)) // <=0

    )
    {   
        u16 addr;
        if (offset != 0) {
            s16 signedOffset = (s16)offset; // Estendi a 16 bit mantenendo il segno
            addr = programCounter + (signedOffset * 2); // Moltiplica per 2 perché ogni istruzione è di 2 byte
        }
        else{
            addr = (readReg(14) << 8) | readReg(15);
        }

        programCounter = addr;
    }
}
void call(u8 rhi, u8 rlo)
{
    
    // Push High Byte
    pushStack((s8)((programCounter >> 8) & 0xFF));
    // Push Low Byte
    pushStack((s8)(programCounter & 0xFF));
    
    programCounter = ((readReg(rhi) << 8) | readReg(rlo));
}

void ret() {
    // Pop in ordine inverso rispetto alla push
    u8 lo = (u8)popStack();
    u8 hi = (u8)popStack();
    
    programCounter = (hi << 8) | lo;
}
void ldi(u8 rd, s8 imm)
{
    writeReg(rd, imm);
}

void ld(u8 rd, u8 rhi, u8 rlo)
{
    u16 addr = (readReg(rhi) << 8) | readReg(rlo);
    s8 value = readRam(addr);
    checkAluFlags(value);
    writeReg(rd,value);
}
void st(u8 rs1, u8 rhi, u8 rlo)
{
    u16 addr = (readReg(rhi) << 8) | readReg(rlo);
    s8 value = readReg(rs1);
    checkAluFlags(value);
    writeRam(addr,value);
}
void push(u8 rs1)
{
    s8 value = readReg(rs1);
    checkAluFlags(value);
    pushStack(value);
}
void pop(u8 rd)
{
    s8 value = popStack();
    checkAluFlags(value);
    writeReg(rd,value);
}

void screen(u8 rx, u8 ry, u8 rgb)
{
    putPixel((u8)readReg(rx),(u8)readReg(ry),rgb);
}

void sec()
{
    carry = 1;
}

void ldso(u8 rd, u8 offset)
{
    s8 value = readStack(stackPointer - offset);
    checkAluFlags(value);
    writeReg(rd,value);
}

void stso(u8 rs1, u8 offset)
{
    s8 value = readReg(rs1);
    checkAluFlags(value);
    writeStack(stackPointer - offset, value);
}

void and(u8 rd, u8 rs1, u8 rs2) {
    s8 result = readReg(rs1) & readReg(rs2);
    checkAluFlags(result); // Nota: in checkAluFlags l'overflow sarà 0
    writeReg(rd, result);
}

void or(u8 rd, u8 rs1, u8 rs2) {
    s8 result = readReg(rs1) | readReg(rs2);
    checkAluFlags(result);
    writeReg(rd, result);
}

void shl(u8 rd, u8 rs1) {
    u8 val = (u8)readReg(rs1);
    s8 result = (s8)(val << 1);
    checkAluFlags(result);
    carry = (val & 0x80) >> 7; // Il bit più significativo finisce nel carry
    writeReg(rd, result);
}

void shr(u8 rd, u8 rs1) {
    u8 val = (u8)readReg(rs1);
    s8 result = (s8)(val >> 1);
    checkAluFlags(result);
    carry = (val & 0x01);      // Il bit meno significativo finisce nel carry
    writeReg(rd, result);
}
void not(u8 rd, u8 rs1) {
    s8 val = readReg(rs1);
    s8 result = ~val; // Operatore bitwise NOT in C
    
    checkAluFlags(result);
    // Nota: Il NOT non genera mai carry o overflow, 
    // quindi checkAluFlags li azzererà correttamente.
    
    writeReg(rd, result);
}

void stop()
{
    printf("Esecuzione terminata con STOP\n");
    running = 0;
    gfxClose();
}

void cls(u8 rgb) {
    clearScreen(rgb);
}