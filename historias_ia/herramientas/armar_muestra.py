#!/usr/bin/env python3
"""Arma la muestra: une las frases de voz con pausas, sintetiza musica oscura + efectos (hits/risers/whoosh), mezcla y escribe
el guion visual (props JSON para Remotion) con las duraciones EXACTAS de cada frase.
Uso: python3 armar_muestra.py carpeta_voz/ (con frases.json) salida_dir"""
import json, os, subprocess, sys
import numpy as np

SR = 44100
rng = np.random.default_rng(11)
PAUSA = 0.45


def leer(r):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", r, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def lp(x, k):
    c = np.cumsum(np.insert(x, 0, 0.0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])


def hit(d=1.4):
    t = np.arange(int(d * SR)) / SR
    return np.sin(2 * np.pi * (52 - 16 * t) * t) * np.exp(-t / 0.35) + 0.3 * lp(rng.normal(0, 1, len(t)), 60) * np.exp(-t / 0.08)


def riser(d=2.2):
    n = int(d * SR); t = np.arange(n) / SR
    r = rng.normal(0, 1, n); f = lp(r, 4) - lp(r, 40)
    return f * (t / d) ** 2.2 * 0.9 + np.sin(2 * np.pi * (80 + 420 * (t / d) ** 2) * t) * (t / d) ** 2.5 * 0.25


def whoosh(d=0.8):
    n = int(d * SR); t = np.arange(n) / SR
    r = rng.normal(0, 1, n); return (lp(r, 5) - lp(r, 80)) * np.sin(np.pi * t / d) ** 2


def golpe_suave(d=0.9):
    """thump grave y seco (sub-bajo que cae de 70 a 38 Hz) + clic corto: marca el corte sin 'soplido'"""
    t = np.arange(int(d * SR)) / SR
    f = 38 + 32 * np.exp(-t / 0.07)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22) + 0.35 * lp(rng.normal(0, 1, len(t)), 12) * np.exp(-t / 0.012)


def glitch(d=0.42):
    """ráfaga digital: pitidos cortos bit-crusheados + crujido de estática"""
    n = int(d * SR); y = np.zeros(n); t = 0.0
    for k in range(7):
        L = int(rng.uniform(0.018, 0.05) * SR); f = rng.choice([620, 930, 1480, 2200, 3100])
        i = int(t * SR); tt = np.arange(L) / SR
        b = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 * np.hanning(L); y[i:i + L] += b[: n - i]; t += rng.uniform(0.02, 0.055)
    y += 0.25 * (rng.random(n) < 0.02) * rng.normal(0, 1, n)
    return np.round(y * 6) / 6 * np.exp(-np.arange(n) / (0.25 * SR))


def succion(d=0.75):
    """hit grave invertido: crece hasta el corte (como algo que 'se acerca') y se corta en seco"""
    h = hit(d)[::-1].copy(); t = np.arange(len(h)) / SR
    return h * (0.4 + 0.6 * (t / d))


def transicion(nombre):
    return {"golpe": (golpe_suave, 0.05), "glitch": (glitch, 0.0), "succion": (succion, 0.72), "whoosh": (whoosh, 0.4)}[nombre]


def drone(dur):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f, a in ((55.0, 1.0), (82.4, 0.55), (110.0, 0.3), (58.3, 0.35)):
        y += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (0.65 + 0.35 * np.sin(2 * np.pi * 0.05 * t + rng.uniform(0, 6)))
    pulso = np.zeros(n); paso = 1.9
    for k in np.arange(0.5, dur - 1, paso):                                       # latido grave lento
        i = int(k * SR); h = np.sin(2 * np.pi * 48 * np.arange(int(0.5 * SR)) / SR) * np.exp(-np.arange(int(0.5 * SR)) / (0.12 * SR)); pulso[i:i + len(h)] += h[: n - i]
    return y / np.abs(y).max() + 0.8 * pulso


def main(vozdir, out, trans="whoosh", nombre="mezcla"):
    os.makedirs(out, exist_ok=True)
    fr = json.load(open(os.path.join(vozdir, "frases.json"), encoding="utf-8"))
    voz = []; t0 = []; t = 0.0
    for f in fr:
        v = leer(f["archivo"]); v = v[: int(len(v) - 0.05 * SR)] if len(v) > SR else v
        t0.append(t); voz.append(np.concatenate([v, np.zeros(int(PAUSA * SR))])); t += (len(v) / SR) + PAUSA
    voz = np.concatenate(voz); D = len(voz) / SR
    v_rms = np.sqrt(np.mean(voz ** 2))
    mus = drone(D); mus *= v_rms * 0.55 / np.sqrt(np.mean(mus ** 2))
    fx = np.zeros(len(voz))
    def poner(x, tt, g):
        i = max(0, int(tt * SR)); fx[i:i + len(x)] += g * x[: len(fx) - i]
    for k, tt in enumerate(t0):
        if k:
            fn, adelanto = transicion(trans); x = fn()
            poner(x, tt - adelanto, 0.5 * v_rms / np.sqrt(np.mean(x ** 2)))
    for k in (4, 6):                                                                # frases de impacto: riser + hit
        poner(riser(), t0[k] - 2.0, 0.5 * v_rms / 0.2); poner(hit(), t0[k] + 0.05, 1.4 * v_rms / np.sqrt(np.mean(hit() ** 2)) * 0.5)
    mez = voz + mus + fx
    fade = np.minimum(1, np.minimum(np.arange(len(mez)) / (1.5 * SR), (len(mez) - np.arange(len(mez))) / (2.0 * SR)))
    mez *= fade; mez *= 0.9 / max(0.9, np.abs(mez).max())
    raw = (mez * 32767).astype("<i2").tobytes()
    wav = os.path.join(out, "mezcla.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-c:a", "libmp3lame", "-q:a", "2", os.path.join(out, nombre + ".mp3")], input=raw, check=True)
    ends = [t0[i + 1] if i + 1 < len(t0) else D for i in range(len(t0))]
    json.dump({"t0": t0, "dur": D, "ends": ends}, open(os.path.join(out, "tiempos.json"), "w"))
    print("duracion", round(D, 1), "s; inicios", [round(x, 1) for x in t0])


if __name__ == "__main__":
    main(*sys.argv[1:5])
