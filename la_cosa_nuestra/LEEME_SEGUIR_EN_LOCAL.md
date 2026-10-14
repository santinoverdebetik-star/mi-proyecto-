# Seguir el video de La Cosa Nuestra en tu computadora

Estado: el video V4 (`salida/La_Cosa_Nuestra_V4.mp4`) esta completo salvo los clips de la serie.
La voz ("salvatore soprano" de Voizum), el guion (`GUION_V2.md`) y la seleccion de fotos ya estan hechos.

## Lo que hay en `la_cosa_nuestra/video/trabajo/`
- `graded/` 189 fotos de lugares (licencia libre, sin caras) ya con el color del video; creditos en `CREDITOS_FOTOS.csv`
- `reales/` 10 fotos historicas de dominio publico con su pie de foto; creditos en `CREDITOS_FOTOS_REALES.csv`
- `tableros/` tableros de evidencias de cada Parte
- `timeline.json` momento exacto de cada regla y de cada palabra (para sincronizar)
- `voz_final.mp3` la voz completa (27 min 14 s), ya ecualizada
- `clips/` aqui van TUS clips de la serie: `slot_05.mp4`, `slot_06.mp4`... (ver `CLIPS_SERIE_ENCONTRADOS.csv`)

## Hacer el video final
Requisitos: Python 3, ffmpeg en el PATH, `pip install numpy opencv-python-headless pillow`

    cd la_cosa_nuestra/video
    python hacer_video_final.py

Crea `salida/La_Cosa_Nuestra_V5.mp4`: voz + musica de mafia al 6 %, sin subtitulos, y con tus clips
en sus huecos (los huecos sin clip siguen con fotos). Para ver un trozo antes: `--desde 128 --hasta 248 --salida prueba.mp4`.
Para cambiar el volumen de la musica: `--musica 0.05`.

## Si quieres cambiar algo
- Guion o voz: la voz se genera con `voizum_generar.py` (necesita tu clave en la variable `VOIZUM_API_KEY`, nunca en un archivo).
- Texto limpio para la voz: `python generar_texto_voz.py`.
- Clips: `bajar_clips.bat` recorta desde YouTube; las ventanas marcadas AJUSTAR hay que revisarlas.
