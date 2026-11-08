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

O `run.sh` define duas variáveis de ambiente (não é preciso configurar nada à mão):

| Variável | Por quê |
|---|---|
| `QT_QPA_PLATFORM=xcb` | O GLEW do Ubuntu usa GLX. Sob Wayland (WSLg), o Qt cria um contexto EGL e o programa fecha com `GLEW Error` |
| `GALLIUM_DRIVER=d3d12` (só no WSL) | Sem ela, o Mesa renderiza na CPU (llvmpipe) em vez da GPU |

Para o uso da interface, veja [contours/TUTORIAL.md](contours/TUTORIAL.md).

## Modificações em relação ao original

O commit com a tag `original` contém o código dos autores (commit `090e35a`) sem alterações. Todas as mudanças da equipe podem ser vistas com:

```bash
git diff original -- contours/
```

| Commit | Mudança |
|---|---|
| Correções de compatibilidade com Linux | 3 correções para GCC/Qt 6.10, sem mudança de comportamento (detalhes na mensagem do commit) |

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
| NotebookLM (Google) | Organização e estudo do artigo | Conferência com o texto do artigo |

As decisões de projeto (escolha do problema, proposta, métricas) foram tomadas pela equipe.

## Licença

O código em `contours/` é dos autores do artigo, sob a licença MIT ([contours/LICENSE](contours/LICENSE)). O Qt é usado sob a LGPL.
