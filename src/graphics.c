#include "graphics.h"

static Color screenBuffer[SCREEN_WIDTH * SCREEN_HEIGHT];
static Texture2D screenTexture;
static bool initialized = false;

static Color rgb3ToColor(unsigned char rgb) {
    unsigned char r = (rgb & 0x01) ? 255 : 0;
    unsigned char g = (rgb & 0x02) ? 255 : 0;
    unsigned char b = (rgb & 0x04) ? 255 : 0;
    return (Color){r, g, b, 255};
}

void gfxInit(void) {
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "CPU Emulator");
    ClearWindowState(FLAG_WINDOW_RESIZABLE);
    
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        screenBuffer[i] = (Color){0, 0, 0, 255};
    }
    
    Image image = GenImageColor(SCREEN_WIDTH, SCREEN_HEIGHT, BLACK);
    screenTexture = LoadTextureFromImage(image);
    UnloadImage(image);
    
    initialized = true;
}

void gfxClose(void) {
    if (initialized) {
        UnloadTexture(screenTexture);
        CloseWindow();
        initialized = false;
    }
}

void putPixel(int x, int y, unsigned char rgb) {
    if (!initialized) return;
    if (x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT) return;
    
    screenBuffer[y * SCREEN_WIDTH + x] = rgb3ToColor(rgb);
}

void clearScreen(unsigned char rgb) {
    if (!initialized) return;
    
    Color color = rgb3ToColor(rgb);
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        screenBuffer[i] = color;
    }
}

void render(void) {
    if (!initialized) return;
    
    UpdateTexture(screenTexture, screenBuffer);
    DrawTexture(screenTexture, 0, 0, WHITE);
}

int windowShouldClose(void) {
    return WindowShouldClose();
}
