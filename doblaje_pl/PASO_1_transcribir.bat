@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo  PASO 1: instalar, separar la voz y transcribir
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
for %%f in (*.mp4 *.mkv *.mov *.webm) do if not defined VIDEO set "VIDEO=%%f"
if not defined VIDEO (
  echo ERROR: no hay ningun video en esta carpeta.
  pause
  exit /b 1
)
echo Video encontrado: %VIDEO%
echo.

echo [1/3] Instalando programas (puede tardar varios minutos)...
python -m pip install numpy demucs faster-whisper edge-tts
if errorlevel 1 (
  echo ERROR en la instalacion. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo [2/3] Separando la voz de la musica (tarda varios minutos)...
python doblar.py extraer "%VIDEO%"
if errorlevel 1 (
  echo ERROR al separar la voz. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo [3/3] Transcribiendo el audio...
python doblar.py transcribir --video "%VIDEO%"
if errorlevel 1 (
  echo ERROR al transcribir. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo ==============================================
echo  LISTO. Ahora adjunta en el chat el archivo:
echo     work\segments.json
echo ==============================================
start "" explorer work
pause
