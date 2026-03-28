#ifndef GRAPHICS_H
#define GRAPHICS_H

#include <raylib.h>

#define SCREEN_WIDTH  256
#define SCREEN_HEIGHT 256
#define SCREEN_SCALE 3

void gfxInit(void);
void gfxClose(void);
void putPixel(int x, int y, unsigned char rgb);
void clearScreen(unsigned char rgb);
void render(void);
int windowShouldClose(void);

#endif
