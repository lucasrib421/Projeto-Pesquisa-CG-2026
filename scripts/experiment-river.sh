#!/usr/bin/env bash
# Experimento do rio: baseline (rio no mapa P) × proposta (rio explícito, modos reserve e passive),
# para três perfis de altura do leito (alto, baixo, terreno) e várias sementes.
# Saída em results/experiment-river/perfil-<perfil>/<modo>/seed-<n>/, métricas por perfil e
# a página results/experiment-river/index.html.
# Uso: bash scripts/experiment-river.sh [sementes...]   (padrão: 239 240 241 242 243)
# Só alguns perfis ou modos: PROFILES="terreno" MODES="channel" bash scripts/experiment-river.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ $# -gt 0 ]; then SEEDS=("$@"); else SEEDS=(239 240 241 242 243); fi
PROFILES=(${PROFILES:-alto baixo terreno})
MODES=(${MODES:-baseline control reserve passive channel})

for profile in "${PROFILES[@]}"; do
    # Caminhos relativos à pasta de trabalho do run.sh (contours/AppIso/AppIso)
    river=../../../experiments/river-fig11-perfil-$profile.csv
    out=../../../results/experiment-river/perfil-$profile
    for mode in "${MODES[@]}"; do
        for seed in "${SEEDS[@]}"; do
            dir="$REPO_DIR/results/experiment-river/perfil-$profile/$mode/seed-$seed"
            mkdir -p "$dir"
            echo "=== perfil $profile, $mode, semente $seed"
            if ! bash "$REPO_DIR/scripts/run.sh" --experiment "$mode" --river "$river" --seed "$seed" \
                    --out "$out/$mode/seed-$seed/" > "$dir/run.log" 2>&1; then
                echo "ERRO na execução. Log: $dir/run.log" >&2
                exit 1
            fi
            grep "\[River\]" "$dir/run.log"
        done
    done
    echo "### Perfil $profile"
    python3 "$REPO_DIR/scripts/metrics.py" "$REPO_DIR/results/experiment-river/perfil-$profile"
done

python3 "$REPO_DIR/scripts/compare_page.py" "$REPO_DIR/results/experiment-river" "$REPO_DIR/experiments/river-fig11-perfil-alto.csv"
