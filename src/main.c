#include "main.h"
#include "core.h"
#include "graphics.h"

extern u8 running;

int main() {
    printf("--- AVVIO EMULAZIONE SISTEMA ---\n");

    gfxInit();



s8 myProgram[] = { 0x72, 0x0A, 0x71, 0x01, 0x73, 0x0A, 0x00, 0x00, 0xA1, 0x27, 0x7E, 0x00, 0x7F, 0x06, 0xF2, 0x00, 0x00, 0x00, 0x63, 0xEF, 0x7E, 0x00, 0x7F, 0x00, 0x60, 0xEF };
    loadProgram(myProgram, sizeof(myProgram));

    while (running && !windowShouldClose()) {
        step();
        render();
    }

    gfxClose();
    printRF();

    return 0;
}
