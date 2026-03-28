; ==================== MOLTIPLICATORE ====================

#define ris r1
#define a r2 
#define b r3
.code
mult:
    ldi ris, 0
    ldi r6, 0

    ldso r4, 4
    ldso r5, 3

    jump =         ; se b == 0, salto assoluto a r14:r15 (endMult)
    ldi r14, hi(multLp)
    ldi r15, lo(multLp)
    jump <          ; se b < 0, salto assoluto a r14:r15 (multLp)
    
    sec
    subc r5, r0, r5

    ldi r6, -1

    multLp:
        add ris, ris, r4
        addi r5, r5, 1
        
        ldi r14, hi(multLp)
        ldi r15, lo(multLp)
        jump <          ; se b < 0, salto assoluto a r14:r15
    
        add r6, r6, r0
        ldi r14, hi(endMult)
        ldi r15, lo(endMult)
        jump <          ; se r6 < 0 (cioè == -1), salto assoluto a r14:r15
        
        sec 
        subc ris, r0, ris
    
    endMult:
        ret

stop

; ===== GENERATED CODE =====

main:
    ldi r14, 5
    push r14
    ldi r14, hi(fact)
    ldi r15, lo(fact)
    call r14, r15
    pop r0
    stso r12, 0
    stop

fact:
    ldso r14, 0
    push r14
    ldi r14, 1
    pop r15
    sec
    subc r14, r15, r14
    jump >, OF(endif0)
    ldi r14, 1
    add r12, r14, r0
    ret
endif0:
    ldso r14, 0
    add r13, r14, r0
    ldso r14, 0
    push r14
    ldi r14, 1
    pop r15
    sec
    subc r12, r15, r14
    push r12
    ldi r14, hi(fact)
    ldi r15, lo(fact)
    call r14, r15
    pop r0
    push r12
    push r13
    ldi r14, hi(mult)
    ldi r15, lo(mult)
    call r14, r15
    pop r0
    pop r0
    ret

