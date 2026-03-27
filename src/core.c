#include "core.h"
#include "type.h"

u8 overflow = 0;
u8 negative = 0;
u8 zero = 0;
u8 carry = 0;
u8 stackPointer = 0;
u16 programCounter = 0;

s8 registerFile[16];
// stack FF00-FFFF
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
    s8 out = readStack(stackPointer);
    stackPointer--;
    return out;
}


s8 readReg(u8 rs1)
{
    if (rs1 == 0) return 0;
    else if (rs1>15) printf("Errore registro inesistente troppo alto");
    return registerFile[rs1];
}
void writeReg(u8 rd, s8 imm)
{
    if (rd == 0) return;
    registerFile[rd] = imm;
}


void checkAluFlags(int sum)
{
    s8 result8 = (s8)sum;

    zero = (result8 == 0);
    negative = (result8 < 0);
    
    overflow = (sum < -128 || sum > 127);

    carry = ((sum & 0x100) != 0);
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
    int diff = readReg(rs1) - readReg(rs2)- (1-carry);
    int tempForFlags = diff;
    if (diff >= 0) {
        tempForFlags |= 0x100; // Imposta il bit carry se il risultato è positivo
    } else {
        tempForFlags &= ~0x100; // Pulisce il bit carry se c'è stato prestito
    }
    checkAluFlags(diff);
    writeReg(rd,(s8)diff);
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
void jump(u8 cond, u16 addr)
{
    if (
        cond == 0
        ||
        cond == 1 && overflow==1
        ||
        cond == 2 && negative==1
        ||
        cond == 3 && zero==1
    )
    {
        programCounter = addr;
    }
}
void call(u16 addr)
{
    // Push High Byte
    pushStack((s8)((programCounter >> 8) & 0xFF));
    // Push Low Byte
    pushStack((s8)(programCounter & 0xFF));
    
    programCounter = addr;
}

void ret() {
    // Pop in ordine inverso rispetto alla push
    u8 lo = (u8)popStack();
    u8 hi = (u8)popStack();
    
    programCounter = (hi << 8) | lo;
}
void ldi(u8 rd, s8 imm)
{
    checkAluFlags(imm);
    writeReg(rd, imm);
}

void ld(u8 rd, u16 addr)
{
    s8 value = readRam(addr);
    checkAluFlags(value);
    writeReg(rd,value);
}
void st(u8 rs1, u16 addr)
{
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
    putPixel(readReg(rx),readReg(ry),rgb);
}

void sec()
{
    carry = 1;
}

void putPixel(u8 x, u8 y, u8 rgb)
{

}
