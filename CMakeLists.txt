cmake_minimum_required(VERSION 3.11)
project(CPUEmulator C)

# --- 1. Gestione Raylib (FetchContent) ---
include(FetchContent)
FetchContent_Declare(
  raylib
  GIT_REPOSITORY https://github.com/raysan5/raylib.git
  GIT_TAG        master
)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(raylib)

# --- 2. Configurazione Sorgenti e Header ---

# Diciamo a CMake dove trovare i file .c (dentro src/)
set(SOURCES 
    src/main.c 
    src/core.c
)

add_executable(${PROJECT_NAME} ${SOURCES})

# Diciamo a CMake dove trovare i file .h (dentro include/)
# Così nei file .c puoi scrivere #include "core.h" invece di #include "../include/core.h"
target_include_directories(${PROJECT_NAME} PRIVATE include)

# --- 3. Linking ---
target_link_libraries(${PROJECT_NAME} raylib)

# Librerie di sistema per Linux
if(UNIX AND NOT APPLE)
    target_link_libraries(${PROJECT_NAME} m pthread dl rt)
endif()