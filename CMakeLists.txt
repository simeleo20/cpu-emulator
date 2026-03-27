cmake_minimum_required(VERSION 3.11)
project(CPUEmulator C)

# Esporta i comandi per far funzionare IntelliSense (errori in tempo reale)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# --- 1. Gestione Raylib (FetchContent) ---
include(FetchContent)
FetchContent_Declare(
  raylib
  GIT_REPOSITORY https://github.com/raysan5/raylib.git
  GIT_TAG        master
)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(raylib)

# --- 2. Configurazione Automatica Sorgenti ---

# Prende in automatico tutti i file .c in src/ e tutti i .h in include/
file(GLOB_RECURSE SOURCES "src/*.c")
file(GLOB_RECURSE HEADERS "include/*.h")

# Se aggiungi un nuovo file, CMake lo vedrà alla prossima compilazione
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# --- 4. Flag di Compilazione (Sicurezza e Warning) ---
if(MSVC)
    # Per Visual Studio
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    # Per GCC e Clang (Linux/macOS)
    target_compile_options(${PROJECT_NAME} PRIVATE 
        -Wall           # Warning base
        -Wextra          # Warning extra (molto utili)
        -Wconversion     # <--- Fondamentale: ti avvisa se -220 non entra in 8 bit
        -Wshadow         # Ti avvisa se usi lo stesso nome per variabili diverse
    )
endif()

# Diciamo a CMake dove sono gli header per gli #include "file.h"
target_include_directories(${PROJECT_NAME} PRIVATE include)

# --- 3. Linking ---
target_link_libraries(${PROJECT_NAME} raylib)

# Librerie necessarie per far girare Raylib su Linux (X11, audio, ecc.)
if(UNIX AND NOT APPLE)
    target_link_libraries(${PROJECT_NAME} m pthread dl rt)
endif()