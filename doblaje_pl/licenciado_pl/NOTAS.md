# «Dámaso López, El Licenciado» ES → PL

- Entrega: `salida/Damaso_Lopez_Licenciado_PL.mp4` (34:03; original 35:43; 206 pausas ≥ 0,7 s acortadas a 0,4 s; la narración es muy continua, por eso se quitan solo 1,7 min).
- **Texto en pantalla:** 28 tarjetas (títulos, citas, fechas, mapas con leyendas) traducidas al polaco con `tarjetas_motor.py` (misma tipografía, color, desvanecimiento y movimiento); lista completa en `tarjetas.py`. Se dejan sin cambios nombres propios de lugares/personas, el apodo «EL LICENCIADO» y el texto de imágenes de archivo (carteles, documentos, pantallas).
- **Tiempos:** el polaco es más largo que el español; las frases que no entran en su hueco se aceleran como máximo ×1,08 y la siguiente arranca después (`--cascada`): retraso medio 0,06 s, máximo 0,92 s.
- Transcripción: «Mini League/Mini Leak» = **Mini Lic**; «Semanario Z» = tygodnik **Zeta**; «Río 12» = **Riodoce**; «Damazo/Dámaz O.» = **Dámaso**; la frase 833 es dudosa en la transcripción («grupo de damas o alianzas»).
- Los hechos del video (varios «según…») se tradujeron fielmente, no se verificaron.
- QA: APROBADO (`qa_reporte.md`). Avisos: cifras escritas con letras y longitud de frases cortas (cortes de oración).

## Intro de suscripción (10 s)
Añadida delante del video sin tocar el resto (concat sin recodificar; 300 + 61277 fotogramas). Planos a 1966,6 s y 628 s, frase 3, color celeste. Pausas: sin pausas ≥ 0,7 s según el QA sobre voz limpia (máx. 0,70 s), nada que recortar. Pendiente: tarjetas de texto que quedaron en español (OCR sin terminar).
