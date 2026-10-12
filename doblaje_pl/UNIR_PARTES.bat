@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo  Uniendo parte_00 ... parte_13 en un solo video
echo ==============================================
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ERROR: no se encontro ffmpeg.
  pause
  exit /b 1
)
if not exist parte_00.mp4 (
  echo ERROR: no encuentro parte_00.mp4. Pon todas las partes en esta carpeta.
  pause
  exit /b 1
)
if exist _lista.txt del _lista.txt
for /f "delims=" %%f in ('dir /b /on parte_*.mp4') do echo file '%%f'>>_lista.txt
ffmpeg -y -v error -f concat -safe 0 -i _lista.txt -c copy -movflags +faststart video_pl_final.mp4
if errorlevel 1 (
  echo ERROR al unir. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)
del _lista.txt
echo.
echo LISTO: video_pl_final.mp4 (sin recomprimir, calidad intacta)
pause
