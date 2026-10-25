# «Los cinco sicarios más jóvenes de América Latina» ES → PL

- Entrega: `salida/Ninos_Sicarios_Mas_Jovenes_PL.mp4` (29:41 con la intro; original 31:42; 1920×1080; 228 pausas ≥ 0,7 s acortadas a 0,4 s, se quitan 2,1 min; fotogramas 53 501 = 300 de intro + 53 201).
- Nota: el enlace de Drive es el mismo de los videos «Chapo 701» y «Mansiones abandonadas», pero el archivo fue reemplazado otra vez (modificado el 25/10/2026, 1,26 GB, 31:42): es otro video.
- **Texto en pantalla:** OCR cada 2 s: solo hay texto de imágenes de archivo (carteles, matrículas, marcas, fotos de prensa), que se deja como está. No hay rótulos del canal ni botón Subscribe, así que no hubo paso de traducción de texto.
- 785 frases; retraso máximo 0,32 s (`--cascada`); aceleración máxima ×1,12; se acortaron ~60 frases que no entraban en su hueco.
- Transcripción: «acorrido» = «a corrido» (brzmią jak korrido); «los de Goyé» / «de Goyard» = «los degollé» / «degollar» (podrzynać gardła). «Reino Criminal» se dice y se escribe en polaco: «Królestwo Przestępcze».
- Nombres propios con pronunciación española para Piper (`pronunciacion.json`): Chuchito Nini, Juanito Pistolas, Medellín, Ponchis, Jiménez, Escobar, Pizarro, Castaño, Uribe Turbay, etc.
- Los hechos (fechas de 2019–2026, cifras, casos) se tradujeron tal como los dice el video; no se verificaron.
- **Intro (10 s):** planos a 668 s y 966,5 s, frase 7, color violeta, `--relleno 1.18`. Se añadió `FRASES[7]` y el color `violeta` a `crear_intro.py`.
- **QA:** 2 «FALLO» que son falsos positivos (`qa_reporte.md`). (1) Glosario: el segmento 571 en español dice «Edgar Jiménez» y la traducción dice solo «Edgar». (2) Cuatro fotogramas con similitud 0,69–0,82: revisados a ojo; son fotos con grano o transiciones casi negras, idénticos al origen. Fotogramas 53 201 = esperados, audio y video de la misma duración (1773,37 s), 228 cortes todos en pausa, 785 frases en su sitio, retraso máx. 0,32 s, voz española eliminada (0 palabras), similitud de lo que dice la voz 0,91, −16,2 LUFS frente a −17,9 original, sin recortes.
