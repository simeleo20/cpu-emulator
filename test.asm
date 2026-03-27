start:
ldi r3, 10
ldi r4, 5

add r2, 3, 4
push r2

ldi r14, HI(start)
ldi r15, LO(start)
jump 0, r14, r15