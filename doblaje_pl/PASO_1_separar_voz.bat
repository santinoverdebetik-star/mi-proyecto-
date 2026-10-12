@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo  PASO 1: instalar y separar la voz de la musica
echo ==============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: no se encontro Python.
  pause
  exit /b 1
)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ERROR: no se encontro ffmpeg.
  pause
  exit /b 1
)
if not exist doblar.py (
  echo ERROR: falta doblar.py en esta carpeta.
  pause
  exit /b 1
)

set "VIDEO="
for %%f in (*.mp4 *.mkv *.mov *.webm) do if /i not "%%f"=="video_pl.mp4" if not defined VIDEO set "VIDEO=%%f"
if not defined VIDEO (
  echo ERROR: no hay ningun video en esta carpeta.
  pause
  exit /b 1
)
echo Video encontrado: %VIDEO%
echo.

echo [1/3] Instalando programas (puede tardar varios minutos, descarga varios GB)...
python -m pip install numpy demucs piper-tts faster-whisper
if errorlevel 1 (
  echo ERROR en la instalacion. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo [2/3] Bajando la voz polaca mc_speech (Piper, gratis)...
if not exist voices mkdir voices
if not exist voices\pl_PL-mc_speech-medium.onnx curl -L -o voices\pl_PL-mc_speech-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/mc_speech/medium/pl_PL-mc_speech-medium.onnx
if not exist voices\pl_PL-mc_speech-medium.onnx.json curl -L -o voices\pl_PL-mc_speech-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/mc_speech/medium/pl_PL-mc_speech-medium.onnx.json
echo.
echo [3/3] Separando la voz de la musica (tarda varios minutos)...
python doblar.py extraer "%VIDEO%"
if errorlevel 1 (
  echo ERROR al separar la voz. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo ==============================================
echo  LISTO. Ahora ejecuta PASO_2_doblar.bat
echo ==============================================
pause
