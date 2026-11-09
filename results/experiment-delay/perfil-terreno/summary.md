# Resumo do experimento do rio

Média ± desvio padrão entre sementes. Alturas normalizadas em [0, 1] (uma caixa do histograma ≈ 0,09).

| Modo | Execuções | Nós sem vizinho mais baixo | Erro médio no leito | Erro máximo no leito | Piso de quantização | Abaixo das margens imediatas, por senha (%) | Abaixo das margens imediatas, por altura (%) | Crescimento (ms) |
|---|---|---|---|---|---|---|---|---|
| control | 5 | 0 ± 0 | 0.080 ± 0.005 | 0.179 ± 0.035 | 0.024 ± 0.000 | 10.6 ± 5.1 | 1.2 ± 2.7 | 11 ± 1 |
| channel-d0 | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 76.2 ± 5.8 | 0.0 ± 0.0 | 11 ± 1 |
| channel-d0.5 | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 81.8 ± 9.3 | 2.1 ± 3.7 | 11 ± 1 |
| channel-d1 | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 93.1 ± 3.3 | 20.5 ± 7.9 | 11 ± 0 |
| channel-d2 | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 91.2 ± 6.4 | 58.8 ± 6.3 | 11 ± 1 |
| channel-dnever | 5 | 0 ± 0 | 0.024 ± 0.000 | 0.044 ± 0.001 | 0.024 ± 0.000 | 94.3 ± 6.9 | 61.7 ± 1.6 | 10 ± 1 |

## Forma do vale

| Modo | Execuções | Isolinhas que cruzam o rio | Leito entalhado nos dois lados (%) | Margem esquerda − leito | Margem direita − leito | Assimetria (esquerda − direita) |
|---|---|---|---|---|---|---|
| control | 5 | 11.8 ± 2.9 | 0.9 ± 1.2 | 0.047 ± 0.010 | -0.032 ± 0.009 | 0.079 ± 0.005 |
| channel-d0 | 5 | 4.0 ± 0.0 | 0.0 ± 0.0 | 0.014 ± 0.009 | 0.003 ± 0.008 | 0.012 ± 0.009 |
| channel-d0.5 | 5 | 4.0 ± 0.0 | 2.9 ± 1.1 | 0.053 ± 0.007 | 0.021 ± 0.015 | 0.032 ± 0.018 |
| channel-d1 | 5 | 4.0 ± 0.0 | 15.2 ± 6.3 | 0.079 ± 0.007 | 0.040 ± 0.005 | 0.038 ± 0.003 |
| channel-d2 | 5 | 4.0 ± 0.0 | 36.7 ± 6.8 | 0.127 ± 0.007 | 0.053 ± 0.009 | 0.074 ± 0.006 |
| channel-dnever | 5 | 4.0 ± 0.0 | 37.7 ± 7.6 | 0.207 ± 0.026 | 0.060 ± 0.007 | 0.147 ± 0.024 |

## Perfil transversal: altura média por distância até o rio

| Modo | Execuções | 0–30 m | 30–60 m | 60–100 m | 100–150 m | 150–250 m |
|---|---|---|---|---|---|---|
| control | 5 | 0.279 ± 0.007 | 0.293 ± 0.011 | 0.306 ± 0.011 | 0.317 ± 0.008 | 0.345 ± 0.002 |
| channel-d0 | 5 | 0.205 ± 0.006 | 0.239 ± 0.010 | 0.275 ± 0.007 | 0.296 ± 0.004 | 0.333 ± 0.003 |
| channel-d0.5 | 5 | 0.219 ± 0.003 | 0.263 ± 0.007 | 0.293 ± 0.011 | 0.307 ± 0.007 | 0.333 ± 0.009 |
| channel-d1 | 5 | 0.240 ± 0.004 | 0.279 ± 0.007 | 0.305 ± 0.005 | 0.318 ± 0.006 | 0.340 ± 0.006 |
| channel-d2 | 5 | 0.265 ± 0.011 | 0.301 ± 0.009 | 0.310 ± 0.006 | 0.315 ± 0.004 | 0.341 ± 0.006 |
| channel-dnever | 5 | 0.310 ± 0.015 | 0.342 ± 0.012 | 0.335 ± 0.011 | 0.330 ± 0.011 | 0.344 ± 0.005 |

## Efeito do rio em relação ao controle (mesmas sementes)

Rebaixamento: positivo = corredor mais baixo que no controle. Assimetria extra: assimetria do modo menos a do controle; perto de 0 = sem degrau criado pelo rio.

| Modo | Rebaixamento do corredor 0–60 m | Assimetria extra (degrau) |
|---|---|---|
| channel-d0 | +0.064 ± 0.008 | -0.067 ± 0.011 |
| channel-d0.5 | +0.045 ± 0.009 | -0.047 ± 0.017 |
| channel-d1 | +0.026 ± 0.008 | -0.041 ± 0.007 |
| channel-d2 | +0.003 ± 0.009 | -0.005 ± 0.010 |
| channel-dnever | -0.040 ± 0.009 | +0.068 ± 0.021 |
