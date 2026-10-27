# Prueba de 4 minutos con la voz de Martin (Voizum) — cómo continuar

Todo está listo menos la voz: **la clave `VOIZUM_API_KEY` solo se carga al iniciar una sesión nueva** (la sesión donde se armó esto no la ve).

## En una sesión nueva (con el secreto ya guardado en el entorno)

Pegá este mensaje:

> Continuá desde `historias_ia/LEEME_PRUEBA_4MIN.md`: buscá la voz Martin en Voizum, generá la prueba de 4 minutos y renderizala.

o ejecutá a mano (desde `historias_ia/herramientas`, `video/` con `npm install` hecho):

```bash
python3 prueba_4min.py --listar-voces            # busca las voces que contienen "martin" (muestra su id)
python3 prueba_4min.py --voz-id ID_DE_MARTIN     # 1 solo trabajo de Voizum (~190 créditos), alinea, mezcla y escribe video/props_prueba4.json
cd ../video
CHROMIUM_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  npx remotion render src/index.ts Historia out/prueba4.mp4 --props=props_prueba4.json --scale=0.5 --concurrency=4
```
(En tu PC no hace falta `CHROMIUM_PATH`; para 1080p quitá `--scale=0.5`.)

Estado verificado: el flujo completo (alineación voz↔texto 548/549 palabras, 42 escenas, mezcla con glitch + golpes) se probó con una voz gratuita **solo para comprobar el proceso**; esa voz no es la del video.

Opciones: `--lineas N` (cuánto del guion; 52 ≈ 4 min), `--velocidad 1.05` (velocidad de la voz Voizum).

## Qué hay
- `GUION_VIRUS_IA.md` — guion completo (~25 min, 3.399 palabras) + verificación de hechos con fuentes.
- `GUION_VIRUS_IA_texto_voz.txt` — solo el texto para la voz.
- `herramientas/prueba_4min.py` — voz → alineación → escenas → mezcla.
- `video/` — Remotion. 3D procedural: `caja_tv, caja_led, intrusion, contagio, manometro, cajas15, casas_red, fabrica, candado, candado_agujero, apagon, duplicacion, rack, radar, nucleo, red, puerta, pantalla_rota`; parámetro `luz`: `noche | media | clara`.
- El 3D se renderiza al 60 % de resolución interna (`GL_K` en `Escena3D.tsx`): ~4× más rápido en la nube.
