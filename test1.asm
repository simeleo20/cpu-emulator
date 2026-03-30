; ===== GENERATED CODE =====

main:
    ldi r2, 10
    push r2
    push r14
    push r15
    push r2
    ldi r14, HI(sommar)
    ldi r15, LO(sommar)
    call r14, r15
    pop r0
    pop r15
    pop r14
    push r1
    ldi r2, 21
    push r2
    ldso r2, 2
    add r15, r2, r0
    ldso r2, 1
    add r1, r15, r2
    push r1
    stop

sommar:
    ldso r2, 3
    jump !=, OF(endif0)
    ldi r1, 0
    ret
endif0:
    push r14
    push r15
    ldso r2, 3
    subi r3, r2, 1
    push r3
    ldi r14, HI(sommar)
    ldi r15, LO(sommar)
    call r14, r15
    pop r0
    pop r15
    pop r14
    ldso r2, 3
    add r1, r1, r2
    ret

