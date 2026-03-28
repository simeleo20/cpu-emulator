; ===== GENERATED CODE =====

main:
    ldi r14, 10
    add r1, r14, r0
    ldi r14, 5
    add r2, r14, r0
    sec
    subc r15, r1, r2
    jump >, OF(else1)
    subc r15, r1, r2
    sec
    subc r15, r0, r15
    add r12, r15, r0
    ret
    jump OF(endif0)
else1:
    subc r15, r2, r1
    sec
    subc r15, r0, r15
    add r12, r15, r0
    ret
endif0:
    ret
