# ESTADO — IA DESCONTROLADA (actualizado 2026-10-28)

## Hecho
- Guion completo "Los virus de IA ya casi están aquí" (~25 min, 3.399 palabras) con verificación de hechos → `GUION_VIRUS_IA.md`.
- Voz Martín (Voizum id `2db0a890-0274-448e-96c2-09b08f2196e0`) generada para las primeras 52 líneas (3:39) → `video/public/prueba4/voz.mp3`.
- Música de aventura audible (`herramientas/musica_aventura.py`), glitch como transición, baja un poco más desde 2:46 (nivel 0,24).
- Biblioteca de 45 clips 3D (ninguno se repite), fondos de 50 fotos reales (`video/public/fondos/`, créditos en `CREDITOS_FONDOS.csv`), bordes biselados, sombras, plano más cerrado.
- Pipeline: `herramientas/prueba_4min.py` (voz → alineación → escenas → fondos → mezcla) y `video/render_por_tramos.sh` (render reanudable).
- Prueba nueva (V4, fondos reales) renderizándose por tramos; al terminar queda en `video/out/prueba4.mp4` (se copia a `muestra/`).

## Reglas fijas del usuario (ver GUIA_DE_ESTILO.md)
Ningún clip 3D se repite · clips ≤ 5 s · mucha luz · música de aventura audible y baja · fondos de lugares reales (no azules) · clips lo más parecidos a la referencia y reales.

## Pendiente / ideas para seguir
1. Ver la prueba V4 y ajustar (el usuario la pidió para evaluar).
2. Clips que aún no calzan perfecto con la frase (p. ej. tras el diagrama "tu conexión alquilada").
3. Video completo de 25 min: faltan ~250 clips únicos → generar imágenes en ImageFX (prompts por escena) o ampliar la biblioteca.
4. Verificar con el informe original lo de Anthropic (15 cajas / 26B) y Palisade (81 %).
5. **Rotar la clave de Voizum** (se compartió dos veces en el chat). Nunca guardarla en archivos.
6. Subir la carpeta a `D:\youtube stuff\IA DESCONTROLADA\` (el zip de entrega se genera con el script de entrega descrito en LEEME de la carpeta).

## V5 (estudio oscuro + fotos reales intercaladas)
- Hecho: fondo estudio oscuro, objetos apoyados en piso (MIN_Y en Escena3D.tsx), clips Foto.tsx alternados con 3D (3 s / 2,2 s), pool de ~100 fotos reales (public/fotos + fondos_raw). Video: muestra/prueba_4min_V5_estudio_y_fotos_540p.mp4.
- Pendiente: feedback del usuario sobre V5; más fotos/ImageFX para el video de 25 min; rotar clave Voizum.
- ImageFX: `herramientas/prompts_imagefx.py` genera `IMAGENES_IMAGEFX_PROMPTS.md` (206 prompts, uno por hueco de foto). Las imágenes se guardan como `video/public/fotos_fx/bNN_k.jpg` y `prueba_4min.py` las usa primero.
- V8 (muestra/prueba_4min_V8_insertos_y_audio_540p.mp4): insertos gráficos sin texto, música 0.05, efectos bajos, 3D 4,6 s, render incremental (herramientas/render_incremental.py). Pendiente: feedback del usuario; voz+render del video completo de 25 min (~1.400 créditos Voizum, muchas horas de render); ImageFX opcional.
