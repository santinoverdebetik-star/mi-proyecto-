# «Alejandrina Giselle Guzmán y El Chapo 701» ES → PL

- Entrega: `salida/Alejandrina_Guzman_Chapo_701_PL.mp4` (29:33 con la intro; original 32:54; 1920×1080; 248 pausas ≥ 0,7 s acortadas a 0,4 s, se quitan 3,5 min).
- **Texto en pantalla:** no hay rótulos ni botón del canal; todo el texto visible es de imágenes de archivo (carteles, la placa «Estela contra el olvido», revistas, mapas), que se deja como está. Por eso no hubo paso de traducción de texto.
- **Tiempos:** retraso máximo de las frases 0,55 s (`--cascada`); frases largas 59, 190, 213, 219, 225, 284 y 365 quedaron algo aceleradas.
- Transcripción: «Forbeth» = Forbes; «Infobuy» = Infobae; «impí/impio» = IMPI; «Alejandrina Giselle» (el audio dice así). La frase 330 («canasto de la bandería») es dudosa; se tradujo «jakiejkolwiek ucieczki».
- Los hechos del video (varios «según los reportes…») se tradujeron fielmente, no se verificaron.
- **Intro (10 s):** planos a 200 s y 1190 s, frase 5, color amarillo. La intro se reescala a 1080p y 300 fotogramas (300 + 52 888 = 53 188).
- **Arreglo técnico:** el original mezcla fotogramas con etiquetas de color distintas (pc/bt470bg y tv/bt709); `recortar-pausas` ahora usa `-reinit_filter 0` y normaliza el color (antes perdía el 75 % de los fotogramas).
- **QA:** 2 «FALLO» que son falsos positivos, el resto OK (`qa_reporte.md`). (1) Glosario: el polaco declina los nombres (Guadalajarze, Alejandriny, narkokultury) y el control busca la forma exacta. (2) Fotograma de salida 16371 con similitud 0,83 frente al 18470 de origen: revisadas las imágenes, son idénticas; es una escena casi negra (rojo oscuro) donde la métrica pierde sensibilidad. Fotogramas 52 888 = esperados, audio y video de la misma duración, sincronía de 372 frases correcta, retraso máx. 0,55 s, voz española eliminada (0 palabras), similitud de lo que dice la voz 0,93.
