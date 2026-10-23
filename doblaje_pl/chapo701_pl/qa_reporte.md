# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1920x1080 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=52888 esperado=52888 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1762.93s esperado=1762.93s (original 1973.8s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1762.93s audio=1762.93s |
| Video: 111 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | FALLO | desfasados: [(16371, 18470, 0.831)] sin imagen: [] medio 0.965 |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 248 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 372 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.33s / 0.35s / 0.64s; 0 pausas > 1.5 s, 38 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-1.3 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-17.9 LUFS, doblado=-16.3 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.00s, máximo 0.55s, 1 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 30 aceleradas (≤ límite), 7 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.12 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 372 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [4, 36, 59, 60, 62, 74, 76, 94, 98, 123, 140, 144, 145, 151, 162, 169, 170, 183, 184, 192, 232, 234, 241, 253, 275, 278, 299, 325, 334, 335, 336, 345, 362] |
| Traducción: longitud razonable respecto al original | OK |  |
| Traducción: términos del glosario | FALLO | [(2, 'Guadalajara', 'Guadalajara'), (28, 'Alejandrina', 'Alejandrina'), (36, 'Guadalajara', 'Guadalajara'), (39, 'narcocultura', 'narkokultura'), (97, 'narcocultura', 'narkokultura'), (111, 'Alejandrina', 'Alejandrina'), (115, 'Alejandrina', 'Alejandrina'), (133, 'Alejandrina', 'Alejandrina'), (135, 'narcocultura', 'narkokultura'), (163, 'Guadalajara', 'Guadalajara'), (190, 'Guadalajara', 'Guadalajara'), (207, 'IMPI', 'IMPI'), (207, 'narcocultura', 'narkokultura'), (214, 'Alejandrina', 'Alejandrina'), (222, 'Alejandrina', 'Alejandrina'), (251, 'Alejandrina', 'Alejandrina'), (272, 'Alejandrina', 'Alejandrina'), (282, 'narcocultura', 'narkokultura'), (320, 'Alejandrina', 'Alejandrina'), (347, 'narcocultura', 'narkokultura'), (353, 'Alejandrina', 'Alejandrina'), (361, 'Guadalajara', 'Guadalajara')] |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.93 |

**Resultado: 2 FALLO(S)**