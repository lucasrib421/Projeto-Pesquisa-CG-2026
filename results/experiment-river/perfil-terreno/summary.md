# Resumo do experimento do rio

Média ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] (uma caixa do histograma ≈ 0,09).

| Modo | Execuções | Nós sem vizinho mais baixo | Erro médio no leito | Erro máximo no leito | Piso de quantização | Abaixo das margens imediatas, por senha (%) | Abaixo das margens imediatas, por altura (%) | Crescimento (ms) |
|---|---|---|---|---|---|---|---|---|
| baseline | 5 | 0 ± 0 | 0.099 ± 0.005 | 0.201 ± 0.014 | 0.024 ± 0.000 | 14.9 ± 7.1 | 0.0 ± 0.0 | 12 ± 1 |
| control | 5 | 0 ± 0 | 0.080 ± 0.005 | 0.179 ± 0.035 | 0.024 ± 0.000 | 10.6 ± 5.1 | 1.2 ± 2.7 | 10 ± 0 |
| reserve | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 76.2 ± 5.8 | 0.0 ± 0.0 | 11 ± 0 |
| passive | 5 | 0 ± 0 | 0.029 ± 0.003 | 0.084 ± 0.020 | 0.024 ± 0.000 | 73.5 ± 7.2 | 0.0 ± 0.0 | 12 ± 2 |

## Forma do vale

| Modo | Execuções | Isolinhas que cruzam o rio | Leito entalhado, 1 nível abaixo das margens a 20-60 m (%) |
|---|---|---|---|
| baseline | 5 | 3.4 ± 0.9 | 0.4 ± 1.0 |
| control | 5 | 11.8 ± 2.9 | 2.5 ± 2.3 |
| reserve | 5 | 4.0 ± 0.0 | 0.0 ± 0.0 |
| passive | 5 | 5.2 ± 1.8 | 0.4 ± 0.9 |

## Perfil transversal: altura média por distância até o rio

| Modo | Execuções | 0–30 m | 30–60 m | 60–100 m | 100–150 m | 150–250 m |
|---|---|---|---|---|---|---|
| baseline | 5 | 0.104 ± 0.008 | 0.145 ± 0.004 | 0.219 ± 0.004 | 0.273 ± 0.005 | 0.331 ± 0.011 |
| control | 5 | 0.279 ± 0.007 | 0.293 ± 0.011 | 0.306 ± 0.011 | 0.317 ± 0.008 | 0.345 ± 0.002 |
| reserve | 5 | 0.205 ± 0.006 | 0.239 ± 0.010 | 0.275 ± 0.007 | 0.296 ± 0.004 | 0.333 ± 0.003 |
| passive | 5 | 0.199 ± 0.010 | 0.238 ± 0.009 | 0.277 ± 0.007 | 0.299 ± 0.010 | 0.329 ± 0.011 |

## Efeito do rio (positivo = corredor mais baixo que no controle)

| Modo | Rebaixamento do corredor 0–60 m em relação ao controle |
|---|---|
| baseline | +0.161 ± 0.009 |
| reserve | +0.064 ± 0.008 |
| passive | +0.067 ± 0.007 |
