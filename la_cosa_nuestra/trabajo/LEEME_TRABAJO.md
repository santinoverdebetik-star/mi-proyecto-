# Cómo rehacer el video en tu PC (o en cualquier sesión)

Todo lo necesario está en esta carpeta; los scripts están en `la_cosa_nuestra/video/`.

**Requisitos:** Python 3 con `pip install opencv-python-headless numpy pillow` y `ffmpeg` en el PATH.
Para los clips: `yt-dlp` (ver `video/bajar_clips.bat`).

Contenido de `trabajo/`:
- `voz_final.mp3` – voz completa "salvatore soprano" (27:14), ya ecualizada y con el titulo de la regla 19 sin duplicar.
- `timeline.json` – bloques del guion con sus tiempos y cada palabra con su tiempo.
- `palabras_final.json` – transcripción de la voz (para sincronizar).
- `fotos/` – las 189 fotos curadas (licencia libre, sin caras). Créditos: `CREDITOS_FOTOS.csv`.
- `reales/` – 10 fotos históricas reales (dominio público) y `reales.json` con los pies de foto.
- `clips/` – (tú la creas) clips de la serie `slot_NN.mp4`, 3 a 5 s.

## Pasos (desde la carpeta del proyecto)
```
cd la_cosa_nuestra/video
set T=..\trabajo_render           (en Linux/Mac: T=../trabajo_render)
mkdir %T%
copy ..\trabajo\timeline.json %T%\
python armar_video.py preparar ..\trabajo\fotos %T%
python armar_video.py reales ..\trabajo\reales %T%
python armar_video.py tableros %T%\timeline.json %T%
mkdir %T%\clips        (copia aqui tus slot_NN.mp4)
set SOLO_CON_CLIP=1
python armar_video.py plan %T%\timeline.json %T%
set SIN_SUBS=1
python armar_video.py render %T%\timeline.json %T% 0 1634.6 4
set MAFIA=1
set MUSIC_GAIN=0.06
python musica.py ..\trabajo\timeline.json ..\trabajo\voz_final.mp3 mezcla_raw.wav
ffmpeg -i mezcla_raw.wav -af loudnorm=I=-16:TP=-1.5:LRA=9 -ar 44100 mezcla.wav
python armar_video.py unir %T% mezcla.wav ..\..\salida\La_Cosa_Nuestra_V5.mp4
```
(En Linux/Mac usa `export VAR=valor` en lugar de `set`.)
La voz se generó en Voizum (job `cmv7iqt7h0085oy01evvvmqc8`); el audio original se puede volver a bajar hasta el 18/10/2026.
