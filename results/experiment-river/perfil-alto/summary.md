# Resumo do experimento do rio

Média ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] (uma caixa do histograma ≈ 0,09).

| Modo | Execuções | Nós sem vizinho mais baixo | Erro médio no leito | Erro máximo no leito | Piso de quantização | Abaixo das margens imediatas, por senha (%) | Abaixo das margens imediatas, por altura (%) | Crescimento (ms) |
|---|---|---|---|---|---|---|---|---|
| baseline | 5 | 0 ± 0 | 0.102 ± 0.006 | 0.187 ± 0.015 | 0.021 ± 0.001 | 14.9 ± 7.1 | 0.0 ± 0.0 | 16 ± 4 |
| control | 5 | 0 ± 0 | 0.085 ± 0.011 | 0.212 ± 0.031 | 0.021 ± 0.001 | 10.6 ± 5.1 | 1.2 ± 2.7 | 13 ± 3 |
| reserve | 5 | 0 ± 0 | 0.021 ± 0.001 | 0.044 ± 0.001 | 0.021 ± 0.001 | 75.2 ± 6.5 | 0.0 ± 0.0 | 12 ± 1 |
| passive | 5 | 0 ± 0 | 0.024 ± 0.002 | 0.065 ± 0.006 | 0.021 ± 0.001 | 83.5 ± 6.3 | 0.4 ± 0.9 | 14 ± 6 |
| channel | 5 | 0 ± 0 | 0.021 ± 0.001 | 0.044 ± 0.001 | 0.021 ± 0.001 | 93.5 ± 6.5 | 66.6 ± 3.5 | 10 ± 1 |

## Forma do vale

| Modo | Execuções | Isolinhas que cruzam o rio | Leito entalhado, 1 nível abaixo das margens a 20-60 m (%) |
|---|---|---|---|
| baseline | 5 | 3.4 ± 0.9 | 0.4 ± 1.0 |
| control | 5 | 11.8 ± 2.9 | 2.5 ± 2.3 |
| reserve | 5 | 4.0 ± 0.0 | 0.0 ± 0.0 |
| passive | 5 | 4.8 ± 1.1 | 0.4 ± 0.9 |
| channel | 5 | 4.0 ± 0.0 | 68.3 ± 8.2 |

## Perfil transversal: altura média por distância até o rio

| Modo | Execuções | 0–30 m | 30–60 m | 60–100 m | 100–150 m | 150–250 m |
|---|---|---|---|---|---|---|
| baseline | 5 | 0.104 ± 0.008 | 0.145 ± 0.004 | 0.219 ± 0.004 | 0.273 ± 0.005 | 0.331 ± 0.011 |
| control | 5 | 0.279 ± 0.007 | 0.293 ± 0.011 | 0.306 ± 0.011 | 0.317 ± 0.008 | 0.345 ± 0.002 |
| reserve | 5 | 0.198 ± 0.004 | 0.237 ± 0.009 | 0.274 ± 0.011 | 0.295 ± 0.005 | 0.336 ± 0.008 |
| passive | 5 | 0.195 ± 0.005 | 0.239 ± 0.009 | 0.274 ± 0.008 | 0.294 ± 0.011 | 0.329 ± 0.005 |
| channel | 5 | 0.308 ± 0.014 | 0.342 ± 0.012 | 0.335 ± 0.011 | 0.330 ± 0.011 | 0.344 ± 0.005 |

## Efeito do rio (positivo = corredor mais baixo que no controle)

| Modo | Rebaixamento do corredor 0–60 m em relação ao controle |
|---|---|
| baseline | +0.161 ± 0.009 |
| reserve | +0.068 ± 0.009 |
| passive | +0.069 ± 0.005 |
| channel | -0.039 ± 0.009 |
