start:
ldi r2, 10
ldi r1, 1

ldi r3, 10

loop:
addi r1 1
screen r1, r2, 7
ldi r14, HI(loop)
ldi r15, LO(loop)
sec
subi r3, 1
jump 3, r14, r15


ldi r14, HI(start)
ldi r15, LO(start)
jump 0, r14, r15