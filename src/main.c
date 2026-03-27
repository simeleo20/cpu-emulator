#include "main.h"
#include "core.h"
#include "graphics.h"

extern u8 running;

int main() {
    printf("--- AVVIO EMULAZIONE SISTEMA ---\n");

    gfxInit();
s8 myProgram[] = { 0x73, 0x0A, 0x74, 0x05, 0x12, 0x34, 0xF0, 0x20, 0x7E, 0x00, 0x7F, 0x00, 0x60, 0xEF };
    loadProgram(myProgram, sizeof(myProgram));

    while (running && !windowShouldClose()) {
        step();
        render();
    }

    gfxClose();
    printRF();

    return 0;
}
