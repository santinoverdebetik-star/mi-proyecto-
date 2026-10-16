# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1280x720 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=45820 esperado=45820 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1527.33s esperado=1527.33s (original 1797.9s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1527.33s audio=1527.33s |
| Video: 113 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | OK | SSIM medio 0.976, mínimo 0.940; sin desfase de fotogramas |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 382 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 890 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.29s / 0.33s / 0.63s; 0 pausas > 1.5 s, 181 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-1.4 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-14.5 LUFS, doblado=-14.9 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.02s, máximo 0.64s, 2 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 58 aceleradas (≤ límite), 101 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.08 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 890 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | OK |  |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [82, 124, 208, 212, 229, 241, 247, 248, 256, 272, 283, 317, 332, 362, 379, 382, 391, 455, 456, 457, 471, 472, 476, 479, 486, 513, 543, 549, 563, 623, 625, 642, 649, 658, 729, 735, 741, 744, 795, 876] |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.93 |

**Resultado: APROBADO**