# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1280x720 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=53536 esperado=53536 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1784.53s esperado=1784.53s (original 2044.0s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1784.53s audio=1784.53s |
| Video: 110 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | OK | SSIM medio 0.980, mínimo 0.945; sin desfase de fotogramas |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 205 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 253 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.38s / 0.38s / 0.67s; 0 pausas > 1.5 s, 0 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = deu | OK | deu |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.5 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-14.6 LUFS, doblado=-12.9 LUFS |
| Tiempos: ningún segmento excede su hueco ni se acelera más del límite | OK | 0 acelerados (≤ límite), 253 a velocidad natural |
| Tiempos: aceleración máxima aplicada | OK | x1.0 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 253 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [15, 82, 84, 134, 141, 142, 152, 249] |
| Traducción: longitud razonable respecto al original | OK |  |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.95 |

**Resultado: APROBADO**