#!/usr/bin/env python3
"""Gera results/experiment-river/index.html: comparação lado a lado dos modos.

Uso: python3 scripts/compare_page.py [results/experiment-river] [experiments/river-fig11-perfil-alto.csv]
Abre no navegador, sem internet. Mostra as tabelas summary.md de cada perfil, as isolinhas e o
terreno de cada modo (seletores de perfil e semente) e o traçado do rio (CSV) por cima das imagens.
"""
import csv
import html
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'results/experiment-river')
river_csv = Path(sys.argv[2] if len(sys.argv) > 2 else 'experiments/river-fig11-perfil-alto.csv')

profiles = sorted(p.name for p in root.glob('perfil-*') if (p / 'summary.md').exists())
modes = [m for m in ['baseline', 'control', 'reserve', 'passive', 'channel'] if any((root / p / m).is_dir() for p in profiles)]
seeds = sorted({d.name[len('seed-'):] for p in profiles for m in modes for d in (root / p / m).glob('seed-*') if d.is_dir()},
               key=int)

# Rio: metros no domínio Box2(500) -> coordenadas 0..1000 com o topo = y máximo
# (mesma orientação do terreno e das isolinhas, que usam matrix(1,0,0,-1,500,500))
pts = []
for row in csv.reader(l for l in open(river_csv) if not l.startswith('#')):
    try:
        x, y = float(row[0]), float(row[1])
    except (ValueError, IndexError):
        continue
    pts.append(f'{x + 500:.1f},{500 - y:.1f}')
overlay = f'<svg viewBox="0 0 1000 1000" class="river"><polyline points="{" ".join(pts)}"/></svg>'


def md_table(path):
    rows = [l for l in path.read_text().splitlines() if l.startswith('|')]
    head = ''.join(f'<th>{html.escape(c.strip())}</th>' for c in rows[0].strip('|').split('|'))
    body = ''.join('<tr>' + ''.join(f'<td>{html.escape(c.strip())}</td>' for c in r.strip('|').split('|')) + '</tr>'
                   for r in rows[2:])
    return f'<div class="tablewrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


tables = ''.join(f'<h2 class="ptitle">{html.escape(p)}</h2>{md_table(root / p / "summary.md")}' for p in profiles)

desc = {
    'baseline': 'Método original: rio pintado no mapa de probabilidade P (Figura 11).',
    'control': 'Controle: mapa P uniforme e nenhum rio (isola o efeito do rio).',
    'reserve': 'Proposta, D1-A: nós do rio reservados até a senha-alvo.',
    'passive': 'Proposta, D1-B: nós do rio ativados na senha-alvo ou antes, se o crescimento chegar.',
    'channel': 'Proposta, canal: como reserve, mas o crescimento não se espalha a partir do rio (leito entalhado).',
}
cols = ''.join(f'''
<section class="col">
  <h2>{m}</h2><p class="desc">{desc[m]}</p>
  <h3>Isolinhas</h3><div class="pic"><img class="isos" data-mode="{m}" data-file="isos.svg" alt="Isolinhas, modo {m}">{overlay}</div>
  <h3>Terreno (claro = alto)</h3><div class="pic"><img data-mode="{m}" data-file="terrain.png" alt="Terreno, modo {m}">{overlay}</div>
</section>''' for m in modes)

page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Experimento do rio</title>
<style>
:root {{ --bg:#f6f3ec; --fg:#1f2a2e; --muted:#5f6b66; --line:#ddd6c8; --card:#fdfbf6; --river:#00a37a; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1f2a2e; --fg:#f6f3ec; --muted:#bfcbc6; --line:#3a474c; --card:#26343a; --river:#3fd6a8; }} }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; margin:0; padding:16px; }}
h1 {{ margin:0 0 4px; font-size:24px; }} .muted {{ color:var(--muted); }} .ptitle {{ font-size:18px; margin:16px 0 4px; }}
.controls {{ display:flex; gap:16px; flex-wrap:wrap; align-items:center; margin:16px 0; position:sticky; top:0; background:var(--bg); padding:8px 0; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }} th,td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; }}
.tablewrap {{ overflow-x:auto; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; }}
.col {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px; }}
.col h2 {{ margin:0; font-size:20px; }} .col h3 {{ font-size:14px; margin:12px 0 4px; color:var(--muted); }}
.desc {{ margin:4px 0 0; font-size:14px; color:var(--muted); }}
.pic {{ position:relative; }} img {{ width:100%; display:block; border-radius:6px; }} .isos {{ background:#fff; }}
.river {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }}
.river polyline {{ fill:none; stroke:var(--river); stroke-width:5; stroke-dasharray:14 8; opacity:.95; }}
body.hide-river .river {{ display:none; }}
</style></head><body>
<h1>Experimento do rio</h1>
<p class="muted">Mesma máscara, histograma e ~3000 partículas em todos os modos. Alturas normalizadas em [0, 1].
Perfil alto: leito de 0 a 0,40; perfil baixo: leito de 0 a 0,15. Gerado por scripts/compare_page.py.</p>
{tables}
<div class="controls">
  <label>Perfil <select id="profile">{''.join(f'<option value="{p}">{p}</option>' for p in profiles)}</select></label>
  <label>Semente <select id="seed">{''.join(f'<option>{s}</option>' for s in seeds)}</select></label>
  <label><input type="checkbox" id="river" checked> Mostrar o traçado do rio (tracejado)</label>
</div>
<div class="grid">{cols}</div>
<script>
function update() {{
  const p = document.getElementById('profile').value, s = document.getElementById('seed').value;
  document.querySelectorAll('img[data-mode]').forEach(i => {{ i.src = p + '/' + i.dataset.mode + '/seed-' + s + '/' + i.dataset.file; }});
}}
document.getElementById('profile').addEventListener('change', update);
document.getElementById('seed').addEventListener('change', update);
document.getElementById('river').addEventListener('change', e => document.body.classList.toggle('hide-river', !e.target.checked));
update();
</script>
</body></html>
'''
(root / 'index.html').write_text(page)
print(f'Página: {root / "index.html"}')
