#!/usr/bin/env python3
"""Transcribe el audio con faster-whisper y guarda palabras con tiempos: alinear_whisper.py audio.mp3 salida.json"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=3)
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout, np.float32)
seg, info = m.transcribe(audio, language="es", word_timestamps=True, beam_size=3, vad_filter=False)
palabras = []
for s in seg:
    for w in (s.words or []):
        palabras.append({"w": w.word.strip(), "t0": round(w.start, 3), "t1": round(w.end, 3)})
    print(round(s.end), "s", flush=True)
json.dump({"duracion": info.duration, "palabras": palabras}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print("LISTO", len(palabras), "palabras")
