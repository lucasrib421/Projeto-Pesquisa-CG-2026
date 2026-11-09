#!/usr/bin/env bash
# Experimento do rio: baseline (rio no mapa P) × proposta (rio explícito, modos reserve e passive),
# com várias sementes. Saída em results/experiment-river/<modo>/seed-<n>/ e resumo das métricas.
# Uso: bash scripts/experiment-river.sh [sementes...]   (padrão: 239 240 241 242 243)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ $# -gt 0 ]; then SEEDS=("$@"); else SEEDS=(239 240 241 242 243); fi

# Caminhos relativos à pasta de trabalho do run.sh (contours/AppIso/AppIso)
RIVER=../../../experiments/river-fig11.csv
OUT=../../../results/experiment-river

for mode in baseline reserve passive; do
    for seed in "${SEEDS[@]}"; do
        dir="$REPO_DIR/results/experiment-river/$mode/seed-$seed"
        mkdir -p "$dir"
        echo "=== $mode, semente $seed"
        if ! bash "$REPO_DIR/scripts/run.sh" --experiment "$mode" --river "$RIVER" --seed "$seed" \
                --out "$OUT/$mode/seed-$seed/" > "$dir/run.log" 2>&1; then
            echo "ERRO na execução. Log: $dir/run.log" >&2
            exit 1
        fi
        grep "\[River\]" "$dir/run.log"
    done
done

python3 "$REPO_DIR/scripts/metrics.py" "$REPO_DIR/results/experiment-river"
python3 "$REPO_DIR/scripts/compare_page.py" "$REPO_DIR/results/experiment-river" "$REPO_DIR/experiments/river-fig11.csv"
