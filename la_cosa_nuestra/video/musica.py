#!/usr/bin/env python3
"""Genera por sintesis (numpy) un ambiente oscuro (drones, piano lento, contrabajo, percusion suave, cuerdas)
y los efectos (whoosh al cambiar de bloque, golpe grave en cada sello), y los mezcla con la voz.

Uso: python3 musica.py timeline.json voz.mp3 salida.wav
Es un sustituto sencillo: para el video final conviene cambiar la pista por una real de la Biblioteca de audio
de YouTube (sin atribucion) y dejar solo los efectos."""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import musica_mafia

SR = 44100
rng = np.random.default_rng(7)


def leer(ruta):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)) + 1e-9)


def lowpass(x, k):
    """media movil como filtro paso bajo barato"""
    c = np.cumsum(np.insert(x, 0, 0.0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])


def eco(x, taps):
    y = x.copy()
    for d, g in taps:
        n = int(d * SR)
        y[n:] += g * x[:-n]
    return y


def nota(f, dur, tau, arm=(1, .5, .25, .12), ataque=0.006):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(arm))
    env = np.exp(-t / tau) * np.minimum(1, t / ataque)
    return s * env


def poner(buf, nota_, t):
    i = int(t * SR)
    if i < len(buf):
        j = min(len(buf), i + len(nota_))
        buf[i:j] += nota_[: j - i]


def drone(dur, raiz):
    n = int(dur * SR)
    t = np.arange(n) / SR
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + rng.uniform(0, 6))
    y = np.zeros(n)
    for mult, a, det in [(1, 1.0, 0.0), (2, 0.55, 0.15), (3, 0.28, -0.2), (1.5, 0.4, 0.1), (4, 0.12, 0.3)]:
        y += a * np.sin(2 * np.pi * (raiz * mult + det) * t + rng.uniform(0, 6))
    y *= lfo
    ruido = np.cumsum(rng.normal(0, 1, n)); ruido -= lowpass(ruido, 4000); ruido = lowpass(ruido, 40)
    y += 0.8 * ruido / (rms(ruido) + 1e-9) * rms(y) * 0.25
    return y


def pistas(modo, dur):
    n = int(dur * SR)
    A = {"A": 55.0, "B": 49.0, "C": 41.2, "D": 55.0}[modo]
    y = drone(dur, A / 2) * 1.0
    pent = [220.0, 261.6, 293.7, 329.6, 392.0, 440.0]
    if modo in ("A", "D"):          # piano lento
        capa = np.zeros(n); t = rng.uniform(1, 4)
        while t < dur - 3:
            f = rng.choice(pent) * (0.5 if rng.random() < 0.4 else 1.0)
            poner(capa, nota(f, 3.5, 1.5 if modo == "A" else 2.0), t)
            if rng.random() < 0.35: poner(capa, nota(f * 1.5, 3.0, 1.3, (1, .3, .1)), t + 0.22)
            t += rng.uniform(4.0, 8.5 if modo == "A" else 11)
        y = y + 1.6 * rms(y) * eco(capa, [(0.38, .35), (0.77, .22), (1.3, .12)]) / (rms(capa) + 1e-9) * 0.35
    if modo == "B":                  # contrabajo en pizzicato, algo ironico
        capa = np.zeros(n); paso = 60 / 72; t = 0.5; seq = [41.2, 49.0, 55.0, 49.0, 41.2, 36.7, 41.2, 55.0]; k = 0
        while t < dur - 1:
            poner(capa, nota(seq[k % len(seq)] * 2, 0.5, 0.18, (1, .6, .2), 0.004), t); k += 1; t += paso
        y = y * 0.7 + 1.2 * rms(y) * capa / (rms(capa) + 1e-9) * 0.5
    if modo == "C":                  # tension: latido grave + clicks suaves
        capa = np.zeros(n); t = 0.5
        while t < dur - 1:
            poner(capa, nota(52, 0.45, 0.14, (1, .3)), t); poner(capa, nota(52, 0.45, 0.14, (1, .3)) * 0.6, t + 0.42)
            t += 2.4
        tick = np.zeros(n); t = 1.7
        while t < dur - 1:
            ruido = rng.normal(0, 1, int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / (0.006 * SR))
            poner(tick, ruido, t); t += 2.4
        y = y * 0.8 + 1.1 * rms(y) * capa / (rms(capa) + 1e-9) * 0.5 + 0.2 * rms(y) * tick / (rms(tick) + 1e-9)
    if modo == "D":                  # cuerdas largas
        capa = np.zeros(n); tt = np.arange(n) / SR
        for f in (110.0, 130.8, 164.8, 220.0):
            for d in (-0.4, 0.4):
                capa += sum((1 / k) * np.sin(2 * np.pi * (f + d) * k * tt + rng.uniform(0, 6)) for k in (1, 2, 3, 4))
        capa *= (0.5 - 0.5 * np.cos(2 * np.pi * tt / 22.0)) ** 1.5       # swell lento
        y = y * 0.7 + 1.3 * rms(y) * capa / (rms(capa) + 1e-9) * 0.55
    return y / rms(y)


def whoosh(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    r = rng.normal(0, 1, n)
    f = lowpass(r, 6) - lowpass(r, 90)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.2
    return f * env


def golpe(dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * (58 - 18 * t) * t) * np.exp(-t / 0.22)
            + 0.25 * lowpass(rng.normal(0, 1, len(t)), 50) * np.exp(-t / 0.05))


def main(timeline, voz, salida):
    tl = json.load(open(timeline, encoding="utf-8"))
    v = leer(voz); D = len(v) / SR
    mood = {"gancho": "A", "sellos": "A", "cierre": "D"}
    def modo_bloque(b, parte):
        if b["tipo"] in mood: return mood[b["tipo"]]
        return {1: "B", 2: "B", 3: "C", 4: "C", 5: "D"}.get(parte, "A")
    secciones = []; parte = 0
    for b in tl["bloques"]:
        if b["tipo"] == "parte":
            parte = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}[b["n"]]
        secciones.append((b["t0"], b["t1"], modo_bloque(b, parte)))
    # fusionar bloques contiguos del mismo modo
    fus = []
    for a, b_, m in secciones:
        if fus and fus[-1][2] == m: fus[-1] = (fus[-1][0], b_, m)
        else: fus.append((a, b_, m))
    cf = 3.0
    musica = np.zeros(len(v))
    for a, b_, m in fus:
        dur = (b_ - a) + 2 * cf
        seg = musica_mafia.pista(m, dur) if os.environ.get('MAFIA') else pistas(m, dur)
        i0 = int((a - cf) * SR); n = len(seg)
        env = np.ones(n); k = int(cf * SR)
        env[:k] = np.sin(np.linspace(0, np.pi / 2, k)); env[-k:] = np.cos(np.linspace(0, np.pi / 2, k))
        seg = seg * env
        s0, s1 = max(0, i0), min(len(musica), i0 + n)
        musica[s0:s1] += seg[s0 - i0: s1 - i0]
    musica *= rms(v) * float(os.environ.get("MUSIC_GAIN", "0.12")) / rms(musica)           # musica al ~12 % de la voz
    # bajar un poco la musica en la intro de cada bloque? (sin clips de serie, se mantiene fija)
    if os.environ.get('MUSIC_ONLY_OUT'):
        ffm0 = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', os.environ['MUSIC_ONLY_OUT']], stdin=subprocess.PIPE)
        ffm0.communicate((np.clip(musica, -1, 1) * 32767).astype('<i2').tobytes())
    fx = np.zeros(len(v))
    for b in tl["bloques"]:
        if b["tipo"] in ("parte", "regla", "cierre", "sellos") and b["t0"] > 1:
            w = whoosh(); poner(fx, w * 0.35 * rms(v) / (rms(w) + 1e-9) * 0.9, max(0, b["t0"] - 0.35))
        if b["tipo"] == "regla" and "t_sello" in b:
            g = golpe(); poner(fx, g * rms(v) * 0.85 / (rms(g) + 1e-9), b["t_sello"] + 0.2)
    mezcla = v + musica + fx
    pico = np.abs(mezcla).max()
    if pico > 0.93: mezcla *= 0.93 / pico
    s16 = (mezcla * 32767).astype("<i2")
    ffm = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", salida],
                           stdin=subprocess.PIPE)
    ffm.communicate(s16.tobytes())
    print(f"mezcla lista: {D / 60:.1f} min | secciones de musica: {[(round(a), m) for a, _, m in fus]}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
