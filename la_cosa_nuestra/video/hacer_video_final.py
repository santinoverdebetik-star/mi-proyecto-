#!/usr/bin/env python3
"""Hace el video completo (sin subtitulos) con UN comando.

Uso (desde la carpeta la_cosa_nuestra/video):
    python hacer_video_final.py                     # video completo -> ../../salida/La_Cosa_Nuestra_V5.mp4
    python hacer_video_final.py --desde 128 --hasta 248 --salida prueba.mp4   # solo un trozo (prueba)

Requisitos: Python 3, ffmpeg en el PATH y  pip install numpy opencv-python-headless pillow
Antes: deja tus clips de la serie en  trabajo/clips/slot_NN.mp4  (los huecos sin clip siguen con fotos).

Pasos: 1) mezcla voz + musica de mafia (volumen 6 %, normalizada a -16 LUFS)
       2) plan de cortes (huecos solo si hay clip)  3) render en paralelo  4) une video + audio
"""
import argparse, os, shutil, subprocess, sys, json

AQUI = os.path.dirname(os.path.abspath(__file__))
TRAB = os.path.join(AQUI, "trabajo")


def correr(cmd, env=None):
    print(">", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env={**os.environ, **(env or {})})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", type=float, default=0.0)
    ap.add_argument("--hasta", type=float, default=None)
    ap.add_argument("--procesos", type=int, default=max(1, min(4, os.cpu_count() or 2)))
    ap.add_argument("--salida", default=os.path.join(AQUI, "..", "..", "salida", "La_Cosa_Nuestra_V5.mp4"))
    ap.add_argument("--musica", default="0.06", help="volumen de la musica respecto a la voz (0.06 = 6 %)")
    a = ap.parse_args()
    py = sys.executable
    timeline = os.path.join(TRAB, "timeline.json")
    voz = os.path.join(TRAB, "voz_final.mp3")
    dur = json.load(open(timeline, encoding="utf-8"))["duracion"]
    hasta = a.hasta or dur
    raw, mezcla = os.path.join(TRAB, "mezcla_raw.wav"), os.path.join(TRAB, "mezcla.wav")
    # 1) audio
    correr([py, os.path.join(AQUI, "musica.py"), timeline, voz, raw], {"MAFIA": "1", "MUSIC_GAIN": a.musica})
    correr(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "44100", mezcla])
    if a.desde > 0 or a.hasta:                                    # recortar el audio si es una prueba
        recorte = os.path.join(TRAB, "mezcla_trozo.wav")
        correr(["ffmpeg", "-v", "error", "-y", "-ss", str(a.desde), "-t", str(hasta - a.desde), "-i", mezcla, recorte])
        mezcla = recorte
    # 2) plan (los huecos solo existen si hay clip en trabajo/clips)
    for f in os.listdir(TRAB):
        if f.startswith("parte_") and f.endswith(".mp4"): os.remove(os.path.join(TRAB, f))
    correr([py, os.path.join(AQUI, "armar_video.py"), "plan", timeline, TRAB], {"SOLO_CON_CLIP": "1"})
    # 3) render
    correr([py, os.path.join(AQUI, "armar_video.py"), "render", timeline, TRAB, str(a.desde), str(hasta), str(a.procesos)], {"SIN_SUBS": "1"})
    # 4) unir
    salida = os.path.abspath(a.salida)
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    correr([py, os.path.join(AQUI, "armar_video.py"), "unir", TRAB, mezcla, salida])
    print("\nListo:", salida)


if __name__ == "__main__":
    main()
