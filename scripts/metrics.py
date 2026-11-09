#!/usr/bin/env python3
"""Métricas do experimento do rio.

Uso: python3 scripts/metrics.py results/experiment-river

Lê <pasta>/<modo>/seed-<n>/{nodes.csv,edges.csv,run_info.txt}, gerados por
`AppIso --experiment`, e escreve <pasta>/summary.csv (uma linha por execução)
e <pasta>/summary.md (média e desvio padrão por modo).
"""
import csv
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
        banks_ok = 0
        for i in river:
            banks = [j for j in neigh[i] if j not in river]
            if banks and all(rank[i] < rank[j] for j in banks):
                banks_ok += 1
        m.update({
            'riverbed_error_mean': statistics.mean(err),
            'riverbed_error_max': max(err),
            'quantization_floor_mean': statistics.mean(floor),
            'river_in_valley_pct': 100.0 * banks_ok / len(river),
        })
    return m


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/experiment-river')
    runs = sorted(p.parent for p in root.glob('*/seed-*/run_info.txt'))
    if not runs:
        sys.exit(f'Nenhuma execução encontrada em {root}')
    rows = [run_metrics(r) for r in runs]

    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(root / 'summary.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    cols = [('nodes_without_lower_neighbour', 'Nós sem vizinho mais baixo', 0),
            ('riverbed_error_mean', 'Erro médio no leito', 3),
            ('riverbed_error_max', 'Erro máximo no leito', 3),
            ('quantization_floor_mean', 'Piso de quantização', 3),
            ('river_in_valley_pct', 'Rio em vale (%)', 1),
            ('ms_growth', 'Crescimento (ms)', 0)]
    lines = ['| Modo | Execuções | ' + ' | '.join(c[1] for c in cols) + ' |',
             '|---|---|' + '---|' * len(cols)]
    for mode in ['baseline', 'reserve', 'passive']:
        sel = [r for r in rows if r['mode'] == mode]
        if not sel:
            continue
        cells = []
        for key, _, dec in cols:
            vals = [r[key] for r in sel if key in r]
            mean = statistics.mean(vals)
            sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
            cells.append(f'{mean:.{dec}f} ± {sd:.{dec}f}')
        lines.append(f'| {mode} | {len(sel)} | ' + ' | '.join(cells) + ' |')
    table = '\n'.join(lines) + '\n'
    (root / 'summary.md').write_text(
        '# Resumo do experimento do rio\n\nMédia ± desvio padrão entre sementes. Alturas normalizadas em [0, 1].\n\n' + table)
    print(table)


if __name__ == '__main__':
    main()
