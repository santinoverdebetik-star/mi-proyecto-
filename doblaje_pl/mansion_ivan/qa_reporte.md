# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1280x720 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=36288 esperado=36288 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1209.60s esperado=1209.60s (original 1791.0s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1209.60s audio=1209.60s |
| Video: 109 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | OK | SSIM medio 0.963, mínimo 0.938; sin desfase de fotogramas |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 325 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 336 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.36s / 0.36s / 0.59s; 0 pausas > 1.5 s, 1 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.5 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-15.8 LUFS, doblado=-15.2 LUFS |
| Tiempos: ningún segmento excede su hueco ni se acelera más del límite | OK | 1 acelerados (≤ límite), 335 a velocidad natural |
| Tiempos: aceleración máxima aplicada | OK | x1.0233 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 336 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | OK |  |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [42, 55, 60, 84, 105, 217] |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.91 |

**Resultado: APROBADO**