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
PAPER_URL = 'https://doi.org/10.1111/cgf.70389'
REPO_URL = 'https://github.com/lucasrib421/Projeto-Pesquisa-CG-2026'
SLIDES_URL = 'https://claude.ai/artifact/1UBaWMzWhfY5voAZN24pEk'


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

# (chave, título, linhas, pasta, modo)
variants = [
    ('baseline', 'Método original', river_rows, 'results/experiment-river', 'baseline'),
    ('control', 'Controle', delay_rows, 'results/experiment-delay', 'control'),
    ('reserve', 'Rio como semente (D = 0)', delay_rows, 'results/experiment-delay', 'channel-d0'),
    ('dnever', 'Canal que nunca espalha', delay_rows, 'results/experiment-delay', 'channel-dnever'),
    ('d2', 'Canal com atraso D = 2', delay_rows, 'results/experiment-delay', 'channel-d2'),
]
stats = {key: summarize(rows, mode) for key, _, rows, _, mode in variants}
where = {key: (base, mode) for key, _, _, base, mode in variants}
title = {key: t for key, t, _, _, _ in variants}

# Os quatro métodos mostrados em imagens: mecanismo e o que observar
methods = [
    ('baseline', 'Artigo',
     'O rio é <b>pintado no mapa de probabilidade P</b>. O crescimento passa mais rápido por essa faixa, então ela recebe senhas cedo e fica baixa.',
     'Uma faixa larga de terreno baixo ao longo do rio, sem leito entalhado. Não há como dizer a altura do leito.'),
    ('control', 'Referência',
     'Sem rio e com o mapa P uniforme: o crescimento avança igual em toda a região. É o <b>terreno natural</b>, contra o qual o corredor e o degrau são medidos.',
     'Nenhuma estrutura ao longo do traçado tracejado.'),
    ('dnever', 'Proposta',
     'Cada ponto do rio fica bloqueado até receber a <b>senha da altura pedida</b> e depois <b>nunca</b> é ponto de partida do crescimento. As margens são alcançadas pelo crescimento normal e ficam mais altas que o leito.',
     'Leito entalhado, mas o rio vira uma <b>parede</b>: o lado leste só é alcançado contornando o rio e fica mais alto (degrau).'),
    ('d2', 'Proposta · melhor resultado',
     'Igual ao anterior, mas <b>2 níveis de altura depois</b> de receber a senha o ponto do rio passa a espalhar o crescimento. Primeiro as margens ficam acima do leito; depois o rio rebaixa o entorno e deixa o crescimento atravessar.',
     'Canal dentro de um vale mais escuro dos dois lados, <b>sem degrau</b>.'),
]

# Traçado do rio: metros no domínio Box2(500) -> 0..1000 com o topo = y máximo (mesma orientação das imagens)
pts = []
for row in csv.reader(l for l in open(RIVER_CSV) if not l.startswith('#')):
    try:
        x, y = float(row[0]), float(row[1])
    except (ValueError, IndexError):
        continue
    pts.append(f'{x + 500:.1f},{500 - y:.1f}')
overlay = f'<svg viewBox="0 0 1000 1000" class="river" aria-hidden="true"><polyline points="{" ".join(pts)}"/></svg>'


def badges(key):
    s = stats[key]
    if key == 'control':
        return '<li><span>Referência das medidas</span></li>'
    return (f'<li><b>{num(s["incised"], 0)}%</b><span>leito entalhado</span></li>'
            f'<li><b>{num(s["corridor"], 2, True)}</b><span>corredor rebaixado</span></li>'
            f'<li><b>{num(s["step"], 2, True)}</b><span>degrau</span></li>')


cards = ''
for key, tag, how, see in methods:
    base, mode = where[key]
    cards += f'''
<article class="method{' best' if key == 'd2' else ''}">
  <p class="tag">{tag}</p>
  <h3>{html.escape(title[key])}</h3>
  <ul class="badges">{badges(key)}</ul>
  <div class="viewer" data-view="0">
    <div class="pic"><img src="{base}/{PROFILE}/{mode}/seed-{SEED}/isos.svg" alt="Isolinhas: {html.escape(title[key])}" class="isos" loading="lazy">{overlay}</div>
    <div class="pic"><img src="{base}/{PROFILE}/{mode}/seed-{SEED}/terrain.png" alt="Terreno: {html.escape(title[key])}" loading="lazy">{overlay}</div>
    <div class="nav">
      <button type="button" class="prev" aria-label="Imagem anterior">‹</button>
      <span class="label" aria-live="polite">Isolinhas</span>
      <button type="button" class="next" aria-label="Próxima imagem">›</button>
    </div>
  </div>
  <h4>Como funciona</h4><p>{how}</p>
  <h4>O que observar</h4><p>{see}</p>
</article>'''

rows_html = ''
for key, _, _, _, _ in variants:
    s = stats[key]
    err = num(s['error']) if 'error' in s else '—'
    cor = num(s['corridor'], sign=True) if 'corridor' in s else '—'
    step = num(s['step'], sign=True) if 'step' in s else '—'
    cls = ' class="best"' if key == 'd2' else ''
    rows_html += (f'<tr{cls}><th scope="row">{html.escape(title[key])}</th><td>{num(s["pits"], 0)}</td>'
                  f'<td>{err}</td><td>{num(s["incised"], 1)}%</td><td>{cor}</td><td>{step}</td></tr>')

d2, never, base = stats['d2'], stats['dnever'], stats['baseline']
page = f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rios com elevação explícita</title>
<meta name="description" content="Projeto de pesquisa em Computação Gráfica: rios com elevação explícita na síntese de terrenos por iso-contornos.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#f6f3ec; --fg:#1f2a2e; --muted:#5b6662; --line:#ddd6c8; --card:#fdfbf6; --accent:#a84e2a;
        --river:#0b8f6c; --best:#e6f2ec; --chip:#efe9dd; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#1b2427; --fg:#f2efe8; --muted:#b8c4bf; --line:#34434a; --card:#233036;
        --accent:#e59a72; --river:#3fd6a8; --best:#1f3d36; --chip:#2c3b42; }} }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font:16px/1.65 Inter, system-ui, sans-serif; margin:0; }}
main {{ max-width:1180px; margin:0 auto; padding:0 16px 64px; }}
h1, h2, h3 {{ font-family:'Source Serif 4', Georgia, serif; font-weight:600; line-height:1.2; }}
h2 {{ font-size:26px; margin:56px 0 8px; }}
h2 + .intro {{ margin-top:0; color:var(--muted); max-width:760px; }}
a {{ color:var(--accent); text-decoration:none; }} a:hover {{ text-decoration:underline; }}

.hero {{ padding:56px 0 32px; border-bottom:1px solid var(--line); }}
.kicker {{ font-size:13px; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }}
.hero h1 {{ font-size:clamp(32px, 5vw, 48px); margin:0; }}
.hero .subtitle {{ font-family:'Source Serif 4', Georgia, serif; font-size:clamp(20px, 3vw, 26px); color:var(--muted); margin:4px 0 20px; }}
.hero .team {{ margin:0 0 16px; font-size:15px; color:var(--muted); }}
.pills {{ display:flex; gap:8px; flex-wrap:wrap; }}
.pill {{ font-size:14px; font-weight:500; padding:6px 14px; border:1px solid var(--line); border-radius:999px; background:var(--card); color:var(--fg); }}
.pill:hover {{ border-color:var(--accent); text-decoration:none; }}

.summary {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px; margin-top:32px; }}
.summary div {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px; }}
.summary h3 {{ font-size:18px; margin:0 0 6px; color:var(--accent); }}
.summary p {{ margin:0; }}

.steps {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:16px; counter-reset:step; margin-top:16px; }}
.steps div {{ border-left:3px solid var(--accent); padding:4px 0 4px 16px; }}
.steps h3 {{ font-size:17px; margin:0 0 4px; }}
.steps h3::before {{ counter-increment:step; content:counter(step) ". "; color:var(--accent); }}
.steps p {{ margin:0; }}

.legend {{ display:flex; gap:20px; flex-wrap:wrap; font-size:14px; color:var(--muted); margin:16px 0; align-items:center; }}
.legend span {{ display:inline-flex; gap:8px; align-items:center; }}
.ramp {{ width:72px; height:10px; border-radius:5px; background:linear-gradient(90deg, #5470e8, #d9dbe6, #e05a45); }}
.gray {{ width:72px; height:10px; border-radius:5px; background:linear-gradient(90deg, #000, #fff); border:1px solid var(--line); }}
.dash {{ width:32px; border-top:3px dashed var(--river); }}
label {{ display:inline-flex; gap:8px; align-items:center; cursor:pointer; }}

.methods {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(min(100%, 460px), 1fr)); gap:20px; }}
.method {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; display:flex; flex-direction:column; }}
.method.best {{ border:2px solid var(--river); }}
.method .tag {{ font-size:12px; letter-spacing:1px; text-transform:uppercase; color:var(--muted); margin:0; }}
.method.best .tag {{ color:var(--river); font-weight:600; }}
.method h3 {{ font-size:20px; margin:2px 0 10px; }}
.method h4 {{ font-size:13px; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin:14px 0 2px; }}
.method p {{ margin:0; font-size:15px; }}
.badges {{ list-style:none; padding:0; margin:0 0 10px; display:flex; gap:6px; flex-wrap:wrap; }}
.badges li {{ background:var(--chip); border-radius:8px; padding:4px 8px; font-size:12px; display:flex; flex-direction:column; line-height:1.3; }}
.badges b {{ font-size:15px; }} .badges span {{ color:var(--muted); }}
.viewer {{ position:relative; }}
.viewer .pic {{ display:none; }}
.viewer[data-view="0"] .pic:nth-of-type(1), .viewer[data-view="1"] .pic:nth-of-type(2) {{ display:block; }}
.pic {{ position:relative; }} .pic img {{ width:100%; aspect-ratio:1; display:block; border-radius:8px; }} .isos {{ background:#fff; }}
.nav {{ display:flex; align-items:center; justify-content:center; gap:12px; margin-top:8px; }}
.nav button {{ width:36px; height:36px; border-radius:50%; border:1px solid var(--line); background:var(--bg); color:var(--fg);
               font-size:22px; line-height:1; cursor:pointer; }}
.nav button:hover {{ border-color:var(--accent); }}
.nav .label {{ min-width:96px; text-align:center; font-weight:600; font-size:14px; }}
.switch {{ display:inline-flex; border:1px solid var(--line); border-radius:999px; overflow:hidden; }}
.switch button {{ border:0; background:var(--card); color:var(--fg); padding:6px 14px; font:inherit; font-size:14px; cursor:pointer; }}
.switch button[aria-pressed="true"] {{ background:var(--accent); color:#fff; }}
.river {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; }}
.river polyline {{ fill:none; stroke:var(--river); stroke-width:6; stroke-dasharray:16 10; }}
body.hide-river .river {{ display:none; }}

.tablewrap {{ overflow-x:auto; margin-top:16px; }}
table {{ border-collapse:collapse; width:100%; font-size:15px; }}
th, td {{ border-bottom:1px solid var(--line); padding:10px 12px; text-align:left; }}
thead th {{ font-size:13px; color:var(--muted); font-weight:600; }}
tbody th {{ font-weight:500; }}
tr.best th, tr.best td {{ background:var(--best); font-weight:600; }}
dl.metrics {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:4px 24px; font-size:14px; margin-top:16px; }}
dl.metrics dt {{ font-weight:600; margin-top:8px; }} dl.metrics dd {{ margin:0; color:var(--muted); }}

.cols {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; margin-top:16px; }}
.box {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px; }}
.box h3 {{ margin:0 0 8px; font-size:18px; }} .box ul {{ margin:0; padding-left:20px; }} .box li {{ margin:4px 0; }}

details {{ background:var(--card); border:1px solid var(--line); border-radius:12px; padding:12px 16px; margin-top:12px; }}
summary {{ cursor:pointer; font-weight:600; }}
code, pre {{ font-family:ui-monospace, 'SFMono-Regular', monospace; font-size:14px; }}
pre {{ background:var(--bg); border-radius:8px; padding:12px; overflow-x:auto; }}
footer {{ margin-top:48px; font-size:13px; color:var(--muted); }}
</style></head>
<body><main>

<header class="hero">
  <p class="kicker">Projeto de pesquisa · Computação Gráfica · IFNMG 2026/2</p>
  <h1>Rios com elevação explícita</h1>
  <p class="subtitle">na síntese de terrenos por iso-contornos</p>
  <p class="team">Lucas Santos, João Victor e Luis Fhilipe · Prof. Wagner Ferreira de Barros</p>
  <nav class="pills" aria-label="Links">
    <a class="pill" href="{PAPER_URL}">Artigo base ↗</a>
    <a class="pill" href="{REPO_URL}">Código e dados ↗</a>
    <a class="pill" href="{SLIDES_URL}">Slides do Checkpoint 2 ↗</a>
  </nav>
</header>

<section class="summary" aria-label="Resumo">
  <div><h3>O problema</h3><p>O artigo de Huftier et al. (2026) gera terrenos a partir de curvas de nível, mas os autores apontam que <b>rios continuam difíceis</b>: só podem ser sugeridos pintando um mapa de probabilidade.</p></div>
  <div><h3>A proposta</h3><p>Deixar o usuário <b>desenhar o rio e dizer a altura do leito</b>. Os pontos do rio passam a ser pontos de partida do crescimento que gera o terreno, cada um na altura pedida.</p></div>
  <div><h3>O resultado</h3><p>A altura do leito passa a ser controlada, sem criar poças. Com um <b>atraso de 2 níveis</b>, o rio forma um canal dentro de um vale: {num(d2["incised"], 0)}% do leito fica abaixo das duas margens.</p></div>
</section>

<h2>Como o algoritmo do artigo funciona</h2>
<p class="intro">Os métodos abaixo são variações deste processo. Entender a "fila de senhas" é o suficiente para acompanhar o resto.</p>
<div class="steps">
  <div><h3>Pontos e vizinhos</h3><p>Cerca de 3000 pontos são espalhados pela região e ligados por triângulos. Cada ponto conhece seus vizinhos.</p></div>
  <div><h3>Fila de senhas</h3><p>A partir da costa, o crescimento sorteia um ponto da frente e dá a <b>próxima senha</b> a um vizinho ainda sem senha. O mapa P deixa o sorteio mais frequente em algumas regiões.</p></div>
  <div><h3>Senha vira altura</h3><p>Quem recebe senha antes fica mais baixo; um histograma converte a ordem em 12 alturas. Como todo ponto é alcançado a partir de um vizinho mais baixo, <b>nunca se formam poças</b>.</p></div>
</div>

<h2>Os quatro métodos comparados</h2>
<p class="intro">Mesma região de costa, histograma e número de pontos da Figura 11 do artigo; semente aleatória {SEED}. O leito pedido vai de 0 (foz, perto da costa) a 0,15 (nascente). Números: média de 5 sementes aleatórias.</p>
<div class="legend">
  <span>Isolinhas: <i class="ramp"></i> baixo → alto (branco = mar)</span>
  <span>Terreno: <i class="gray"></i> baixo → alto (preto = mar)</span>
  <span><i class="dash"></i> traçado do rio</span>
  <label><input type="checkbox" id="river" checked> mostrar traçado</label>
  <span>Ver em todos: <span class="switch" role="group" aria-label="Ver em todos os métodos">
    <button type="button" data-all="0" aria-pressed="true">Isolinhas</button><button type="button" data-all="1" aria-pressed="false">Terreno</button>
  </span></span>
</div>
<div class="methods">{cards}
</div>

<h2>Números</h2>
<p class="intro">Média de 5 sementes aleatórias. A linha "Rio como semente" é a primeira versão da proposta: o rio espalha o crescimento na hora (D = 0) e forma só o corredor, como o método original.</p>
<div class="tablewrap"><table>
<thead><tr><th scope="col">Método</th><th scope="col">Pontos sem vizinho mais baixo</th><th scope="col">Erro no leito</th><th scope="col">Leito entalhado</th><th scope="col">Corredor rebaixado</th><th scope="col">Degrau</th></tr></thead>
<tbody>{rows_html}</tbody></table></div>
<dl class="metrics">
  <div><dt>Pontos sem vizinho mais baixo</dt><dd>Lugares de onde a água não teria para onde escoar. Zero significa que a garantia do artigo (sem poças) se mantém.</dd></div>
  <div><dt>Erro no leito</dt><dd>Diferença entre a altura pedida e a gerada, em alturas de 0 a 1. Com 12 alturas possíveis, o menor erro possível é ≈ 0,023.</dd></div>
  <div><dt>Leito entalhado</dt><dd>Porcentagem dos pontos do rio pelo menos um nível abaixo das duas margens (20 a 60 m de distância): a forma de vale.</dd></div>
  <div><dt>Corredor rebaixado</dt><dd>Quanto a faixa de 0 a 60 m em volta do rio ficou mais baixa que no controle.</dd></div>
  <div><dt>Degrau</dt><dd>Quanto uma margem ficou mais alta que a outra, além da diferença que já existe no terreno natural.</dd></div>
</dl>

<h2>O que aprendemos</h2>
<div class="cols">
<div class="box"><h3>Aprendizados</h3><ul>
<li>A proposta controla a altura do leito (erro no mínimo possível) sem criar poças.</li>
<li>Se o rio espalha o crescimento na hora, ele "puxa" as margens junto: o terreno desce num corredor largo, sem forma de vale. O método original faz o mesmo (leito entalhado: {num(base["incised"], 0)}%).</li>
<li>Se o rio nunca espalha, o leito fica entalhado ({num(never["incised"], 0)}%), mas o rio vira parede e cria um degrau ({num(never["step"], 2, True)}).</li>
<li>Com atraso de 2 níveis, os dois efeitos se combinam: entalhe de {num(d2["incised"], 0)}%, corredor {num(d2["corridor"], 2, True)} e degrau {num(d2["step"], 2, True)}.</li>
</ul></div>
<div class="box"><h3>Limitações e próximos passos</h3><ul>
<li>O canal tem a largura de um ponto do grafo (~17 m); o rio da Figura 11 tem ~50 m.</li>
<li>Um único traçado de rio e perfis de leito escolhidos pela equipe.</li>
<li>Medidas nas 12 alturas do grafo; área de drenagem e ordem de Strahler ainda não medidas.</li>
<li>Algumas métricas iniciais estavam erradas e foram corrigidas; o histórico está no repositório.</li>
</ul></div>
</div>

<h2>Explorar e reproduzir</h2>
<details><summary>Páginas interativas e dados</summary><ul>
<li><a href="results/experiment-delay/index.html">Varredura do atraso D</a>: todas as variantes de canal, por perfil e semente.</li>
<li><a href="results/experiment-river/index.html">Experimento do rio</a>: método original, controle e as variantes da proposta, em 3 perfis de leito.</li>
<li><a href="results/baseline/fig11/river_isos.svg">Baseline reproduzida</a>: Figura 11 do artigo gerada pelo código original.</li>
<li><a href="{REPO_URL}#readme">README</a>: métodos, métricas, decisões e uso de ferramentas de IA.</li>
</ul></details>
<details><summary>Como reproduzir</summary>
<p>Ubuntu (testado no WSL2), Qt 6, GLEW e CMake; detalhes no README.</p>
<pre><code>bash scripts/setup.sh              # compila
bash scripts/baseline-fig11.sh     # baseline: Figura 11 do artigo
bash scripts/experiment-river.sh   # experimento do rio (~10 min)
bash scripts/experiment-delay.sh   # varredura do atraso (~8 min)
python3 scripts/site_page.py       # regenera esta página</code></pre>
</details>

<footer>Página gerada por <code>scripts/site_page.py</code> a partir dos arquivos <code>summary.csv</code> dos experimentos.</footer>
</main>
<script>
document.getElementById('river').addEventListener('change', e => document.body.classList.toggle('hide-river', !e.target.checked));
const labels = ['Isolinhas', 'Terreno'];
function show(viewer, i) {{
  viewer.dataset.view = i;
  viewer.querySelector('.label').textContent = labels[i];
}}
document.querySelectorAll('.viewer').forEach(v => {{
  v.querySelector('.prev').addEventListener('click', () => show(v, (+v.dataset.view + 1) % 2));
  v.querySelector('.next').addEventListener('click', () => show(v, (+v.dataset.view + 1) % 2));
}});
document.querySelectorAll('[data-all]').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.viewer').forEach(v => show(v, +b.dataset.all));
  document.querySelectorAll('[data-all]').forEach(x => x.setAttribute('aria-pressed', x === b));
}}));
</script>
</body></html>
'''
(REPO / 'index.html').write_text(page)
(REPO / '.nojekyll').write_text('')
print(f'Página: {REPO / "index.html"}')
