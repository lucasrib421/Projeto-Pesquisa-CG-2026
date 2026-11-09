#!/usr/bin/env bash
# Varredura do atraso de espalhamento do modo channel (--spread-delay, em níveis de altura):
# 0 = igual a reserve, "never" = channel original. Compara com o controle, nos perfis baixo e terreno.
# Saída em results/experiment-delay/perfil-<perfil>/<rótulo>/seed-<n>/ e resumo por perfil.
# Uso: bash scripts/experiment-delay.sh [sementes...]   (padrão: 239 240 241 242 243)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ $# -gt 0 ]; then SEEDS=("$@"); else SEEDS=(239 240 241 242 243); fi
PROFILES=(${PROFILES:-baixo terreno})
DELAYS=(${DELAYS:-0 0.5 1 2 never})

run() { # rótulo, perfil, semente, argumentos extras...
    local label=$1 profile=$2 seed=$3; shift 3
    local dir="$REPO_DIR/results/experiment-delay/perfil-$profile/$label/seed-$seed"
    mkdir -p "$dir"
    # Caminhos relativos à pasta de trabalho do run.sh (contours/AppIso/AppIso)
    if ! bash "$REPO_DIR/scripts/run.sh" --river "../../../experiments/river-fig11-perfil-$profile.csv" --seed "$seed" \
            --out "../../../results/experiment-delay/perfil-$profile/$label/seed-$seed/" "$@" > "$dir/run.log" 2>&1; then
        echo "ERRO na execução. Log: $dir/run.log" >&2
        exit 1
    fi
}

for profile in "${PROFILES[@]}"; do
    for seed in "${SEEDS[@]}"; do
        echo "=== perfil $profile, semente $seed"
        run control "$profile" "$seed" --experiment control
        for d in "${DELAYS[@]}"; do
            if [ "$d" = never ]; then
                run channel-dnever "$profile" "$seed" --experiment channel
            else
                run "channel-d$d" "$profile" "$seed" --experiment channel --spread-delay "$d"
            fi
        done
    done
    echo "### Perfil $profile"
    python3 "$REPO_DIR/scripts/metrics.py" "$REPO_DIR/results/experiment-delay/perfil-$profile"
done

python3 "$REPO_DIR/scripts/compare_page.py" "$REPO_DIR/results/experiment-delay" "$REPO_DIR/experiments/river-fig11-perfil-alto.csv"
