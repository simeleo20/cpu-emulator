#!/bin/bash
set -e

# Se la cartella build non esiste o è vuota, configura
if [ ! -d "build" ] || [ ! -f "build/CMakeCache.txt" ]; then
  echo "--- Configurazione CMake ---"
  cmake -B build
fi

echo "--- Compilazione in corso... ---"
# Questo comando è UNIVERSALE: trova da solo se deve usare ninja o make
cmake --build build

echo "--- Esecuzione ---"
./build/CPUEmulator