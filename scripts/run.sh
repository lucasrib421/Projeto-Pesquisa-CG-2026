#!/usr/bin/env bash
# Executa o AppIso com o diretório de trabalho e o ambiente corretos.
# Uso: bash scripts/run.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$REPO_DIR/build/AppIso"

if [ ! -x "$BIN" ]; then
    echo "ERRO: $BIN não encontrado. Rode antes: bash scripts/setup.sh" >&2
    exit 1
fi
if [ ! -e "$REPO_DIR/build/Data" ] || [ ! -e "$REPO_DIR/build/Images" ]; then
    echo "ERRO: links build/Data ou build/Images ausentes. Rode: bash scripts/setup.sh" >&2
    exit 1
fi

# GLEW (Ubuntu) usa GLX; sob Wayland o Qt cria contexto EGL e o glewInit falha.
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

# No WSL, sem isto o Mesa renderiza na CPU (llvmpipe) em vez da GPU.
if grep -qi microsoft /proc/version 2>/dev/null && [ -e /dev/dxg ]; then
    export GALLIUM_DRIVER="${GALLIUM_DRIVER:-d3d12}"
fi

# Shaders e caminhos "../Data/..." são relativos a esta pasta.
cd "$REPO_DIR/contours/AppIso/AppIso"
exec "$BIN" "$@"
