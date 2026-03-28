; ==================== TEST COSTANTI PREDEFINITE ====================

; Colori gia definiti: BLACK, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW, WHITE
; Condizioni gia definite: COND_ALWAYS, COND_OVERFLOW, COND_NEGATIVE, COND_ZERO

.code

init:
    CLS 0
    
    ; Disegna pixel usando colori predefiniti
    LDI R1, 50
    LDI R2, 50
    SCREEN R1, R2, WHITE
    
    LDI R1, 80
    LDI R2, 50
    SCREEN R1, R2, RED
    
    LDI R1, 110
    LDI R2, 50
    SCREEN R1, R2, GREEN
    
    LDI R1, 140
    LDI R2, 50
    SCREEN R1, R2, BLUE

mainLoop:
    LDI R14, HI(mainLoop)
    LDI R15, LO(mainLoop)
    
    LDI R13, 30
delay:
    SUBI R13, R13, 1
    LDI R14, HI(delay)
    LDI R15, LO(delay)
    JUMP COND_ZERO, R14, R15
    
    JUMP COND_ALWAYS, R14, R15
