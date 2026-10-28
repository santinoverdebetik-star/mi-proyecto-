#!/usr/bin/env python3
"""Música de fondo de AVENTURA / misterio cinematográfico (original, sintetizada con numpy):
cuerdas en pad, ostinato de bajo, arpegio pulsado, bombo/caja/hi-hat suaves. Suena en el rango medio (200 Hz – 5 kHz) para que
se oiga también en altavoces pequeños de laptop o móvil (el drone grave anterior casi no se oía allí).
pista(dur, segmentos) -> array con rms 1.  segmentos = [(t0, t1, 'noche'|'media'|'clara'), ...] controla la intensidad."""
import numpy as np
import musica_mafia as mm      # reutiliza la cuerda pulsada (Karplus-Strong)

SR = 44100
BPM = 104
rng = np.random.default_rng(31)
# progresión Am – F – C – G (un compás cada acorde); notas (bajo, [triada])
PROG = [("A2", ["A3", "C4", "E4"]), ("F2", ["A3", "C4", "F4"]), ("C3", ["G3", "C4", "E4"]), ("G2", ["G3", "B3", "D4"])]
ARP = [0, 2, 1, 2, 0, 2, 1, 2]          # índice de nota de la triada por corchea
ARP_ALTA = [1, 2, 0, 2, 1, 2, 0, 1]


def lp(x, k):
    c = np.cumsum(np.insert(x, 0, 0.0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])


def poner(buf, x, t, g=1.0):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += g * x[: j - i]


def cuerda(f, d):
    """pad de cuerdas: 3 sierras desafinadas, filtradas, con ataque lento"""
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for det in (-0.6, 0.0, 0.7):
        fr = f + det; y += 2 * ((t * fr) % 1.0) - 1.0
    y = lp(y, 6) * (1 + 0.1 * np.sin(2 * np.pi * 5.2 * t))
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.45)
    return y * env


def bajo(f, d=0.3):
    t = np.arange(int(d * SR)) / SR
    y = np.sin(2 * np.pi * f * t) + 0.55 * np.sin(2 * np.pi * 2 * f * t) + 0.3 * np.sin(2 * np.pi * 3 * f * t)   # armónicos: se oye en altavoces chicos
    return y * np.exp(-t / 0.16) * np.minimum(1, t / 0.004)


def bombo():
    t = np.arange(int(0.35 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(48 + 80 * np.exp(-t / 0.04)) / SR) * np.exp(-t / 0.13) + 0.2 * lp(rng.normal(0, 1, len(t)), 3) * np.exp(-t / 0.01)


def caja():
    t = np.arange(int(0.2 * SR)) / SR; r = rng.normal(0, 1, len(t))
    return (r - lp(r, 12)) * np.exp(-t / 0.05) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)


def hat():
    t = np.arange(int(0.06 * SR)) / SR; r = rng.normal(0, 1, len(t))
    return (r - lp(r, 4)) * np.exp(-t / 0.014)


def hz(n): return mm.hz(n)


def pista(dur, segmentos=None):
    n = int(dur * SR); y = np.zeros(n)
    beat = 60.0 / BPM; barra = 4 * beat; corchea = beat / 2
    def mood(t):
        for a, b, m in (segmentos or []):
            if a <= t < b: return m
        return "media"
    k = 0
    for b in range(int(dur / barra) + 2):
        t0 = b * barra; m = mood(t0); raiz, tri = PROG[b % 4]
        # pad de cuerdas (todo el compás, se solapa con el siguiente)
        for nt in tri: poner(y, cuerda(hz(nt), barra + 0.5), t0, 0.5 if m != "noche" else 0.42)
        poner(y, cuerda(hz(raiz[:-1] + str(int(raiz[-1]) + 1)), barra + 0.5), t0, 0.35)
        # ostinato de bajo en corcheas
        for i in range(8):
            if i in (1, 5) and m == "noche": continue
            poner(y, bajo(hz(raiz)), t0 + i * corchea, 0.9 if i % 4 == 0 else 0.55)
        # arpegio (más presente y alto cuando hay más luz)
        patron = ARP_ALTA if m == "clara" else ARP
        for i, idx in enumerate(patron):
            nota = tri[idx % 3]; oct_ = int(nota[-1]) + (2 if m == "clara" else 1)
            poner(y, mm.pulsada(hz(nota[:-1] + str(oct_)), 0.6, 0.55, 0.994), t0 + i * corchea, 0.42 if m == "noche" else 0.6)
        # percusión
        poner(y, bombo(), t0, 0.9); poner(y, bombo(), t0 + 2 * beat, 0.75)
        if m != "noche":
            poner(y, caja(), t0 + beat, 0.35); poner(y, caja(), t0 + 3 * beat, 0.35)
        if m == "clara":
            for i in range(8): poner(y, hat(), t0 + i * corchea + (corchea / 2 if i % 2 else 0), 0.14)
    y = y[:n]; y = y - lp(y, 500)                                              # quita graves < ~90 Hz (no suenan en altavoces chicos)
    for d, g in ((0.23, 0.22), (0.47, 0.12)): kk = int(d * SR); y[kk:] += g * y[:-kk]      # eco de sala
    return (y / (np.sqrt(np.mean(y ** 2)) + 1e-9)).astype(np.float64)


if __name__ == "__main__":
    import sys, subprocess
    d = float(sys.argv[1]) if len(sys.argv) > 1 else 30
    x = pista(d, [(0, d / 3, "noche"), (d / 3, 2 * d / 3, "media"), (2 * d / 3, d, "clara")])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", sys.argv[2] if len(sys.argv) > 2 else "aventura.mp3"],
                   input=(np.clip(x * 0.25, -1, 1) * 32767).astype("<i2").tobytes(), check=True)
