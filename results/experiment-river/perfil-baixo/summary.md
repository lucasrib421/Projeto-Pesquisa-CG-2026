# Resumo do experimento do rio

Média ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] (uma caixa do histograma ≈ 0,09).

| Modo | Execuções | Nós sem vizinho mais baixo | Erro médio no leito | Erro máximo no leito | Piso de quantização | Abaixo das margens imediatas, por senha (%) | Abaixo das margens imediatas, por altura (%) | Crescimento (ms) |
|---|---|---|---|---|---|---|---|---|
| baseline | 5 | 0 ± 0 | 0.041 ± 0.002 | 0.132 ± 0.006 | 0.023 ± 0.000 | 14.9 ± 7.1 | 0.0 ± 0.0 | 17 ± 4 |
| control | 5 | 0 ± 0 | 0.198 ± 0.006 | 0.350 ± 0.027 | 0.023 ± 0.000 | 10.6 ± 5.1 | 1.2 ± 2.7 | 11 ± 1 |
| reserve | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 89.7 ± 2.1 | 0.8 ± 1.8 | 12 ± 1 |
| passive | 5 | 0 ± 0 | 0.023 ± 0.001 | 0.050 ± 0.003 | 0.023 ± 0.000 | 91.0 ± 3.0 | 0.4 ± 0.9 | 12 ± 0 |
| channel | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 97.1 ± 1.8 | 87.6 ± 1.8 | 10 ± 0 |

## Forma do vale

| Modo | Execuções | Isolinhas que cruzam o rio | Leito entalhado, 1 nível abaixo das margens a 20-60 m (%) |
|---|---|---|---|
| baseline | 5 | 3.4 ± 0.9 | 0.4 ± 1.0 |
| control | 5 | 11.8 ± 2.9 | 2.5 ± 2.3 |
| reserve | 5 | 2.0 ± 0.0 | 7.0 ± 5.3 |
| passive | 5 | 2.4 ± 0.9 | 7.5 ± 6.6 |
| channel | 5 | 2.0 ± 0.0 | 92.1 ± 5.7 |

## Perfil transversal: altura média por distância até o rio

| Modo | Execuções | 0–30 m | 30–60 m | 60–100 m | 100–150 m | 150–250 m |
|---|---|---|---|---|---|---|
| baseline | 5 | 0.104 ± 0.008 | 0.145 ± 0.004 | 0.219 ± 0.004 | 0.273 ± 0.005 | 0.331 ± 0.011 |
| control | 5 | 0.279 ± 0.007 | 0.293 ± 0.011 | 0.306 ± 0.011 | 0.317 ± 0.008 | 0.345 ± 0.002 |
| reserve | 5 | 0.089 ± 0.004 | 0.162 ± 0.006 | 0.236 ± 0.005 | 0.284 ± 0.009 | 0.339 ± 0.009 |
| passive | 5 | 0.085 ± 0.003 | 0.156 ± 0.007 | 0.233 ± 0.004 | 0.282 ± 0.011 | 0.337 ± 0.006 |
| channel | 5 | 0.275 ± 0.013 | 0.344 ± 0.013 | 0.338 ± 0.011 | 0.333 ± 0.012 | 0.347 ± 0.005 |

## Efeito do rio (positivo = corredor mais baixo que no controle)

| Modo | Rebaixamento do corredor 0–60 m em relação ao controle |
|---|---|
| baseline | +0.161 ± 0.009 |
| reserve | +0.160 ± 0.005 |
| passive | +0.165 ± 0.009 |
| channel | -0.024 ± 0.009 |
