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
        'mode': run_dir.parent.name,  # nome da pasta (ex.: channel-d1), mais específico que info['mode']
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
        dist_river = {i: min(math.dist(pos[i], pos[j]) for j in river) for i in nodes}
        bands = {b: [] for b in BANDS}
        for i, r in nodes.items():
            if r['coast'] == '1':
                continue
            for b in BANDS:
                if b[0] <= dist_river[i] < b[1]:
                    bands[b].append(height[i])
        for b, vals in bands.items():
            if vals:
                m[band_key(b)] = statistics.mean(vals)

        # Forma do vale.
        # Cruzamentos: quantas vezes a altura muda entre nós consecutivos do rio (cada mudança é uma
        # isolinha cruzando o rio; sem cruzamento não há o "V" das curvas de nível).
        # Margens: nós a 20-60 m do nó do rio e a pelo menos 20 m do traçado, separados em esquerda e
        # direita (olhando da foz para a nascente) pela direção local do rio.
        # Leito entalhado: o nó do rio fica pelo menos um nível abaixo da média da margem esquerda E da
        # direita. (A média das duas margens juntas esconde degraus: um lado alto compensa o outro.)
        ordered = sorted(river, key=lambda i: int(nodes[i]['river_index']))
        along = [height[i] for i in ordered]
        level = statistics.median(b - a for a, b in zip(keys, keys[1:]))
        incised = 0
        left_rel, right_rel = [], []
        for k, i in enumerate(ordered):
            a, b = pos[ordered[max(0, k - 1)]], pos[ordered[min(len(ordered) - 1, k + 1)]]
            t = (b[0] - a[0], b[1] - a[1])
            left, right = [], []
            for j in nodes:
                if nodes[j]['coast'] == '1' or dist_river[j] < 20 or not 20 <= math.dist(pos[i], pos[j]) <= 60:
                    continue
                v = (pos[j][0] - pos[i][0], pos[j][1] - pos[i][1])
                (left if t[0] * v[1] - t[1] * v[0] > 0 else right).append(height[j])
            if not left or not right:
                continue
            dl, dr = statistics.mean(left) - height[i], statistics.mean(right) - height[i]
            left_rel.append(dl)
            right_rel.append(dr)
            if dl >= level - 1e-9 and dr >= level - 1e-9:
                incised += 1
        m['river_contour_crossings'] = sum(1 for a, b in zip(along, along[1:]) if a != b)
        m['riverbed_incised_both_pct'] = 100.0 * incised / len(left_rel)
        m['bank_left_minus_bed'] = statistics.mean(left_rel)
        m['bank_right_minus_bed'] = statistics.mean(right_rel)
        m['bank_asymmetry'] = m['bank_left_minus_bed'] - m['bank_right_minus_bed']
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

    known = ['baseline', 'control', 'reserve', 'passive', 'channel']
    present = {r['mode'] for r in rows}
    modes = [m for m in known if m in present] + sorted(present - set(known))

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
    shape_table = table([('river_contour_crossings', 'Isolinhas que cruzam o rio', 1),
                         ('riverbed_incised_both_pct', 'Leito entalhado nos dois lados (%)', 1),
                         ('bank_left_minus_bed', 'Margem esquerda − leito', 3),
                         ('bank_right_minus_bed', 'Margem direita − leito', 3),
                         ('bank_asymmetry', 'Assimetria (esquerda − direita)', 3)])
    profile_table = table([(band_key(b), f'{b[0]}–{b[1]} m', 3) for b in BANDS])

    # Efeito do rio: quanto o corredor de 0–60 m fica mais baixo que no controle (mesmas sementes)
    control = {r['seed']: r for r in rows if r['mode'] == 'control'}
    effect_lines = []
    if control:
        effect_lines = ['| Modo | Rebaixamento do corredor 0–60 m | Assimetria extra (degrau) |', '|---|---|---|']
        corridor = lambda x: (x[band_key((0, 30))] + x[band_key((30, 60))]) / 2
        for mode in modes:
            if mode == 'control':
                continue
            cor, asym = [], []
            for r in rows:
                c = control.get(r['seed'])
                if r['mode'] == mode and c:
                    cor.append(corridor(c) - corridor(r))
                    asym.append(r['bank_asymmetry'] - c['bank_asymmetry'])
            fmt = lambda v: f'{statistics.mean(v):+.3f} ± {statistics.stdev(v) if len(v) > 1 else 0.0:.3f}'
            effect_lines.append(f'| {mode} | {fmt(cor)} | {fmt(asym)} |')
    effect_table = '\n'.join(effect_lines) + '\n' if effect_lines else ''

    text = ('# Resumo do experimento do rio\n\nMédia ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] '
            '(uma caixa do histograma ≈ 0,09).\n\n' + main_table +
            '\n## Forma do vale\n\n' + shape_table +
            '\n## Perfil transversal: altura média por distância até o rio\n\n' + profile_table +
            ('\n## Efeito do rio em relação ao controle (mesmas sementes)\n\nRebaixamento: positivo = corredor mais baixo que no controle. Assimetria extra: assimetria do modo menos a do controle; perto de 0 = sem degrau criado pelo rio.\n\n' + effect_table if effect_table else ''))
    (root / 'summary.md').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
