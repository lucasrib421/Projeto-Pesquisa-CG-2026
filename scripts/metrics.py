#!/usr/bin/env python3
"""Métricas do experimento do rio.

Uso: python3 scripts/metrics.py results/experiment-river/perfil-baixo

Lê <pasta>/<modo>/seed-<n>/{nodes.csv,edges.csv,run_info.txt}, gerados por
`AppIso --experiment`, e escreve <pasta>/summary.csv (uma linha por execução)
e <pasta>/summary.md (média e desvio padrão por modo).
"""
import csv
import math
import statistics
import sys
from pathlib import Path


def read_info(path):
    info = {}
    for line in path.read_text().splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            info[k] = v
    return info


def run_metrics(run_dir):
    info = read_info(run_dir / 'run_info.txt')
    nodes = {int(r['id']): r for r in csv.DictReader(open(run_dir / 'nodes.csv'))}
    neigh = {i: [] for i in nodes}
    for r in csv.DictReader(open(run_dir / 'edges.csv')):
        a, b = int(r['a']), int(r['b'])
        neigh[a].append(b)
        neigh[b].append(a)

    rank = {i: float(r['rank']) for i, r in nodes.items()}
    height = {i: float(r['height']) for i, r in nodes.items()}
    river = {i for i, r in nodes.items() if r['river_index'] != '-1'}
    keys = [float(k) for k in info['histogram_keys'].split(';')]

    # Garantia do artigo: todo nó fora da costa tem um vizinho com senha menor
    no_lower = sum(1 for i, r in nodes.items()
                   if r['coast'] == '0' and not any(rank[j] < rank[i] for j in neigh[i]))

    m = {
        'mode': info['mode'],
        'seed': int(info['seed']),
        'nodes': len(nodes),
        'river_nodes': len(river),
        'nodes_without_lower_neighbour': no_lower,
        'ms_growth': int(info['ms_growth']),
    }
    if river:
        target = {i: float(nodes[i]['target_elevation']) for i in river}
        err = [abs(height[i] - target[i]) for i in river]
        floor = [min(abs(k - target[i]) for k in keys) for i in river]
        # "Vale": o nó do rio é mais baixo que todas as margens (vizinhos fora do rio).
        # Por senha (ordem do crescimento) e por altura (o que o terreno mostra: só 12 alturas,
        # então senha menor não implica altura menor).
        by_rank = by_height = with_banks = 0
        depth = []
        for i in river:
            banks = [j for j in neigh[i] if j not in river]
            if not banks:
                continue
            with_banks += 1
            by_rank += all(rank[i] < rank[j] for j in banks)
            by_height += all(height[i] < height[j] for j in banks)
            depth.append(statistics.mean(height[j] for j in banks) - height[i])
        m.update({
            'riverbed_error_mean': statistics.mean(err),
            'riverbed_error_max': max(err),
            'quantization_floor_mean': statistics.mean(floor),
            'valley_by_rank_pct': 100.0 * by_rank / with_banks,
            'valley_by_height_pct': 100.0 * by_height / with_banks,
            'valley_depth_mean': statistics.mean(depth),
        })

        # Perfil transversal: altura média dos nós (fora da costa) por faixa de distância até o rio.
        # O rio funciona como semente e rebaixa um corredor em volta dele, não só os próprios nós.
        pos = {i: (float(r['x']), float(r['y'])) for i, r in nodes.items()}
        bands = {b: [] for b in BANDS}
        for i, r in nodes.items():
            if r['coast'] == '1':
                continue
            dist = min(math.dist(pos[i], pos[j]) for j in river)
            for b in BANDS:
                if b[0] <= dist < b[1]:
                    bands[b].append(height[i])
        for b, vals in bands.items():
            if vals:
                m[band_key(b)] = statistics.mean(vals)
    return m


BANDS = [(0, 30), (30, 60), (60, 100), (100, 150), (150, 250)]


def band_key(b):
    return f'height_{b[0]}_{b[1]}m'


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/experiment-river/perfil-baixo')
    runs = sorted(p.parent for p in root.glob('*/seed-*/run_info.txt'))
    if not runs:
        sys.exit(f'Nenhuma execução encontrada em {root}')
    rows = [run_metrics(r) for r in runs]

    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(root / 'summary.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    modes = [m for m in ['baseline', 'control', 'reserve', 'passive'] if any(r['mode'] == m for r in rows)]

    def table(cols):
        lines = ['| Modo | Execuções | ' + ' | '.join(c[1] for c in cols) + ' |',
                 '|---|---|' + '---|' * len(cols)]
        for mode in modes:
            sel = [r for r in rows if r['mode'] == mode]
            cells = []
            for key, _, dec in cols:
                vals = [r[key] for r in sel if key in r]
                mean = statistics.mean(vals)
                sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
                cells.append(f'{mean:.{dec}f} ± {sd:.{dec}f}')
            lines.append(f'| {mode} | {len(sel)} | ' + ' | '.join(cells) + ' |')
        return '\n'.join(lines) + '\n'

    main_table = table([('nodes_without_lower_neighbour', 'Nós sem vizinho mais baixo', 0),
                        ('riverbed_error_mean', 'Erro médio no leito', 3),
                        ('riverbed_error_max', 'Erro máximo no leito', 3),
                        ('quantization_floor_mean', 'Piso de quantização', 3),
                        ('valley_by_rank_pct', 'Abaixo das margens imediatas, por senha (%)', 1),
                        ('valley_by_height_pct', 'Abaixo das margens imediatas, por altura (%)', 1),
                        ('ms_growth', 'Crescimento (ms)', 0)])
    profile_table = table([(band_key(b), f'{b[0]}–{b[1]} m', 3) for b in BANDS])

    # Efeito do rio: quanto o corredor de 0–60 m fica mais baixo que no controle (mesmas sementes)
    control = {r['seed']: r for r in rows if r['mode'] == 'control'}
    effect_lines = []
    if control:
        effect_lines = ['| Modo | Rebaixamento do corredor 0–60 m em relação ao controle |', '|---|---|']
        for mode in modes:
            if mode == 'control':
                continue
            diffs = []
            for r in rows:
                c = control.get(r['seed'])
                if r['mode'] == mode and c:
                    corridor = lambda x: (x[band_key((0, 30))] + x[band_key((30, 60))]) / 2
                    diffs.append(corridor(c) - corridor(r))
            sd = statistics.stdev(diffs) if len(diffs) > 1 else 0.0
            effect_lines.append(f'| {mode} | {statistics.mean(diffs):+.3f} ± {sd:.3f} |')
    effect_table = '\n'.join(effect_lines) + '\n' if effect_lines else ''

    text = ('# Resumo do experimento do rio\n\nMédia ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] '
            '(uma caixa do histograma ≈ 0,09).\n\n' + main_table +
            '\n## Perfil transversal: altura média por distância até o rio\n\n' + profile_table +
            ('\n## Efeito do rio (positivo = corredor mais baixo que no controle)\n\n' + effect_table if effect_table else ''))
    (root / 'summary.md').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
