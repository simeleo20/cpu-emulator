; ===== GENERATED CODE =====

main:
    ldi r2, 10
    push r2
    push r2
    ldi r14, HI(sommar)
    ldi r15, LO(sommar)
    call r14, r15
    pop r0
    stop

sommar:
    ldso r2, 3
    jump !=, OF(endif0)
    ldi r1, 0
    ret
endif0:
    ldso r2, 3
    subi r3, r2, 1
    push r3
    ldi r14, HI(sommar)
    ldi r15, LO(sommar)
    call r14, r15
    pop r0
    ldso r2, 3
    add r1, r1, r2
    ret

