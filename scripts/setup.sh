#!/usr/bin/env bash
# Compila o AppIso (código do artigo, em contours/) dentro de build/.
# Uso: bash scripts/setup.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_DIR/contours/AppIso/AppIso"
BUILD_DIR="$REPO_DIR/build"
APT_PACKAGES="build-essential cmake ninja-build pkg-config libglew-dev qt6-base-dev qt6-base-dev-tools qt6-svg-dev"

echo "=== 1/3 Verificando dependências ==="
missing=()
command -v g++ >/dev/null 2>&1 || missing+=("g++")
command -v cmake >/dev/null 2>&1 || missing+=("cmake")
command -v pkg-config >/dev/null 2>&1 || missing+=("pkg-config")
[ -f /usr/include/GL/glew.h ] || missing+=("GLEW (libglew-dev)")
if [ ${#missing[@]} -gt 0 ]; then
    echo "ERRO: faltando: ${missing[*]}" >&2
    echo "No Ubuntu/Debian, instale com:" >&2
    echo "  sudo apt install $APT_PACKAGES" >&2
    exit 1
fi
echo "ok"

echo "=== 2/3 Compilando em build/ ==="
GENERATOR="Unix Makefiles"
command -v ninja >/dev/null 2>&1 && GENERATOR="Ninja"
if ! cmake -S "$SRC_DIR" -B "$BUILD_DIR" -G "$GENERATOR" -DCMAKE_BUILD_TYPE=Release; then
    echo "ERRO: a configuração do CMake falhou. Provavelmente falta o Qt 6:" >&2
    echo "  sudo apt install qt6-base-dev qt6-base-dev-tools qt6-svg-dev" >&2
    exit 1
fi
cmake --build "$BUILD_DIR" --parallel

echo "=== 3/3 Ligando Data/ e Images/ ao lado do executável ==="
# O programa carrega imagens de <pasta do executável>/Data e /Images ao iniciar
# (main-window.h). O CMakeLists original só cria esses links no Windows.
ln -sfn ../contours/AppIso/Data "$BUILD_DIR/Data"
ln -sfn ../contours/AppIso/Images "$BUILD_DIR/Images"

echo
echo "Pronto: $BUILD_DIR/AppIso"
echo "Para executar: bash scripts/run.sh"
