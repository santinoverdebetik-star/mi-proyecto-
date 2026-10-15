# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1280x720 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=61277 esperado=61277 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=2042.57s esperado=2042.57s (original 2142.8s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=2042.57s audio=2042.57s |
| Video: 111 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | OK | SSIM medio 0.978, mínimo 0.906; sin desfase de fotogramas |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 206 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 1249 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.23s / 0.22s / 0.64s; 0 pausas > 1.5 s, 465 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.4 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-14.0 LUFS, doblado=-14.8 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.06s, máximo 0.92s, 34 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 104 aceleradas (≤ límite), 279 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.08 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 1249 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [2, 82, 460, 745, 815, 820, 900] |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [55, 117, 175, 216, 251, 265, 273, 287, 341, 382, 421, 424, 427, 432, 475, 526, 576, 583, 603, 610, 644, 725, 771, 773, 795, 802, 805, 839, 849, 885, 888, 913, 953, 956, 992, 1054, 1089, 1157, 1175, 1218, 1238] |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.92 |

**Resultado: APROBADO**