# «Las mansiones abandonadas de El Chapo, El Mencho y El Mayo» ES → PL

- Entrega: `salida/Mansiones_Abandonadas_Chapo_Mayo_Mencho_PL.mp4` (29:41 con la intro; original 33:03; 1920×1080; 350 pausas ≥ 0,7 s acortadas a 0,4 s, se quitan 3,5 min; fotogramas 53 436 = 300 de intro + 53 136).
- Nota: el enlace de Drive era el mismo del video «Chapo 701», pero el archivo había sido reemplazado (modificado minutos antes, 1,36 GB, 33:03): es otro video.
- **Texto en pantalla:** OCR cada 2 s (990 fotogramas): solo hay texto de imágenes de archivo (marcas de agua, carteles, grafitis, la placa «OBRA DE ARTE», fechas de fotos históricas), que se deja como está. No hay rótulos del canal ni botón Subscribe, así que no hubo paso de traducción de texto.
- 812 frases; retraso máximo 0,23 s (`--cascada`); factor máximo de aceleración 1,12; 30 frases con un pequeño desborde absorbido por los huecos.
- Transcripción: «palacios deportada» = «palacios de portada» (rezydencje z okładek); «Ocegueras» = Oseguera; «a sobrecerrado» = oferta cerrada (aukcja w zamkniętych ofertach); cifras escritas con letras para que Piper las lea bien.
- Los hechos (fechas de 2024–2026, sentencias, cifras) se tradujeron tal como los dice el video; no se verificaron.
- **Intro (10 s):** planos a 421,2 s y 1742 s, frase 6, color rosa, `--relleno 1.18`. Se añadió `FRASES[6]` y el color `rosa` a `crear_intro.py`.
- **QA:** 2 «FALLO» que son falsos positivos, el resto OK (`qa_reporte.md`). (1) Glosario: el segmento 596 dice «finales de mayo» (el mes) y el control lo toma por «Mayo» el capo. (2) Fotogramas de salida 12724 y 42659 con similitud 0,81 y 0,83: revisados, son idénticos al origen; la diferencia es solo el grano de la imagen. Fotogramas 53 136 = esperados, audio y video de la misma duración (1771,2 s), 350 cortes todos en pausa, 812 frases en su sitio, retraso máx. 0,23 s, voz española eliminada (0 palabras), similitud de lo que dice la voz 0,91, −16,4 LUFS frente a −17,9 original, sin recortes.
