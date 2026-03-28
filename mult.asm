; ==================== TEST COSTANTI PREDEFINITE ====================

; Colori gia definiti: BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE
; Condizioni gia definite: COND_ALWAYS, COND_OVERFLOW, COND_NEGATIVE, COND_ZERO



#define ris r1
#define a r2 
#define b r3
.code

ldi a, 7
ldi b, 3

push a 
push b 
ldi r14, hi(mult)
ldi r15, lo(mult)
call r14, r15

stop



mult:
    ;of 4 = a
    ;of 3 = b

    ldi ris, 0
    ldi r6, 0

    ldso r4, 4
    ldso r5, 3
    ldi r14, hi(endMult)
    ldi r15, lo(endMult)
    jump COND_ZERO, r14, r15
    ldi r14, hi(multLp)
    ldi r15, lo(multLp)
    jump COND_NEGATIVE, r14, r15
    sec
    subc r5, r0, r5

    ldi r6, -1

    multLp:
        add ris, ris, r4
        addi r5, r5, 1
        ldi r14, hi(multLp)
        ldi r15, lo(multLp)
        jump COND_NEGATIVE, r14, r15
    
        add r6, r6, r0
        ldi r14, hi(endMult)
        ldi r15, lo(endMult)
        jump COND_NEGATIVE, r14, r15
        sec 
        subc ris, r0, ris
    endMult:
        ret

stop