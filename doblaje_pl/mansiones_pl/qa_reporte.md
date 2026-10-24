# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1920x1080 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=53136 esperado=53136 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1771.20s esperado=1771.20s (original 1982.8s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1771.20s audio=1771.20s |
| Video: 115 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | FALLO | desfasados: [(12724, 14222, 0.808), (42659, 47168, 0.834)] sin imagen: [] medio 0.958 |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 350 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 812 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.33s / 0.35s / 0.65s; 0 pausas > 1.5 s, 96 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.5 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-17.9 LUFS, doblado=-16.4 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.00s, máximo 0.23s, 0 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 59 aceleradas (≤ límite), 30 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.12 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 812 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [28, 60, 89, 108, 111, 117, 125, 177, 231, 246, 247, 250, 301, 314, 334, 394, 465, 471, 487, 494, 497, 511, 513, 573, 591, 594, 595, 602, 603, 645, 712, 713, 714, 715, 718, 757, 776, 791, 792] |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [3, 6, 62, 99, 147, 160, 161, 169, 171, 184, 209, 280, 287, 339, 544, 573, 634, 654, 687, 692, 704, 711, 725, 784] |
| Traducción: términos del glosario | FALLO | [(596, 'Mayo', 'Mayo')] |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.91 |

**Resultado: 2 FALLO(S)**