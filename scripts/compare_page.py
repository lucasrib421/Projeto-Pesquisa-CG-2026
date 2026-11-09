#!/usr/bin/env python3
"""Gera results/experiment-river/index.html: comparação lado a lado dos modos.

Uso: python3 scripts/compare_page.py [results/experiment-river] [experiments/river-fig11.csv]
Abre no navegador, sem internet. Mostra a tabela de summary.md, isolinhas e terreno
de cada modo por semente, e o traçado do rio (CSV) sobre o terreno.
"""
import csv
import html
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/experiment-river')
river_csv = Path(sys.argv[2] if len(sys.argv) > 2 else 'experiments/river-fig11.csv')

modes = [m for m in ['baseline', 'reserve', 'passive'] if (root / m).is_dir()]
seeds = sorted({p.name[len('seed-'):] for m in modes for p in (root / m).glob('seed-*') if p.is_dir()}, key=int)

# Rio: metros no domínio Box2(500) -> pixels da imagem do terreno (topo = y máximo)
pts = []
for row in csv.reader(l for l in open(river_csv) if not l.startswith('#')):
    try:
        x, y = float(row[0]), float(row[1])
    except (ValueError, IndexError):
        continue
    pts.append(f'{(x + 500) / 1000 * 512:.1f},{(500 - y) / 1000 * 512:.1f}')
polyline = ' '.join(pts)

# Tabela markdown de summary.md -> HTML
table_rows = [l for l in (root / 'summary.md').read_text().splitlines() if l.startswith('|')]
thead = ''.join(f'<th>{html.escape(c.strip())}</th>' for c in table_rows[0].strip('|').split('|'))
tbody = ''.join('<tr>' + ''.join(f'<td>{html.escape(c.strip())}</td>' for c in r.strip('|').split('|')) + '</tr>'
                for r in table_rows[2:])

desc = {
    'baseline': 'Método original: rio pintado no mapa de probabilidade P (Figura 11).',
    'reserve': 'Proposta, D1-A: nós do rio reservados até a senha-alvo.',
    'passive': 'Proposta, D1-B: nós do rio ativados na senha-alvo ou antes, se o crescimento chegar.',
}
cols = ''.join(f'''
<section class="col">
  <h2>{m}</h2><p class="desc">{desc[m]}</p>
  <h3>Isolinhas</h3><img class="isos" data-mode="{m}" data-file="isos.svg" alt="Isolinhas, modo {m}">
  <h3>Terreno (claro = alto)</h3>
  <div class="terrain"><img data-mode="{m}" data-file="terrain.png" alt="Terreno, modo {m}">
    <svg viewBox="0 0 512 512" class="river"><polyline points="{polyline}"/></svg></div>
</section>''' for m in modes)

page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Experimento do rio</title>
<style>
:root {{ --bg:#f6f3ec; --fg:#1f2a2e; --muted:#5f6b66; --line:#ddd6c8; --card:#fdfbf6; --river:#2f6b8a; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1f2a2e; --fg:#f6f3ec; --muted:#bfcbc6; --line:#3a474c; --card:#26343a; --river:#5fa3c9; }} }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; margin:0; padding:16px; }}
h1 {{ margin:0 0 4px; font-size:24px; }} .muted {{ color:var(--muted); }}
.controls {{ display:flex; gap:16px; flex-wrap:wrap; align-items:center; margin:16px 0; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }} th,td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; }}
.tablewrap {{ overflow-x:auto; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-top:16px; }}
.col {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px; }}
.col h2 {{ margin:0; font-size:20px; }} .col h3 {{ font-size:14px; margin:12px 0 4px; color:var(--muted); }}
.desc {{ margin:4px 0 0; font-size:14px; color:var(--muted); }}
img {{ width:100%; display:block; border-radius:6px; }} .isos {{ background:#fff; }}
.terrain {{ position:relative; }} .river {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }}
.river polyline {{ fill:none; stroke:var(--river); stroke-width:3; opacity:.9; }}
body.hide-river .river {{ display:none; }}
</style></head><body>
<h1>Experimento do rio</h1>
<p class="muted">Mesma máscara, histograma e ~3000 partículas em todos os modos. Alturas normalizadas em [0, 1]. Gerado por scripts/compare_page.py.</p>
<div class="tablewrap"><table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>
<div class="controls">
  <label>Semente <select id="seed">{''.join(f'<option>{s}</option>' for s in seeds)}</select></label>
  <label><input type="checkbox" id="river" checked> Mostrar o traçado do rio (CSV) sobre o terreno</label>
</div>
<div class="grid">{cols}</div>
<script>
function update() {{
  const s = document.getElementById('seed').value;
  document.querySelectorAll('img[data-mode]').forEach(i => {{ i.src = i.dataset.mode + '/seed-' + s + '/' + i.dataset.file; }});
}}
document.getElementById('seed').addEventListener('change', update);
document.getElementById('river').addEventListener('change', e => document.body.classList.toggle('hide-river', !e.target.checked));
update();
</script>
</body></html>
'''
(root / 'index.html').write_text(page)
print(f'Página: {root / "index.html"}')
