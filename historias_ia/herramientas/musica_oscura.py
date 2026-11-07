#!/usr/bin/env python3
"""Musica de fondo OSCURA y continua (original, numpy), como la de la referencia 3: drone de sub-bajo, pad de cluster menor muy lento, latido grave y tic-tacs
casi imperceptibles, brillo de ruido agudo. Sin melodia ni bateria. pista(dur, segmentos) -> array con rms 1 (mismo contrato que musica_aventura)."""
import numpy as np
SR = 44100
rng = np.random.default_rng(11)
CHORDS = [[55.0, 82.4, 116.5], [43.65, 65.4, 92.5], [49.0, 73.4, 110.0], [41.2, 61.7, 87.3]]      # A, F, G, E con segundas menores (tension)


def lp(x, k):
    c = np.cumsum(np.insert(x, 0, 0.0)); y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k - 1, y[0]), y])


def pista(dur, segmentos=None):
    n = int(dur * SR); t = np.arange(n) / SR
    drone = np.zeros(n)
    for f, g in [(41.2, 1.0), (41.5, 0.6), (82.4, 0.25)]:
        drone += g * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.05 * t))
    drone *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t + 1.0) ** 2
    pad = np.zeros(n); seg = 18.0
    for k in range(int(dur / seg) + 2):
        a, b = int(k * seg * SR), min(n, int((k + 1.25) * seg * SR))
        if a >= n: break
        tt = t[a:b] - k * seg; env = np.sin(np.pi * np.clip(tt / (1.25 * seg), 0, 1)) ** 1.5
        for f in CHORDS[k % 4]:
            for det in (0.996, 1.0, 1.004):
                w = 2 * ((tt * f * det) % 1.0) - 1.0
                pad[a:b] += env * w * 0.12
    pad = lp(pad, 90)                                                                    # sierras -> calido y apagado (< ~500 Hz)
    pad *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t) ** 2
    lat = np.zeros(n)                                                                    # latido grave cada ~1,7 s
    for k in range(int(dur / 1.7)):
        for off, g in ((0.0, 1.0), (0.26, 0.6)):
            i = int((k * 1.7 + off) * SR); L = int(0.22 * SR)
            if i + L < n: tt = np.arange(L) / SR; lat[i:i + L] += g * np.sin(2 * np.pi * (62 * np.exp(-tt * 9) + 34) * tt) * np.exp(-tt * 14)
    tic = np.zeros(n); k0 = int(0.006 * SR)                                              # tic-tac de reloj casi inaudible
    for k in range(int(dur / 0.5)):
        i = int(k * 0.5 * SR)
        if i + k0 < n: tic[i:i + k0] += rng.standard_normal(k0) * np.exp(-np.arange(k0) / (0.0015 * SR)) * (1.0 if k % 2 else 0.6)
    brillo = lp(rng.standard_normal(n), 3) - lp(rng.standard_normal(n), 40)             # aire agudo muy suave
    brillo *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.03 * t) ** 2
    inten = np.ones(n)
    for (a, b, luz) in (segmentos or []):
        g = {"noche": 1.25, "media": 1.0, "clara": 0.8}.get(luz, 1.0); i, j = int(a * SR), min(n, int(b * SR)); inten[i:j] = g
    inten = lp(inten, int(2.0 * SR) | 1)[:n]
    m = (drone * 0.9 + pad * 0.9 + lat * 0.35 + tic * 0.045 + brillo * 0.02) * inten
    return m / (np.sqrt(np.mean(m ** 2)) + 1e-9)
