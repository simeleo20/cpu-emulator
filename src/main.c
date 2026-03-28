#include "main.h"
#include "core.h"
#include "graphics.h"
#include "program.h"

extern u8 running;

int main() {
    printf("--- AVVIO EMULAZIONE SISTEMA ---\n");

    gfxInit();
    
    loadProgram(codeData, codeSize);
    loadStaticData(staticData, staticDataSize, staticDataAddr);

    while (running && !windowShouldClose()) {
        step();
        render();
    }

    gfxClose();
    printRF();

    return 0;
}
