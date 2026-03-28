#define x r13
#define y r12
#define vx r11
#define vy r10
#define tmp1 r14
#define tmp2 r15
#define width 254
#define high 254


ldi x, 6
ldi y, 100

ldi vx, 1
ldi vy, 1

loop:

    add x, x, vx
    add y, y, vy
    cls BLACK
    screen x, y, WHITE
    
    ldi tmp1, width
    ldi tmp2, high
    
    check_x_r:
        sec
        subc r0, tmp1, x
        jump =, OF(invx)
    check_x_l:
        addi r0, x, 0
        jump =, OF(invx)
    check_y_d:
        sec
        subc r0, tmp2, y
        jump =, OF(invy)
    check_y_u:
        addi r0, y, 0
        jump =, OF(invy)

    


    jump COND_ALWAYS, OF(loop)

end:
    nop
    nop
    nop
    jump COND_ALWAYS, OF(end)


invx:
    sec
    subc vx, r0, vx
    jump COND_ALWAYS, OF(check_y_d)

invy:
    sec
    subc vy, r0, vy
    jump COND_ALWAYS, OF(loop)
