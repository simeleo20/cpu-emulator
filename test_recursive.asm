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

