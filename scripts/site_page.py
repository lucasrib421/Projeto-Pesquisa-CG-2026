#!/usr/bin/env python3
"""Gera index.html na raiz do repositório: página de apresentação dos resultados (GitHub Pages).

Uso: python3 scripts/site_page.py
Os números vêm dos summary.csv dos experimentos (nada é digitado à mão). Rode de novo depois de
refazer os experimentos.
"""
import csv
import html
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROFILE = 'perfil-baixo'
SEED = '239'
RIVER_CSV = REPO / 'experiments' / 'river-fig11-perfil-baixo.csv'
RIVER_DIR = REPO / 'results' / 'experiment-river' / PROFILE
DELAY_DIR = REPO / 'results' / 'experiment-delay' / PROFILE


def load(path):
    return list(csv.DictReader(open(path)))


def corridor(r):
    return (float(r['height_0_30m']) + float(r['height_30_60m'])) / 2


def summarize(rows, mode):
    """Médias entre sementes, com efeitos relativos ao controle da mesma tabela (mesmas sementes)."""
    control = {r['seed']: r for r in rows if r['mode'] == 'control'}
    sel = [r for r in rows if r['mode'] == mode]
    mean = lambda f: statistics.mean(f(r) for r in sel)
    out = {
        'runs': len(sel),
        'pits': mean(lambda r: float(r['nodes_without_lower_neighbour'])),
        'incised': mean(lambda r: float(r['riverbed_incised_both_pct'])),
    }
    if mode != 'control':
        out['corridor'] = mean(lambda r: corridor(control[r['seed']]) - corridor(r))
        out['step'] = mean(lambda r: float(r['bank_asymmetry']) - float(control[r['seed']]['bank_asymmetry']))
    if mode not in ('control', 'baseline'):
        out['error'] = mean(lambda r: float(r['riverbed_error_mean']))
    return out


def num(x, dec=3, sign=False):
    s = f'{x:+.{dec}f}' if sign else f'{x:.{dec}f}'
    return s.replace('.', ',').replace('-', '−')


river_rows, delay_rows = load(RIVER_DIR / 'summary.csv'), load(DELAY_DIR / 'summary.csv')
variants = [
    ('baseline', 'Método original', 'Rio pintado no mapa de probabilidade P (Figura 11 do artigo).',
     river_rows, 'results/experiment-river', 'baseline'),
    ('control', 'Controle', 'Sem rio e mapa P uniforme: mostra o terreno natural.',
     delay_rows, 'results/experiment-delay', 'control'),
    ('reserve', 'Rio como semente', 'Rio com altura explícita que espalha o crescimento na hora (D = 0).',
     delay_rows, 'results/experiment-delay', 'channel-d0'),
    ('dnever', 'Canal (nunca espalha)', 'O rio recebe a altura pedida e nunca espalha o crescimento.',
     delay_rows, 'results/experiment-delay', 'channel-dnever'),
    ('d2', 'Canal com atraso D = 2', 'O rio espalha o crescimento 2 níveis de altura depois de ativado.',
     delay_rows, 'results/experiment-delay', 'channel-d2'),
]
stats = {key: summarize(rows, mode) for key, _, _, rows, _, mode in variants}

# Traçado do rio: metros no domínio Box2(500) -> 0..1000 com o topo = y máximo (mesma orientação das imagens)
pts = []
for row in csv.reader(l for l in open(RIVER_CSV) if not l.startswith('#')):
    try:
        x, y = float(row[0]), float(row[1])
    except (ValueError, IndexError):
        continue
    pts.append(f'{x + 500:.1f},{500 - y:.1f}')
overlay = f'<svg viewBox="0 0 1000 1000" class="river" aria-hidden="true"><polyline points="{" ".join(pts)}"/></svg>'

shown = [v for v in variants if v[0] in ('baseline', 'control', 'dnever', 'd2')]
cards = ''.join(f'''
<figure class="card{' best' if key == 'd2' else ''}">
  <figcaption><strong>{html.escape(title)}</strong><span>{html.escape(desc)}</span></figcaption>
  <div class="pic"><img src="{base}/{PROFILE}/{mode}/seed-{SEED}/isos.svg" alt="Isolinhas: {html.escape(title)}" class="isos" loading="lazy">{overlay}</div>
  <div class="pic"><img src="{base}/{PROFILE}/{mode}/seed-{SEED}/terrain.png" alt="Terreno: {html.escape(title)}" loading="lazy">{overlay}</div>
</figure>''' for key, title, desc, _, base, mode in shown)

rows_html = ''
for key, title, _, _, _, _ in variants:
    s = stats[key]
    err = num(s['error']) if 'error' in s else '—'
    cor = num(s['corridor'], sign=True) if 'corridor' in s else '—'
    step = num(s['step'], sign=True) if 'step' in s else '—'
    rows_html += (f'<tr{" class=\"best\"" if key == "d2" else ""}><td>{html.escape(title)}</td><td>{num(s["pits"], 0)}</td>'
                  f'<td>{err}</td><td>{num(s["incised"], 1)}%</td><td>{cor}</td><td>{step}</td></tr>')

d2, never, base = stats['d2'], stats['dnever'], stats['baseline']
page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rios com elevação explícita</title>
<meta name="description" content="Projeto de pesquisa em Computação Gráfica: rios com elevação explícita na síntese de terrenos por iso-contornos.">
<style>
:root {{ --bg:#f6f3ec; --fg:#1f2a2e; --muted:#5f6b66; --line:#ddd6c8; --card:#fdfbf6; --accent:#a84e2a; --river:#00a37a; --best:#e9f3ee; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1f2a2e; --fg:#f6f3ec; --muted:#bfcbc6; --line:#3a474c; --card:#26343a; --accent:#e08a5f; --river:#3fd6a8; --best:#22413a; }} }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.6 system-ui, sans-serif; margin:0; }}
main {{ max-width:1200px; margin:0 auto; padding:24px 16px 48px; }}
h1 {{ font-size:30px; line-height:1.2; margin:0 0 8px; }} h2 {{ font-size:22px; margin:40px 0 12px; }}
.eyebrow {{ color:var(--accent); font-weight:700; letter-spacing:2px; text-transform:uppercase; font-size:13px; margin:0 0 8px; }}
.muted {{ color:var(--muted); }} a {{ color:var(--accent); }}
.lead {{ font-size:18px; max-width:820px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; }}
.card {{ margin:0; background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px; }}
.card.best {{ border:2px solid var(--river); }}
.card figcaption {{ display:flex; flex-direction:column; gap:2px; margin-bottom:8px; font-size:14px; }}
.card figcaption span {{ color:var(--muted); }}
.pic {{ position:relative; margin-top:8px; }} .pic img {{ width:100%; display:block; border-radius:6px; }} .isos {{ background:#fff; }}
.river {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }}
.river polyline {{ fill:none; stroke:var(--river); stroke-width:5; stroke-dasharray:14 8; }}
body.hide-river .river {{ display:none; }}
.tablewrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:15px; }}
th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; }} th {{ background:var(--card); }}
tr.best td {{ background:var(--best); font-weight:600; }}
.cols {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; }}
.box {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px; }}
.box h3 {{ margin:0 0 8px; font-size:17px; }}
code, pre {{ font-family:ui-monospace, monospace; font-size:14px; }}
pre {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px; overflow-x:auto; }}
label {{ display:inline-flex; gap:8px; align-items:center; margin:8px 0; }}
</style></head>
<body><main>
<p class="eyebrow">Computação Gráfica · IFNMG 2026/2 · Prof. Wagner Ferreira de Barros</p>
<h1>Rios com elevação explícita na síntese de terrenos por iso-contornos</h1>
<p class="muted">Equipe: Lucas Santos · João Victor · Luis Fhilipe ·
<a href="https://github.com/lucasrib421/Projeto-Pesquisa-CG-2026">repositório</a> ·
artigo base: Huftier et al., <a href="https://doi.org/10.1111/cgf.70389"><i>Terrain Synthesis and Authoring based on Iso-Contours</i></a>, CGF 2026</p>

<p class="lead">O artigo gera terrenos como curvas de nível aninhadas: um crescimento (<i>Open Eden Growth</i>) avança da costa para o interior,
e a ordem de chegada de cada ponto vira a altura. Na seção 6.6, os autores apontam que <b>rios</b> continuam difíceis: só podem ser sugeridos
pintando um mapa de probabilidade P. A nossa proposta deixa o usuário <b>desenhar o rio com a altura do leito explícita</b>: os pontos do rio
viram pontos de partida do crescimento, cada um na altura pedida.</p>

<h2>Resultado principal</h2>
<p>Mesma máscara, histograma e ~3000 pontos da Figura 11 do artigo; semente aleatória {SEED}; leito pedido de 0 (foz) a 0,15 (nascente).
O canal com atraso D = 2 é a primeira variante em que o rio aparece com <b>forma de vale</b>: leito abaixo das duas margens, dentro de um corredor rebaixado.</p>
<label><input type="checkbox" id="river" checked> Mostrar o traçado do rio (tracejado)</label>
<div class="grid">{cards}</div>

<h2>Números (média de 5 sementes aleatórias)</h2>
<div class="tablewrap"><table>
<thead><tr><th>Variante</th><th>Nós sem vizinho mais baixo</th><th>Erro no leito</th><th>Leito entalhado nos dois lados</th><th>Corredor rebaixado</th><th>Degrau entre margens</th></tr></thead>
<tbody>{rows_html}</tbody></table></div>
<p class="muted">Alturas normalizadas em [0, 1]; o terreno tem 12 alturas possíveis (passo ≈ 0,09), então o menor erro possível no leito é ≈ 0,023.
<b>Nós sem vizinho mais baixo</b> = 0 significa que a garantia do artigo (sem bacias endorreicas) se mantém.
<b>Corredor</b> e <b>degrau</b> são medidos em relação ao controle, com as mesmas sementes.</p>

<div class="cols">
<div class="box"><h3>O que aprendemos</h3><ul>
<li>A proposta controla a altura do leito (erro no piso de quantização) sem criar poças.</li>
<li>Se o rio espalha o crescimento na hora, ele "puxa" as margens junto: o terreno desce num corredor largo, mas sem forma de vale. O método original faz o mesmo (entalhe {num(base['incised'], 1)}%).</li>
<li>Se o rio nunca espalha, o leito fica entalhado ({num(never['incised'], 1)}%), mas os pontos do rio viram uma parede e criam um degrau entre as margens ({num(never['step'], sign=True)}).</li>
<li>Com um atraso de 2 níveis, os dois efeitos se combinam: entalhe de {num(d2['incised'], 1)}%, corredor {num(d2['corridor'], sign=True)} e sem degrau.</li>
</ul></div>
<div class="box"><h3>Limitações e próximos passos</h3><ul>
<li>O canal tem a largura de um ponto do grafo (~17 m); o rio da Figura 11 tem ~50 m.</li>
<li>Um único traçado (braço esquerdo do rio da Figura 11) e perfis de leito escolhidos pela equipe.</li>
<li>Métricas medidas nas 12 alturas do grafo; área de drenagem e ordem de Strahler ainda não medidas.</li>
<li>Os resultados de várias métricas iniciais estavam errados e foram corrigidos; o histórico está no repositório.</li>
</ul></div>
</div>

<h2>Explorar</h2>
<ul>
<li><a href="results/experiment-delay/index.html">Varredura do atraso D</a>: todas as variantes de canal, por perfil e semente.</li>
<li><a href="results/experiment-river/index.html">Experimento do rio</a>: baseline, controle, reserve, passive e channel, em 3 perfis de leito.</li>
<li><a href="results/baseline/fig11/river_isos.svg">Baseline reproduzida</a>: Figura 11 do artigo gerada pelo código original.</li>
<li><a href="https://github.com/lucasrib421/Projeto-Pesquisa-CG-2026#readme">README</a>: métodos, métricas, decisões e uso de ferramentas de IA.</li>
</ul>

<h2>Reproduzir</h2>
<p>Ubuntu (testado no WSL2), Qt 6, GLEW e CMake; detalhes no README.</p>
<pre><code>bash scripts/setup.sh              # compila
bash scripts/baseline-fig11.sh     # baseline: Figura 11 do artigo
bash scripts/experiment-river.sh   # experimento do rio (~10 min)
bash scripts/experiment-delay.sh   # varredura do atraso (~8 min)
python3 scripts/site_page.py       # regenera esta página</code></pre>
<p class="muted">Página gerada por <code>scripts/site_page.py</code> a partir dos arquivos <code>summary.csv</code>.</p>
</main>
<script>
document.getElementById('river').addEventListener('change', e => document.body.classList.toggle('hide-river', !e.target.checked));
</script>
</body></html>
'''
(REPO / 'index.html').write_text(page)
(REPO / '.nojekyll').write_text('')
print(f'Página: {REPO / "index.html"}')
