# Resumo do experimento do rio

Média ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] (uma caixa do histograma ≈ 0,09).

| Modo | Execuções | Nós sem vizinho mais baixo | Erro médio no leito | Erro máximo no leito | Piso de quantização | Abaixo das margens imediatas, por senha (%) | Abaixo das margens imediatas, por altura (%) | Crescimento (ms) |
|---|---|---|---|---|---|---|---|---|
| control | 5 | 0 ± 0 | 0.198 ± 0.006 | 0.350 ± 0.027 | 0.023 ± 0.000 | 10.6 ± 5.1 | 1.2 ± 2.7 | 10 ± 1 |
| channel-d0 | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 89.7 ± 2.1 | 0.8 ± 1.8 | 13 ± 3 |
| channel-d0.5 | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 94.7 ± 3.7 | 7.8 ± 3.5 | 13 ± 2 |
| channel-d1 | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 97.1 ± 1.8 | 62.5 ± 6.8 | 12 ± 1 |
| channel-d2 | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 97.1 ± 1.8 | 86.0 ± 1.7 | 11 ± 1 |
| channel-dnever | 5 | 0 ± 0 | 0.023 ± 0.000 | 0.045 ± 0.001 | 0.023 ± 0.000 | 97.1 ± 1.8 | 87.6 ± 1.8 | 10 ± 0 |

## Forma do vale

| Modo | Execuções | Isolinhas que cruzam o rio | Leito entalhado nos dois lados (%) | Margem esquerda − leito | Margem direita − leito | Assimetria (esquerda − direita) |
|---|---|---|---|---|---|---|
| control | 5 | 11.8 ± 2.9 | 0.9 ± 1.2 | 0.047 ± 0.010 | -0.032 ± 0.009 | 0.079 ± 0.005 |
| channel-d0 | 5 | 2.0 ± 0.0 | 0.4 ± 1.0 | 0.061 ± 0.018 | 0.050 ± 0.008 | 0.011 ± 0.027 |
| channel-d0.5 | 5 | 2.0 ± 0.0 | 18.8 ± 2.7 | 0.101 ± 0.018 | 0.071 ± 0.004 | 0.029 ± 0.020 |
| channel-d1 | 5 | 2.0 ± 0.0 | 64.6 ± 9.7 | 0.117 ± 0.011 | 0.104 ± 0.011 | 0.012 ± 0.009 |
| channel-d2 | 5 | 2.0 ± 0.0 | 85.9 ± 2.9 | 0.176 ± 0.003 | 0.153 ± 0.006 | 0.023 ± 0.003 |
| channel-dnever | 5 | 2.0 ± 0.0 | 85.9 ± 2.9 | 0.342 ± 0.032 | 0.197 ± 0.011 | 0.146 ± 0.025 |

## Perfil transversal: altura média por distância até o rio

| Modo | Execuções | 0–30 m | 30–60 m | 60–100 m | 100–150 m | 150–250 m |
|---|---|---|---|---|---|---|
| control | 5 | 0.279 ± 0.007 | 0.293 ± 0.011 | 0.306 ± 0.011 | 0.317 ± 0.008 | 0.345 ± 0.002 |
| channel-d0 | 5 | 0.089 ± 0.004 | 0.162 ± 0.006 | 0.236 ± 0.005 | 0.284 ± 0.009 | 0.339 ± 0.009 |
| channel-d0.5 | 5 | 0.110 ± 0.003 | 0.191 ± 0.008 | 0.252 ± 0.011 | 0.293 ± 0.008 | 0.336 ± 0.005 |
| channel-d1 | 5 | 0.135 ± 0.005 | 0.210 ± 0.009 | 0.266 ± 0.011 | 0.296 ± 0.004 | 0.336 ± 0.003 |
| channel-d2 | 5 | 0.173 ± 0.003 | 0.257 ± 0.009 | 0.280 ± 0.005 | 0.290 ± 0.006 | 0.332 ± 0.005 |
| channel-dnever | 5 | 0.275 ± 0.013 | 0.344 ± 0.013 | 0.338 ± 0.011 | 0.333 ± 0.012 | 0.347 ± 0.005 |

## Efeito do rio em relação ao controle (mesmas sementes)

Rebaixamento: positivo = corredor mais baixo que no controle. Assimetria extra: assimetria do modo menos a do controle; perto de 0 = sem degrau criado pelo rio.

| Modo | Rebaixamento do corredor 0–60 m | Assimetria extra (degrau) |
|---|---|---|
| channel-d0 | +0.160 ± 0.005 | -0.068 ± 0.025 |
| channel-d0.5 | +0.136 ± 0.011 | -0.050 ± 0.019 |
| channel-d1 | +0.113 ± 0.007 | -0.067 ± 0.013 |
| channel-d2 | +0.071 ± 0.011 | -0.056 ± 0.006 |
| channel-dnever | -0.024 ± 0.009 | +0.067 ± 0.022 |
