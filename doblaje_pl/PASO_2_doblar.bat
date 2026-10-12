@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo  PASO 2: voz polaca, mezcla y control de calidad
echo ==============================================
echo.

if not exist work\no_vocals.wav (
  echo ERROR: falta work\no_vocals.wav. Ejecuta primero PASO_1_separar_voz.bat
  pause
  exit /b 1
)
if exist segments.json copy /y segments.json work\segments.json >nul
if not exist work\segments.json (
  echo ERROR: falta segments.json. Ponlo en esta carpeta, junto a este archivo.
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

echo [1/4] Ajustando los tiempos a la voz española real...
python doblar.py afinar
if errorlevel 1 (
  echo ERROR al ajustar los tiempos. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo [2/4] Generando la voz polaca mc_speech (Piper, local y gratis)...
if exist pronunciacion.json (
  python doblar.py sintetizar --pronunciacion pronunciacion.json
) else (
  python doblar.py sintetizar
)
if errorlevel 1 (
  echo ERROR al generar la voz. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo [3/4] Mezclando con la musica original (el video no se toca)...
python doblar.py mezclar "%VIDEO%" video_pl.mp4
if errorlevel 1 (
  echo ERROR al mezclar. Saca una captura de esta ventana y mandala.
  pause
  exit /b 1
)

echo.
echo [4/4] Control de calidad (la primera vez descarga un modelo, tarda)...
if exist glosario.json (
  python doblar.py qa "%VIDEO%" video_pl.mp4 --glosario glosario.json --modelo medium
) else (
  python doblar.py qa "%VIDEO%" video_pl.mp4 --modelo medium
)
set QAERR=%errorlevel%

echo.
echo ==============================================
if "%QAERR%"=="0" (
  echo  LISTO: video_pl.mp4 aprobado por el control de calidad.
) else (
  echo  El control de calidad encontro FALLOS. Adjunta en el chat el archivo:
  echo     work\qa_reporte.md
)
echo ==============================================
start "" explorer work
pause
