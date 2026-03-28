#define tmp1 r14
#define tmp2 r15
#define rx r13
#define ry r12
#define ri r11
#define rr r10
#define rg r9
#define rii r8

ldi ry, 120
ldi tmp2, 7
ldi rii 5


loopy:

    subi rii, rii, 1
    jump !=, of(et1)
        ldi rii, 5
        subi tmp2, tmp2, 1
    et1:

    ldi rx, 120

    ldi tmp1, 2
    ldi ri 5
    loop:
        screen rx, ry, RED
        screen ry, rx, CYAN
        addi r7, ry, 1
        screen rx, r7, BLUE
        subi ri, ri, 1
        jump !=, of(draw)
            ldi ri, 5
            addi tmp1, tmp1, 1
        
        draw:
            sec
            subc rx, rx, tmp1
        jump >, OF(loop)
        sec
        subc ry, ry, tmp2
        jump >, OF(loopy)
    





end:
nop
jump COND_ALWAYS, OF(end)
