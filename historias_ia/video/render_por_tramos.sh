#!/bin/bash
# Render reanudable por tramos de 600 fotogramas (si se corta, volver a ejecutar: salta los tramos ya hechos).
# Uso: ./render_por_tramos.sh props.json nombre [escala]   -> out/nombre_tramo_NN.mp4 y out/nombre.mp4
set -e
PROPS=${1:-props_prueba4.json}; NOMBRE=${2:-prueba4}; ESC=${3:-0.5}
export CHROMIUM_PATH=${CHROMIUM_PATH:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}
TOTAL=$(python3 -c "import json,sys;d=json.load(open('$PROPS'));print(round(sum(e['dur'] for e in d['escenas'])*30))")
PASO=600; N=$(( (TOTAL + PASO - 1) / PASO )); mkdir -p out
for ((i=0;i<N;i++)); do
  A=$((i*PASO)); B=$((A+PASO-1)); [ $B -ge $TOTAL ] && B=$((TOTAL-1))
  F=$(printf "out/%s_tramo_%02d.mp4" "$NOMBRE" $i)
  [ -s "$F" ] && { echo "tramo $i ya existe"; continue; }
  npx remotion render src/index.ts Historia "$F.tmp.mp4" --props="$PROPS" --scale=$ESC --concurrency=4 --crf=22 --frames=$A-$B --muted --log=error && mv "$F.tmp.mp4" "$F"
  echo "tramo $i/$N listo"
done
: > out/lista_$NOMBRE.txt; for ((i=0;i<N;i++)); do printf "file '%s_tramo_%02d.mp4'\n" "$NOMBRE" $i >> out/lista_$NOMBRE.txt; done
ffmpeg -v error -y -f concat -safe 0 -i out/lista_$NOMBRE.txt -c copy out/${NOMBRE}_mudo.mp4
AUDIO=$(python3 -c "import json;print('public/'+json.load(open('$PROPS')).get('voz',''))")
ffmpeg -v error -y -i out/${NOMBRE}_mudo.mp4 -i "$AUDIO" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest out/$NOMBRE.mp4
echo "LISTO out/$NOMBRE.mp4"
