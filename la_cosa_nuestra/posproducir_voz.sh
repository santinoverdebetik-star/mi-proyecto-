#!/usr/bin/env bash
# Posproduccion de la voz de La Cosa Nuestra (ecualizacion + compresion + loudness).
# Uso: ./posproducir_voz.sh entrada.mp3 salida.mp3
# Cadena: pasaaltos 75 Hz, recorte de graves/barro (160 y 320 Hz), presencia (2,8 kHz y 5 kHz),
# aire (>9 kHz), compresion suave 2.5:1 y normalizacion a -16 LUFS (pico real -1.5 dBFS).
set -euo pipefail
[ $# -eq 2 ] || { echo "Uso: $0 entrada.mp3 salida.mp3"; exit 1; }
ffmpeg -hide_banner -loglevel error -y -i "$1" -af "highpass=f=75,equalizer=f=160:t=q:w=1.0:g=-3,equalizer=f=320:t=q:w=1.2:g=-3,equalizer=f=2800:t=q:w=0.9:g=4,equalizer=f=5000:t=q:w=1:g=2,highshelf=f=9000:g=3,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=150:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 44100 -ac 1 -b:a 192k "$2"
