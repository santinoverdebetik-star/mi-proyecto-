# Doblajes del canal "Reino Criminal"

Herramienta: `doblaje_pl/doblar.py` (extraer → transcribir → afinar → sintetizar → mezclar → recortar-pausas → qa).

## Receta fija (instrucción permanente del usuario) — paso final de CADA doblaje

Eliminar las pausas largas del video ya montado:

1. Detectar los silencios sobre la **voz limpia** (`voz_pl.wav` / voice_natural), nunca sobre el mix con música (la música los taparía).
2. Recortar las pausas **≥ 0,7 s dejando 0,4 s de respiro**; no tocar los gaps cortos (para que no suene atropellado).
3. Aplicar el corte al **video final ya montado**, cortando video y audio juntos para que queden sincronizados.

Comando: `python doblar.py --dir work recortar-pausas video_final.mp4 salida.mp4 --idioma <pl|de> --crf 26`
Luego: `python doblar.py --dir work qa original.mp4 salida.mp4 --idioma <pl|de> --compacto --glosario glosario.json --modelo medium`

Entregas: subir a `salida/` (Git LFS, cuota gratuita 1 GB) y pasar el enlace + el informe de QA.

## Texto en pantalla (también en cada doblaje)

Antes de mezclar: buscar texto en pantalla (OCR de fotogramas cada 2 s; `doblaje_pl/mansion_ivan/` tiene los scripts de ejemplo: `intro_texto.py` borra el texto original y escribe el traducido con el mismo efecto de aparición; `sub_texto.py` traduce el botón animado Subscribe/Subscribed). Se traducen los textos del canal; los nombres propios y el texto de las imágenes de archivo (mapas, pantallas) se dejan como están. Luego el video con textos traducidos es el que entra a `mezclar`.
