#!/usr/bin/env bash
# Posproduccion de la voz de La Cosa Nuestra (ecualizacion + compresion + loudness).
# Uso: ./posproducir_voz.sh entrada.mp3 salida.mp3 [perfil]
#   perfil "brian"     (por defecto): voz de biblioteca vidIQ, graves embarrados.
#   perfil "salvatore": voz Voizum "salvatore soprano" (muy grave, poca claridad en medios, sin agudos).
# Ambos terminan en -16 LUFS con pico real <= -1.5 dBFS.
set -euo pipefail
[ $# -ge 2 ] || { echo "Uso: $0 entrada.mp3 salida.mp3 [brian|salvatore]"; exit 1; }
case "${3:-brian}" in
  brian)     EQ="highpass=f=75,equalizer=f=160:t=q:w=1.0:g=-3,equalizer=f=320:t=q:w=1.2:g=-3,equalizer=f=2800:t=q:w=0.9:g=4,equalizer=f=5000:t=q:w=1:g=2,highshelf=f=9000:g=3" ;;
  salvatore) EQ="highpass=f=70,equalizer=f=200:t=q:w=1.0:g=-2.5,equalizer=f=380:t=q:w=1.2:g=-2,equalizer=f=1500:t=q:w=0.9:g=3.5,equalizer=f=3000:t=q:w=0.9:g=3,equalizer=f=5000:t=q:w=1:g=2,highshelf=f=7000:g=2.5" ;;
  *) echo "perfil desconocido: ${3}"; exit 1 ;;
esac
ffmpeg -hide_banner -loglevel error -y -i "$1" -af "$EQ,acompressor=threshold=-20dB:ratio=2.5:attack=15:release=150:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 44100 -ac 1 -b:a 192k "$2"
