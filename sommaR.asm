;ogni variabile corrisponde a un push sullo stack
main:

ldi r2, 10 ;  = 10
push r2    ; int a

push r2                         ;<- passiamo il parametro che in questo caso è gia in r2 se no lo avremmo dovuto caricare dalla stack
ldi r14, HI(sommar)
ldi r15, LO(sommar)
call r14, r15 ;sommar(a)
pop r0                          ;per ogni push corrisponde un pop
                                ;per quanto riguarda il passagigio di parametri

stop


;se la funzione fosse stata sommar(a,b) viene pushato prima a e poi b 
;quindi a si troverà ad offset 4 e b ad offset 3
sommar: 
    ldso r2, 3          ;estrapoliamo il valore del parametro a
    jump !=, OF(endif0) ;if(a==0) esegue l'istruzione dopo se no esce
        ldi r1, 0
        ret
    endif0:
    subi r3, r2, 1      ; a-1
    push r3             ; passiamo il parametro a-1
    call r14, r15       ;l'address è gia caricato per forza in r14 e r15, se no lo avremmo dovuto loaddare
    pop r0              ;pop del parametro passato precedentemente
    ldso r2, 3          ;il valore di a va ricaricato perché dentro la call potrebbe essere cambiato
    add r1, r1, r2      ;r1 è il reg di default per i return
                        ;quindi contiene il risultato della call appena
                        ;eseguita, possiamo quindi sommarlo ad a
    ret