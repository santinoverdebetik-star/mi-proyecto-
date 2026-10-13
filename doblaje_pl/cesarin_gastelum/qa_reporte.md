# Informe QA doblaje ES→PL

| Prueba | Estado | Detalle |
|---|---|---|
| Video: mismo códec/resolución/fps/paquetes | OK | h264 1280x720 30/1 50683 paquetes |
| Video: contenido idéntico (md5 del stream, sin recomprimir ni ralentizar) | OK | MD5=a48733f0693ea706fe969d31645ef33d |
| Duración igual a la original (±0.10 s) | OK | in=1689.437s out=1689.437s |
| Audio: 1 pista AAC a 48 kHz | OK | [('aac', '48000', 2)] |
| Audio: etiqueta de idioma = pol | OK | pol |
| Audio: sin clipping (pico ≤ -0.9 dB) | OK | max_volume=-2.6 dB |
| Audio: sonoridad similar al video original (±3 LU) | OK | original=-15.5 LUFS, doblado=-15.1 LUFS |
| Tiempos: ningún segmento excede su hueco ni se acelera más del límite | OK | 0 acelerados (≤ límite), 75 a velocidad natural |
| Tiempos: aceleración máxima aplicada | OK | x1.0 |
| Cobertura: todos los segmentos tienen voz audible | OK |  |
| Traducción: todos los segmentos traducidos | OK | 75 segmentos |
| Traducción: sin caracteres exclusivos del español | OK |  |
| Traducción: ninguna cifra inventada o alterada | OK |  |
| Traducción: cifras escritas con letras (revisar a mano) | AVISO | segmentos: [25] |
| Traducción: longitud razonable respecto al original | OK |  |
| Traducción: términos del glosario | OK |  |
| Voz española eliminada (reconocimiento sobre la música) | OK | 0 palabras detectadas |
| Voz polaca dice lo traducido (similitud ≥ 0.80) | OK | 0.96 |

**Resultado: APROBADO**