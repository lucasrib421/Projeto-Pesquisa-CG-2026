# Rios com elevação explícita na síntese de terrenos por iso-contornos

Projeto de Pesquisa da disciplina de Computação Gráfica (IFNMG, 2026/2). Prof. Wagner Ferreira de Barros.

**Equipe:** Lucas Santos · João Victor · Luis Fhilipe

## Artigo base

B. Huftier, H. Schott, E. Galin, O. Argudo, A. Peytavie, E. Guérin. *Terrain Synthesis and Authoring based on Iso-Contours*. Computer Graphics Forum 45(2), 2026. DOI: [10.1111/cgf.70389](https://doi.org/10.1111/cgf.70389). Código original: [Arches-Team/Contours](https://github.com/Arches-Team/Contours).

O método gera terrenos como conjuntos aninhados de curvas de nível. Um crescimento *Open Eden Growth* sobre uma rede de triângulos avança da borda para o interior, e a ordem de chegada de cada ponto define sua altura. Por construção, o terreno não tem bacias endorreicas.

## Proposta

Na seção 6.6, os autores apontam que gerar rios com largura e inclinação variáveis continua sendo um desafio: hoje o rio só pode ser sugerido pelo mapa de probabilidade P ou por várias regiões desenhadas à mão. A proposta da equipe é permitir que o usuário desenhe o rio com a **elevação do leito explícita**. Os pontos do grafo sobre o rio passam a ser sementes extras do crescimento, ativadas quando ele atinge a elevação prescrita.

- **Baseline:** o método original, com o rio definido pelo mapa P (Figura 11 do artigo).
- **Métricas:** erro de elevação no leito, número de bacias endorreicas, área de drenagem, ordem de Strahler e tempo de geração.

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
experiments/     entradas dos experimentos (traçado do rio em CSV, dois perfis)
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

Gera em `results/baseline/fig11/` a Figura 11 do artigo: um rio definido pelo mapa de probabilidade P, comparado com um mapa uniforme. Leva cerca de 8 s. Parâmetros (definidos em `GenerateFigure11`): domínio `Box2(500)` (de −500 a 500, 1000 unidades de lado), ~3000 partículas, 12 isolinhas, máscara `Images/input/mask.png`, mapa P `Images/input/proba.png` (expoente 4), histograma de `Data/dems/rockies_zoom_breach.png`. Gerador aleatório com semente 239 (padrão do código) e `QT_HASH_SEED=0`: execuções repetidas geram arquivos idênticos.

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

Roda 2 perfis de leito × 4 modos × 5 sementes (239 a 243), cerca de 6 minutos, com a mesma máscara, histograma e ~3000 partículas da Figura 11:

| Modo | Rio definido por | Mapa P |
|---|---|---|
| `baseline` | Pintura no mapa P (método original, Figura 11) | `proba.png` |
| `control` | Nenhum rio (isola o efeito do rio) | Uniforme |
| `reserve` | CSV com elevação explícita; nós do rio bloqueados até a senha-alvo (decisão D1-A) | Uniforme |
| `passive` | CSV com elevação explícita; nó ativado na senha-alvo ou antes, se o crescimento chegar (D1-B) | Uniforme |

Perfis do leito (mesmo traçado, braço esquerdo do rio da Figura 11): `experiments/river-fig11-perfil-alto.csv` (0 na foz, 0,40 na nascente) e `experiments/river-fig11-perfil-baixo.csv` (0 a 0,15). Na `baseline` e no `control` o CSV só serve para medir.

Para ver os resultados, abra `results/experiment-river/index.html` no navegador (isolinhas e terreno lado a lado, seletores de perfil e semente, traçado do rio por cima). No WSL:

```bash
explorer.exe "$(wslpath -w results/experiment-river/index.html)"
```

Resultados completos em `results/experiment-river/perfil-<alto|baixo>/summary.md`. Resumo (média entre as 5 sementes; alturas normalizadas em [0, 1], uma caixa do histograma ≈ 0,09):

| Perfil | Modo | Nós sem vizinho mais baixo | Erro médio no leito | Piso de quantização | Rebaixamento do corredor 0–60 m (vs. controle) |
|---|---|---|---|---|---|
| — | baseline | 0 | 0,102 (alto) / 0,041 (baixo) | 0,021 / 0,023 | +0,161 |
| alto | reserve | 0 | 0,021 | 0,021 | +0,068 |
| alto | passive | 0 | 0,024 | 0,021 | +0,069 |
| baixo | reserve | 0 | 0,023 | 0,023 | +0,160 |
| baixo | passive | 0 | 0,023 | 0,023 | +0,165 |

O que os resultados mostram até aqui:
- Nenhum modo cria nós sem vizinho mais baixo: a garantia do artigo (sem bacias endorreicas) se mantém com o rio explícito.
- A proposta controla a altura do leito: o erro fica no piso de quantização (o menor possível com 12 alturas).
- O rio rebaixa um **corredor** de ~60 a 100 m em volta dele, não só os próprios nós: ao ser ativado, ele vira semente, e os vizinhos recebem as senhas seguintes (mesma caixa de altura). Por isso o rio quase nunca fica abaixo das margens **imediatas** (coluna "por altura" no `summary.md`, perto de 0%), mas o corredor fica mais baixo.
- A profundidade do vale depende do perfil pedido em relação ao terreno natural (~0,28 ao longo do traçado, no controle). Com o perfil alto, o vale é raso (+0,07, menos de uma caixa) e quase invisível; com o perfil baixo, é tão profundo quanto o da baseline (+0,16).

Definições (em `scripts/metrics.py`):
- **Nós sem vizinho mais baixo:** nós fora da costa sem vizinho de senha menor. É a garantia do artigo; deve ser 0.
- **Erro no leito:** \|altura gerada − altura pedida\| nos nós do rio. Na baseline e no controle, mede a distância entre o terreno gerado e um perfil que esses modos não têm como receber.
- **Piso de quantização:** menor erro possível, porque o terreno só tem 12 alturas (uma por caixa do histograma).
- **Perfil transversal:** altura média dos nós por faixa de distância até o rio. **Rebaixamento do corredor:** média das faixas 0–30 m e 30–60 m no controle menos a mesma média no modo, por semente.
- **Abaixo das margens imediatas** (por senha e por altura): nó do rio mais baixo que todos os vizinhos fora do rio. A versão por senha pode ser alta enquanto a por altura é ~0%, porque senhas próximas caem na mesma caixa de altura.

Limitações conhecidas destes resultados preliminares:
- O traçado tem a largura de um nó (~17 m entre nós vizinhos); a largura do vale vem só do crescimento em volta do rio. O rio pintado da baseline tem ~50 m.
- Dois perfis lineares, escolhidos pela equipe; outros perfis ainda não foram testados.
- O traçado segue só o braço esquerdo do rio da Figura 11.
- Métricas medidas nas alturas do grafo (12 níveis), não no terreno interpolado.

### Decisões de implementação (provisórias)

| Decisão | Escolha atual |
|---|---|
| D1. Crescimento chega ao rio antes da hora | As duas opções implementadas (`reserve` e `passive`) para comparação |
| D2. Rio que "sobe" | Máximo acumulado da foz para a nascente (contado em `run_info.txt`) |
| D3. Entrada | CSV `x,y,elevation`: metros no domínio `Box2(500)` e altura **normalizada [0, 1]**, da foz para a nascente |
| D4. Linha → nós do grafo | Nó mais próximo a cada passo de r/4 ao longo da linha; buracos contados em `run_info.txt` |
| D5. Condições | Baseline com o rio no mapa P; controle e proposta com P uniforme; demais entradas iguais |

Para rodar um modo isolado (os caminhos são relativos a `contours/AppIso/AppIso`, a pasta de trabalho do `run.sh`; `--stay` mantém a janela aberta para ver o terreno em 3D):

```bash
bash scripts/run.sh --experiment reserve --river ../../../experiments/river-fig11-perfil-baixo.csv --seed 239 --out ../../../results/teste/ --stay
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
| Rios com elevação explícita (proposta) | Arquivos novos `river-generation.h/.cpp` (subclasse de `IsoVectoGenerationV1`, sem alterar o original) e `river-experiment.cpp`; opções `--experiment` (`baseline`, `control`, `reserve`, `passive`), `--river`, `--seed`, `--stay` |

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
| NotebookLM (Google) | Organização e estudo do artigo | Conferência com o texto do artigo |

As decisões de projeto (escolha do problema, proposta, métricas) foram tomadas pela equipe.

## Licença

O código em `contours/` é dos autores do artigo, sob a licença MIT ([contours/LICENSE](contours/LICENSE)). O Qt é usado sob a LGPL.
