#!/usr/bin/env python3
"""Gera um perfil de leito que acompanha o terreno natural.

Uso: python3 scripts/make_profile.py <rio.csv> <pasta-do-controle> <margem> <saida.csv>
Ex.: python3 scripts/make_profile.py experiments/river-fig11-perfil-alto.csv \
         results/experiment-river/perfil-baixo/control 0.1 experiments/river-fig11-perfil-terreno.csv

Para cada ponto do traçado: altura natural = média da altura dos nós a até 30 m do ponto, em todas
as execuções do controle (P uniforme, sem rio). Leito = natural - margem, nunca abaixo de 0 e nunca
descendo rio acima (máximo acumulado da foz para a nascente).
"""
import csv
import math
import statistics
import sys
from pathlib import Path

RADIUS = 30.0

river_csv, control_dir, margin, out = sys.argv[1], Path(sys.argv[2]), float(sys.argv[3]), sys.argv[4]

pts = []
for line in open(river_csv):
    if line[:1] in '-0123456789':
        x, y = map(float, line.split(',')[:2])
        pts.append((x, y))

runs = [[(float(r['x']), float(r['y']), float(r['height'])) for r in csv.DictReader(open(f))]
        for f in sorted(control_dir.glob('seed-*/nodes.csv'))]
if not runs:
    sys.exit(f'Nenhum nodes.csv em {control_dir}/seed-*/')

profile, natural_list, top = [], [], 0.0
for p in pts:
    near = [h for run in runs for (x, y, h) in run if math.dist((x, y), p) <= RADIUS]
    natural = statistics.mean(near)
    top = max(top, max(0.0, natural - margin))
    natural_list.append(natural)
    profile.append(top)

with open(out, 'w') as f:
    f.write(f'# Rio da Figura 11 (braco esquerdo), mesmo tracado dos outros perfis.\n')
    f.write(f'# elevation = altura natural (media de {len(runs)} execucoes de controle, nos a ate {RADIUS:.0f} m) - {margin},\n')
    f.write('# sem ficar abaixo de 0 e sem descer rio acima. Gerado por scripts/make_profile.py.\n')
    f.write('x,y,elevation\n')
    for (x, y), e in zip(pts, profile):
        f.write(f'{x:.1f},{y:.1f},{e:.4f}\n')

print(f'{len(pts)} pontos; leito de {profile[0]:.3f} a {profile[-1]:.3f}; '
      f'natural de {min(natural_list):.3f} a {max(natural_list):.3f} -> {out}')
