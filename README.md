# Rios com elevação explícita na síntese de terrenos por iso-contornos

Projeto de Pesquisa da disciplina de Computação Gráfica (IFNMG, 2026/2). Prof. Wagner Ferreira de Barros.

**Equipe:** Lucas Santos · João Victor · Luis Fhilipe

**Página de resultados:** https://lucasrib421.github.io/Projeto-Pesquisa-CG-2026/ (gerada por `scripts/site_page.py`)

## Artigo base

B. Huftier, H. Schott, E. Galin, O. Argudo, A. Peytavie, E. Guérin. *Terrain Synthesis and Authoring based on Iso-Contours*. Computer Graphics Forum 45(2), 2026. DOI: [10.1111/cgf.70389](https://doi.org/10.1111/cgf.70389). Código original: [Arches-Team/Contours](https://github.com/Arches-Team/Contours).

O método gera terrenos como conjuntos aninhados de curvas de nível. Um crescimento *Open Eden Growth* sobre uma rede de triângulos avança da borda para o interior, e a ordem de chegada de cada ponto define sua altura. Por construção, o terreno não tem bacias endorreicas.

## Proposta

Na seção 6.6, os autores apontam que gerar rios com largura e inclinação variáveis continua sendo um desafio: hoje o rio só pode ser sugerido pelo mapa de probabilidade P ou por várias regiões desenhadas à mão. A proposta da equipe é permitir que o usuário desenhe o rio com a **elevação do leito explícita**. Os pontos do grafo sobre o rio passam a ser sementes extras do crescimento, ativadas quando ele atinge a elevação prescrita.

- **Baseline:** o método original, com o rio definido pelo mapa P (Figura 11 do artigo).
- **Métricas medidas:** erro de elevação no leito, nós sem vizinho mais baixo (garantia de não haver bacias endorreicas), forma do vale (leito entalhado nos dois lados, rebaixamento do corredor, degrau entre as margens) e tempo de geração.
- **Métricas planejadas, ainda não medidas:** área de drenagem e ordem de Strahler.

## Estrutura do repositório

```
contours/        código do artigo (C++/Qt), importado intacto e depois modificado
scripts/
  setup.sh       verifica dependências e compila em build/
  run.sh         executa o programa com o ambiente correto
  baseline-fig11.sh  reproduz a baseline (Figura 11 do artigo)
  experiment-river.sh  experimento do rio (baseline × proposta, várias sementes)
  metrics.py     métricas do experimento (summary.csv, summary.md)
  compare_page.py  página HTML de comparação lado a lado
  make_profile.py  gera o perfil de leito que acompanha o terreno
  experiment-delay.sh  varredura do atraso de espalhamento do modo channel
  site_page.py   gera index.html, a página de resultados (GitHub Pages)
experiments/     entradas dos experimentos (traçado do rio em CSV, três perfis)
results/         resultados dos experimentos
build/           saída da compilação (não versionada)
```

## Dependências

Testado em Ubuntu 26.04 (WSL2) com GCC 15.2, CMake 4.2, Qt 6.10.2 e GLEW 2.2.

```bash
sudo apt install build-essential cmake ninja-build pkg-config libglew-dev qt6-base-dev qt6-base-dev-tools qt6-svg-dev
```

O programa usa OpenGL 4.5 ou superior (compute shaders). Para conferir a versão disponível, use `glxinfo -B` (pacote `mesa-utils`).

## Compilar e executar

```bash
bash scripts/setup.sh
```

```bash
bash scripts/run.sh
```

O `run.sh` define estas variáveis de ambiente (não é preciso configurar nada à mão):

| Variável | Por quê |
|---|---|
| `QT_QPA_PLATFORM=xcb` | O GLEW do Ubuntu usa GLX. Sob Wayland (WSLg), o Qt cria um contexto EGL e o programa fecha com `GLEW Error` |
| `GALLIUM_DRIVER=d3d12` (só no WSL) | Sem ela, o Mesa renderiza na CPU (llvmpipe) em vez da GPU |
| `QT_HASH_SEED=0` | O Qt sorteia a ordem dos `QSet` a cada execução, e o Eden Growth percorre um `QSet` ao sortear nós. Sem ela, a mesma entrada gera resultados diferentes |

Para o uso da interface, veja [contours/TUTORIAL.md](contours/TUTORIAL.md).

## Reproduzir a baseline (Figura 11)

```bash
bash scripts/baseline-fig11.sh
```

Gera em `results/baseline/fig11/` a Figura 11 do artigo: um rio definido pelo mapa de probabilidade P, comparado com um mapa uniforme. Leva cerca de 8 s. Parâmetros (definidos em `GenerateFigure11`): domínio `Box2(500)` (de −500 a 500 m, 1 km de lado; a unidade interna é o metro), ~3000 partículas, 12 isolinhas, máscara `Images/input/mask.png`, mapa P `Images/input/proba.png` (expoente 4), histograma de `Data/dems/rockies_zoom_breach.png`. Gerador aleatório com semente 239 (padrão do código) e `QT_HASH_SEED=0`: execuções repetidas geram arquivos idênticos.

| Arquivo | Conteúdo |
|---|---|
| `river_mask.svg` | Máscara (região do terreno) |
| `river_noise.png`, `uniform_noise.png` | Mapas de probabilidade P: com rio e uniforme |
| `river_isos.svg`, `uniform_isos.svg` | Isolinhas geradas |
| `river_eden.svg`, `uniform_eden.svg` | Grafo com a ordem de crescimento (~17 MB cada; não versionados, regenerados pelo script) |

## Experimento do rio (resultados preliminares)

```bash
bash scripts/experiment-river.sh
```

Roda 3 perfis de leito × 5 modos × 5 sementes (239 a 243), cerca de 10 minutos, com a mesma máscara, histograma e ~3000 partículas da Figura 11. Para rodar só parte: `PROFILES="terreno" MODES="channel" bash scripts/experiment-river.sh`.

| Modo | Rio definido por | Mapa P |
|---|---|---|
| `baseline` | Pintura no mapa P (método original, Figura 11) | `proba.png` |
| `control` | Nenhum rio (isola o efeito do rio) | Uniforme |
| `reserve` | CSV com elevação explícita; nós do rio bloqueados até a senha-alvo e depois sementes do crescimento (decisão D1-A) | Uniforme |
| `passive` | CSV; nó ativado na senha-alvo ou antes, se o crescimento chegar (D1-B) | Uniforme |
| `channel` | CSV; como `reserve`, mas o crescimento **não se espalha** a partir do rio | Uniforme |

Perfis do leito, todos sobre o mesmo traçado (braço esquerdo do rio da Figura 11):
- `experiments/river-fig11-perfil-alto.csv`: linear, 0 na foz e 0,40 na nascente;
- `experiments/river-fig11-perfil-baixo.csv`: linear, 0 a 0,15;
- `experiments/river-fig11-perfil-terreno.csv`: altura natural ao longo do traçado (média de 5 execuções do controle) menos 0,1, gerado por `scripts/make_profile.py`.

Na `baseline` e no `control`, o CSV só serve para medir.

Para ver os resultados, abra `results/experiment-river/index.html` no navegador (isolinhas e terreno lado a lado, seletores de perfil e semente, traçado do rio por cima). No WSL:

```bash
explorer.exe "$(wslpath -w results/experiment-river/index.html)"
```

Resultados completos em `results/experiment-river/perfil-<alto|baixo|terreno>/summary.md`. Resumo (média entre as 5 sementes; alturas normalizadas em [0, 1], uma caixa do histograma ≈ 0,09; baseline e controle não dependem do perfil):

| Perfil | Modo | Nós sem vizinho mais baixo | Erro médio no leito | Leito entalhado nos dois lados (%) | Rebaixamento do corredor 0–60 m | Degrau (assimetria extra) |
|---|---|---|---|---|---|---|
| — | baseline | 0 | — | 0,0 | +0,161 | −0,085 |
| — | control | 0 | — | 0,9 | — | — |
| alto | reserve | 0 | 0,021 | 0,0 | +0,068 | −0,062 |
| alto | passive | 0 | 0,024 | 0,0 | +0,069 | −0,069 |
| alto | channel | 0 | 0,021 | 43,1 | −0,039 | +0,068 |
| baixo | reserve | 0 | 0,023 | 0,4 | +0,160 | −0,068 |
| baixo | passive | 0 | 0,023 | 3,0 | +0,165 | −0,080 |
| baixo | channel | 0 | 0,023 | 85,9 | −0,024 | +0,067 |
| terreno | reserve | 0 | 0,024 | 0,0 | +0,064 | −0,067 |
| terreno | passive | 0 | 0,029 | 0,0 | +0,067 | −0,056 |
| terreno | channel | 0 | 0,024 | 37,7 | −0,040 | +0,068 |

O que os resultados mostram até aqui:
- Nenhum modo cria nós sem vizinho mais baixo: a garantia do artigo (sem bacias endorreicas) se mantém com o rio explícito.
- A proposta controla a altura do leito: o erro fica no piso de quantização (o menor possível com 12 alturas). O erro da baseline em relação aos perfis é de 0,04 a 0,10.
- Há dois efeitos distintos, e cada variante produz um:
  - **Corredor rebaixado** (`reserve`, `passive`, e também a `baseline`): o rio vira semente, o crescimento se espalha a partir dele e as margens recebem as senhas seguintes. O terreno desce numa faixa de ~60 a 100 m (até +0,16 com o perfil baixo, igual à baseline), mas o leito fica na mesma altura das margens: um lóbulo largo, sem a forma de vale (leito entalhado ~0%, inclusive na baseline).
  - **Leito entalhado** (`channel`): o rio recebe a altura pedida, mas não semeia as margens, que ficam com a altura natural. O leito fica abaixo das duas margens em 38 a 86% dos nós, conforme o perfil, e o canal aparece no terreno. O corredor em volta não desce, e surge um **degrau**: a margem leste fica ~0,07 mais alta do que no controle, porque os nós do rio, que nunca entram na frente, funcionam como parede permanente e o lado leste só é alcançado contornando o rio (confirmado pela varredura do atraso, abaixo).
- Um vale de rio real combina os dois efeitos (canal entalhado dentro de um vale mais largo). Nenhuma das variantes acima faz as duas coisas; o canal com espalhamento atrasado (seção seguinte) faz.

Definições (em `scripts/metrics.py`):
- **Nós sem vizinho mais baixo:** nós fora da costa sem vizinho de senha menor. É a garantia do artigo; deve ser 0.
- **Erro no leito:** \|altura gerada − altura pedida\| nos nós do rio.
- **Piso de quantização:** menor erro possível, porque o terreno só tem 12 alturas (uma por caixa do histograma).
- **Leito entalhado nos dois lados:** nó do rio pelo menos um nível abaixo da média da margem esquerda **e** da direita (nós a 20–60 m dele e a pelo menos 20 m do traçado, separados pela direção local do rio). Mede a forma de vale. Uma versão anterior usava a média das duas margens juntas e superestimava o entalhe quando um lado era muito mais alto (ex.: 74,5% contra 37,7% no perfil terreno).
- **Degrau (assimetria extra):** (margem esquerda − margem direita) no modo menos a mesma diferença no controle, por semente. Perto de 0: o rio não criou degrau; negativo: o vale ficou mais simétrico que o terreno natural.
- **Isolinhas que cruzam o rio** (no `summary.md`): mudanças de altura entre nós consecutivos do rio.
- **Perfil transversal** (no `summary.md`): altura média por faixa de distância até o rio. **Rebaixamento do corredor:** média das faixas 0–30 m e 30–60 m no controle menos a mesma média no modo, por semente.
- **Abaixo das margens imediatas** (no `summary.md`, por senha e por altura): a versão por senha pode ser alta enquanto a por altura é ~0%, porque senhas próximas caem na mesma caixa de altura.

Limitações conhecidas destes resultados preliminares:
- O canal tem a largura de um nó (~17 m entre nós vizinhos); o rio pintado da baseline tem ~50 m.
- O perfil `terreno` usa as alturas do próprio controle; os perfis lineares foram escolhidos pela equipe.
- O traçado segue só o braço esquerdo do rio da Figura 11.
- Métricas medidas nas alturas do grafo (12 níveis), não no terreno interpolado.

## Canal com espalhamento atrasado (varredura)

```bash
bash scripts/experiment-delay.sh
```

O modo `channel` aceita `--spread-delay D` (em níveis de altura; 1 nível = nós / caixas do histograma senhas): o nó do rio recebe a altura pedida e só passa a espalhar o crescimento D níveis depois. Durante o atraso as margens ficam mais altas que o leito (entalhe); depois o rio espalha e o entorno desce (corredor). `D = 0` é idêntico à `reserve` e D ausente (nunca espalha) é idêntico ao `channel`, byte a byte. A varredura roda D = 0; 0,5; 1; 2; nunca, mais o controle, nos perfis baixo e terreno (5 sementes; ~8 minutos). Resultados em `results/experiment-delay/` (página em `results/experiment-delay/index.html`).

Perfil baixo (média de 5 sementes; em todas as linhas: 0 nós sem vizinho mais baixo e erro no leito 0,023, o piso):

| D (níveis) | Leito entalhado nos dois lados (%) | Rebaixamento do corredor 0–60 m | Degrau (assimetria extra) |
|---|---|---|---|
| 0 (= reserve) | 0,4 | +0,160 | −0,068 |
| 0,5 | 18,8 | +0,136 | −0,050 |
| 1 | 64,6 | +0,113 | −0,067 |
| **2** | **85,9** | **+0,071** | **−0,056** |
| nunca (= channel) | 85,9 | −0,024 | +0,067 |

No perfil terreno, a tendência é a mesma, mas mais fraca (D = 2: 36,7% de entalhe, corredor +0,003), porque o leito pedido fica só 0,1 abaixo do terreno natural.

O que a varredura mostra:
- O entalhe cresce com o atraso e satura em D = 2; o corredor diminui com o atraso.
- O degrau só aparece quando o rio **nunca** espalha: com qualquer atraso finito, depois de liberado o rio deixa o crescimento atravessar, e o outro lado não fica atrasado. Isso confirma a hipótese da parede (permanente) para o degrau do `channel`.
- Com D = 2 e o perfil baixo, o rio fica entalhado nos dois lados **e** dentro de um corredor rebaixado, sem degrau: a primeira variante com a forma de um vale de rio. No terreno, aparece como um canal dentro de uma faixa mais escura dos dois lados.

## Decisões de implementação (provisórias)

| Decisão | Escolha atual |
|---|---|
| D1. Crescimento chega ao rio antes da hora | Variantes implementadas para comparação: `reserve`, `passive` e `channel` (com atraso de espalhamento `--spread-delay`) |
| D2. Rio que "sobe" | Máximo acumulado da foz para a nascente (contado em `run_info.txt`) |
| D3. Entrada | CSV `x,y,elevation`: metros no domínio `Box2(500)` e altura **normalizada [0, 1]**, da foz para a nascente |
| D4. Linha → nós do grafo | Nó mais próximo a cada passo de r/4 ao longo da linha; buracos contados em `run_info.txt` |
| D5. Condições | Baseline com o rio no mapa P; controle e proposta com P uniforme; demais entradas iguais |

Para rodar um modo isolado (os caminhos são relativos a `contours/AppIso/AppIso`, a pasta de trabalho do `run.sh`; `--stay` mantém a janela aberta para ver o terreno em 3D):

```bash
bash scripts/run.sh --experiment channel --spread-delay 2 --river ../../../experiments/river-fig11-perfil-baixo.csv --seed 239 --out ../../../results/teste/ --stay
```

## Modificações em relação ao original

O commit com a tag `original` contém o código dos autores (commit `090e35a`) sem alterações. Todas as mudanças da equipe podem ser vistas com:

```bash
git diff original -- contours/
```

| Commit | Mudança |
|---|---|
| Correções de compatibilidade com Linux | 3 correções para GCC/Qt 6.10, sem mudança de comportamento (detalhes na mensagem do commit) |
| Caminhos `../images/` → `../Images/` | 26 caminhos em minúsculas que falhavam no Linux (a imagem carregava vazia, sem erro) |
| Modo em lote `--figure 11 --out <pasta>` | Gera uma única figura do artigo e fecha (`main.cpp`); sem a opção, comportamento original |
| Rios com elevação explícita (proposta) | Arquivos novos `river-generation.h/.cpp` (subclasse de `IsoVectoGenerationV1`, sem alterar o original) e `river-experiment.cpp`; opções `--experiment` (`baseline`, `control`, `reserve`, `passive`, `channel`), `--river`, `--seed`, `--spread-delay`, `--stay` |

## Problemas conhecidos

- **Modos *Eroded* e *Export PBR*:** os caminhos dos shaders de erosão no código original não correspondem às pastas reais (por exemplo, `LibHeightfield/LibHeightfield/Shaders`). Por isso, esses modos devem falhar (ainda não corrigido nem testado).
- **Não defina `ARCHESLIBDIR`:** com essa variável definida, o código usa os caminhos acima literalmente, sem nenhum fallback.
- **Encoding:** alguns arquivos do original (por exemplo, `graph.h`) têm comentários em Latin-1. Edite-os com o encoding *ISO 8859-1* para não alterar linhas que não foram mexidas.

## Uso de ferramentas de IA

| Ferramenta | Atividade | Como a equipe verificou |
|---|---|---|
| Claude Code (Anthropic) | Análise da estrutura do código original (C++/Qt) e localização dos componentes do algoritmo | Leitura dos arquivos indicados e comparação com o artigo |
| Claude Code | Diagnóstico dos erros de compilação no Linux e das 3 correções de compatibilidade | Compilação e execução; diff revisado (`git diff original`) |
| Claude Code | Diagnóstico de problemas de ambiente no WSL (links de dados, GLEW/Wayland, GPU) e scripts `setup.sh`/`run.sh` | Execução do programa pelos scripts |
| Claude Code | Apoio na leitura do artigo e no levantamento das limitações | Conferência com as seções 6.5 e 6.6 do artigo |
| Claude Code | Rascunho dos slides do Checkpoint 1 | Revisão e apresentação pela equipe |
| Claude Code | Modo em lote, correção dos caminhos, diagnóstico da não reprodutibilidade (`QT_HASH_SEED`) e script da baseline | Execuções repetidas com comparação byte a byte dos arquivos gerados |
| Claude Code | Implementação da proposta (rio como semente), scripts do experimento e das métricas, página de comparação | Teste de fidelidade (modo `baseline` gera isolinhas idênticas às da Figura 11 original); execução com 5 sementes |
| Claude Code | Variantes `control`, `channel` e espalhamento atrasado; métricas de forma do vale; análise dos resultados; material de estudo e relatório da implementação para o NotebookLM | Testes de sanidade byte a byte (`--spread-delay 0` idêntico à `reserve`; sem atraso idêntico ao `channel`); comparação das métricas com as imagens pela equipe, que identificou métricas enganosas depois corrigidas |
| NotebookLM (Google) | Organização e estudo do artigo | Conferência com o texto do artigo |

As decisões de projeto (escolha do problema, proposta, métricas) foram tomadas pela equipe.

## Licença

O código em `contours/` é dos autores do artigo, sob a licença MIT ([contours/LICENSE](contours/LICENSE)). O Qt é usado sob a LGPL.
