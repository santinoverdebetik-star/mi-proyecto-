# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1920x1080 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=53201 esperado=53201 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1773.37s esperado=1773.37s (original 1902.4s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1773.37s audio=1773.37s |
| Video: 119 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | FALLO | desfasados: [(10639, 11420, 0.82), (31864, 34299, 0.815), (36306, 39046, 0.691), (44558, 47839, 0.824)] sin imagen: [] medio 0.956 |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 228 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 785 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.30s / 0.34s / 0.66s; 0 pausas > 1.5 s, 159 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.4 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-17.9 LUFS, doblado=-16.2 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.00s, máximo 0.32s, 0 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 110 aceleradas (≤ límite), 34 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.12 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 785 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [1, 19, 20, 22, 44, 72, 73, 95, 130, 132, 134, 141, 143, 145, 154, 160, 161, 163, 176, 177, 197, 200, 221, 225, 237, 238, 241, 252, 258, 263, 270, 278, 285, 287, 289, 290, 305, 311, 318, 319, 320, 324, 325, 326, 327, 333, 335, 337, 350, 364, 365, 367, 371, 386, 404, 405, 407, 408, 414, 415, 416, 421, 423, 424, 449, 450, 451, 459, 472, 476, 482, 484, 485, 497, 504, 510, 519, 520, 521, 523, 539, 547, 554, 576, 590, 596, 597, 689, 690, 693, 731, 744, 759, 760, 761, 763, 765] |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [7, 8, 18, 75, 140, 163, 177, 204, 241, 248, 253, 319, 325, 350, 365, 408, 451, 472, 520, 576, 611, 659, 669, 680] |
| Traducción: términos del glosario | FALLO | [(571, 'Edgar Jiménez', 'Edgar Jiménez')] |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.91 |

**Resultado: 2 FALLO(S)**