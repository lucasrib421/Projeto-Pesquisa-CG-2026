#!/usr/bin/env bash
# Reproduz a baseline: Figura 11 do artigo (rio definido pelo mapa de probabilidade P).
# Saída em results/baseline/fig11/. Uso: bash scripts/baseline-fig11.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$REPO_DIR/results/baseline/fig11"

mkdir -p "$OUT_DIR"
# Caminho relativo à pasta de trabalho do run.sh (contours/AppIso/AppIso): os SVGs
# gravam o caminho no <title>, e um caminho absoluto mudaria de máquina para máquina.
bash "$REPO_DIR/scripts/run.sh" --figure 11 --out ../../../results/baseline/fig11/

echo "Arquivos gerados em $OUT_DIR:"
ls -1 "$OUT_DIR"
