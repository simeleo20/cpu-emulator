#include <stdio.h>
#include "type.h"

// r0 sempre nullo

//utilities
void printRF();

s8 readReg(u8 rs1);
s8* getRegisters(void);
u8* getFlags(void);
u16* getProgramCounter(void);
u8* getStackPointer(void);
s8* getRam(void);
void writeReg(u8 rd, s8 imm);

void checkAluFlags(int sum);

void loadProgram(const s8* program, u16 size);


void step();
void loop();

void nope();
void add(u8 rd, u8 rs1, u8 rs2);
void addc(u8 rd, u8 rs1, u8 rs2);
void subc(u8 rd, u8 rs1, u8 rs2);
void addi(u8 rd, u8 rs1, s8 imm);
void subi(u8 rd, u8 rs1, s8 imm);
void jump(u8 cond, u8 rhi, u8 rlo);
void ldi(u8 rd, s8 imm);
void ld(u8 rd, u8 rhi, u8 rlo);
void st(u8 rs1, u8 rhi, u8 rlo);
void screen(u8 rx, u8 ry, u8 rgb);
void ldso(u8 rd, u8 offset);
void stso(u8 rs1, u8 offset);
void and(u8 rd, u8 rs1, u8 rs2);
void or(u8 rd, u8 rs1, u8 rs2);
void subopcodes(u16 instruction);

void push(u8 rs1);
void pop(u8 rd);
void sec();
void ret();
void call(u8 rhi, u8 rlo);
void shl(u8 rd, u8 rs1);
void shr(u8 rd, u8 rs1);
void not(u8 rd, u8 rs1);
void cls(u8 rgb);
void stop();

