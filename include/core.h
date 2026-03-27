#include <stdio.h>
#include "type.h"

// r0 sempre nullo

//utilities
void printRF();

s8 readReg(u8 rs1);
void writeReg(u8 rd, s8 imm);

void checkAluFlags(int sum);

void putPixel(u8 x, u8 y, u8 rgb);

void nope();
void add(u8 rd, u8 rs1, u8 rs2);
void addc(u8 rd, u8 rs1, u8 rs2);
void subc(u8 rd, u8 rs1, u8 rs2);
void addi(u8 rd, u8 rs1, s8 imm);
void subi(u8 rd, u8 rs1, s8 imm);
void jump(u8 cond, u16 addr);
void call(u16 addr);
void ret();
void ldi(u8 rd, s8 imm);
void ld(u8 rd, u16 addr);
void st(u8 rs1, u16 addr);
//void str(u8 rs1, u8 rd, u8 off);
void push(u8 rs1);
void pop(u8 rd);
void screen(u8 rx, u8 ry, u8 rgb);
void sec();