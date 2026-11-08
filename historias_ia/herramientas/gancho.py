#!/usr/bin/env python3
"""Genera la voz del GANCHO de ~20 s (frase mas perturbadora del caso, con hechos del propio guion) con Voizum y la pega delante de la voz completa.
Uso: VOIZUM_API_KEY=... python3 gancho.py --voz-id ID   -> video/public/completo/gancho.mp3 y voz_total.mp3 (gancho + silencio + voz)"""
import argparse, os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import prueba_4min as P
GANCHO = P.GANCHO
ap = argparse.ArgumentParser(); ap.add_argument("--voz-id", required=True); a = ap.parse_args()
key = os.environ.get("VOIZUM_API_KEY") or sys.exit("falta VOIZUM_API_KEY")
carp = os.path.join(P.RAIZ, "video", "public", "completo"); g = os.path.join(carp, "gancho.mp3")
P.voz_voizum("\n".join(GANCHO), a.voz_id, g, key, 0.92, 650)
sil = os.path.join(carp, "_sil.mp3"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.9", sil], check=True)
lista = os.path.join(carp, "_lista.txt"); open(lista, "w").write(f"file '{g}'\nfile '{sil}'\nfile '{os.path.join(carp, 'voz.mp3')}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-ar", "44100", "-ac", "1", "-c:a", "libmp3lame", "-q:a", "2", os.path.join(carp, "voz_total.mp3")], check=True)
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
print("gancho", round(dur(g), 1), "s; total", round(dur(os.path.join(carp, "voz_total.mp3")) / 60, 2), "min")
