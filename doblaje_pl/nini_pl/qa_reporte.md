# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo tamaño y fps que el original, códec h264 | OK | h264 1280x720 30/1 |
| Video: fotogramas = suma de los tramos conservados (sin duplicar ni perder ninguno) | OK | salida=41370 esperado=41370 |
| Duración del video = duración esperada (±0.10 s) | OK | salida=1379.00s esperado=1379.00s (original 1978.2s) |
| Audio y video con la misma duración (±0.10 s) | OK | video=1379.00s audio=1379.00s |
| Video: 109 fotogramas (bordes de cada corte + azar) coinciden con su fotograma de origen | OK | SSIM medio 0.968, mínimo 0.935; sin desfase de fotogramas |
| Cortes: ninguno cae dentro de una frase (silencio de voz en los 80 ms previos) | OK | 323 cortes, todos en pausa |
| Sincronía: cada frase suena en su sitio dentro del video nuevo | OK | 333 frases |
| Ritmo: pausas entre frases (media / mediana / máxima) | OK | 0.36s / 0.36s / 0.62s; 0 pausas > 1.5 s, 1 < 0.1 s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-1.5 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-15.5 LUFS, doblado=-15.1 LUFS |
| Tiempos: ninguna frase arranca más de 1.2 s después de su hueco original | OK | retraso medio 0.00s, máximo 0.04s, 0 frases con retraso > 0.5 s |
| Tiempos: aceleración / frases que no entran en su hueco | OK | 1 aceleradas (≤ límite), 0 con el máximo de aceleración y arranque diferido de la siguiente |
| Tiempos: aceleración máxima aplicada | OK | x1.0288 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 333 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [212] |
| Traducción: longitud razonable respecto al original | AVISO | revisar manualmente: [40, 200, 241] |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| La voz doblada dice lo traducido (similitud ≥ 0.80) | OK | 0.92 |

**Resultado: APROBADO**