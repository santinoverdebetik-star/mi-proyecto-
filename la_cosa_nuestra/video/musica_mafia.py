#!/usr/bin/env python3
"""Musica de fondo de estilo 'mafia de cine' (vals en menor con mandolina en tremolo, guitarra, acordeon y contrabajo),
sintetizada con numpy (cuerdas pulsadas por Karplus-Strong). Melodia y armonia ORIGINALES (no copian ningun tema existente).

Uso desde musica.py:  pista(modo, dur_segundos) -> array con rms 1
Modos: A vals sombrio | B vals ironico, mas seco | C tension (pedal grave + notas sueltas) | D acordeon melancolico, lento"""
import functools
import numpy as np

SR = 44100
rng = np.random.default_rng(21)
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(n):
    nombre, octava = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTAS[nombre] + 12 * (octava - 4) - 9) / 12)


@functools.lru_cache(maxsize=4096)
def pulsada(f, dur, brillo=0.55, amort=0.9965):
    """cuerda pulsada (Karplus-Strong), dur en pasos de 0.05 s"""
    n_out = int(dur * SR); L = max(2, int(round(SR / f - 0.5)))
    f_real = SR / (L + 0.5); paso = f / f_real                      # remuestreo fino para afinar exacto
    n = int(n_out * paso) + 4
    r = np.random.default_rng(int(f * 10) % 100000)
    b = r.uniform(-1, 1, L); b -= b.mean()
    for _ in range(2):                                   # suavizar el ataque (menos 'metalico')
        b = (1 - brillo) * b + brillo * np.roll(b, 1)
    y = np.zeros(n + L + 2)
    y[:L] = b
    k = L
    while k < n + 1:
        m = min(L, n + 1 - k)
        y[k:k + m] = amort * 0.5 * (y[k - L:k - L + m] + y[k - L - 1:k - L - 1 + m]) if k > L else amort * 0.5 * (y[0:m] + np.roll(y[:L], 1)[:m])
        k += L
    y = y[:n]
    y = np.interp(np.arange(n_out) * paso, np.arange(len(y)), y)
    y *= np.minimum(1, np.arange(n_out) / (0.002 * SR))
    return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)


def poner(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0: return
    j = min(len(buf), i + len(x))
    buf[i:j] += g * x[: j - i]


def mandolina(buf, nota, t, dur, g, tremolo=True):
    f = hz(nota)
    if not tremolo or dur < 0.2:
        poner(buf, pulsada(f, 1.0, 0.6, 0.994), t, g); return
    paso = 0.085; k = 0
    while k * paso < dur:
        poner(buf, pulsada(f, 0.45, 0.7, 0.991), t + k * paso, g * (1.0 if k else 1.25) * (0.92 + 0.08 * (k % 2)))
        k += 1


def acordeon(buf, notas, t, dur, g):
    n = int(dur * SR)
    if n <= 0 or t * SR >= len(buf): return
    tt = np.arange(n) / SR
    y = np.zeros(n)
    for nota in notas:
        f = hz(nota)
        for d in (-0.7, 0.7):                                                    # dos lengüetas desafinadas
            vib = 1 + 0.004 * np.sin(2 * np.pi * 5.3 * tt + rng.uniform(0, 6))
            y += sum((1 / k ** 1.1) * np.sin(2 * np.pi * (f + d) * k * tt * vib) for k in (1, 2, 3, 4, 5, 6))
    ata = np.minimum(1, tt / 0.25) * np.minimum(1, (dur - tt) / 0.35)
    poner(buf, (y * ata * (0.85 + 0.15 * np.sin(2 * np.pi * 0.35 * tt))).astype(np.float32), t, g / max(1, len(notas)))


# acordes (notas graves de guitarra y triada)
ACORDES = {"Am": ("A2", ["A3", "C4", "E4"]), "E7": ("E2", ["G#3", "B3", "D4"]), "Dm": ("D2", ["A3", "D4", "F4"]),
           "F": ("F2", ["A3", "C4", "F4"]), "G": ("G2", ["B3", "D4", "G4"]), "C": ("C3", ["G3", "C4", "E4"]),
           "Bm": ("B2", ["F#3", "B3", "D4"])}
# 16 compases (3/4): armonia y melodia original (nota, pulsos) por compas
ARMONIA = ["Am", "Am", "E7", "Am", "Dm", "Am", "E7", "Am", "Am", "F", "E7", "Am", "Dm", "G", "E7", "Am"]
MELODIA = [
    [("A4", 2), ("C5", 1)], [("E5", 3)], [("D5", 1), ("C5", 1), ("B4", 1)], [("A4", 3)],
    [("F4", 1), ("A4", 1), ("D5", 1)], [("C5", 2), ("B4", 1)], [("G#4", 2), ("B4", 1)], [("A4", 3)],
    [("E5", 2), ("A5", 1)], [("F5", 2), ("E5", 1)], [("D5", 1), ("B4", 1), ("G#4", 1)], [("A4", 3)],
    [("D5", 2), ("F5", 1)], [("E5", 2), ("D5", 1)], [("B4", 1), ("G#4", 1), ("B4", 1)], [("A4", 3)],
]


def vals(dur, bpm, modo):
    n = int(dur * SR); y = np.zeros(n)
    beat = 60.0 / bpm; barra = 3 * beat; nb = int(dur / barra) + 1
    for b in range(nb):
        t0 = b * barra; ac = ARMONIA[b % 16]; grave, tri = ACORDES[ac]
        seco = modo == "B"
        poner(y, pulsada(hz(grave), 0.9, 0.5, 0.996 if not seco else 0.992), t0, 1.0)            # contrabajo / bajo en el 1
        for p in (1, 2):                                                                         # 'pah-pah' de guitarra
            for k, nt in enumerate(tri):
                poner(y, pulsada(hz(nt), 0.7, 0.55, 0.994), t0 + p * beat + k * 0.012, 0.42)
        # melodia (silencio en los compases 0-1 de cada vuelta para respirar si modo D)
        pos = t0
        for nota, pulsos in MELODIA[b % 16]:
            d = pulsos * beat
            if modo in ("A", "B"):
                mandolina(y, nota, pos, d, 0.55 if modo == "A" else 0.7, tremolo=(modo == "A"))
            elif modo == "D":
                acordeon(y, [nota, nota[:-1] + str(int(nota[-1]) - 1)], pos, d * 0.98, 0.9)
            pos += d
        if modo in ("A", "D"):                                                                   # colchon de acordeon
            acordeon(y, [t_ for t_ in tri[:2]], t0, barra, 0.35 if modo == "A" else 0.5)
    return y


def tension(dur):
    n = int(dur * SR); y = np.zeros(n)
    tt = np.arange(n) / SR
    for f in (55.0, 58.3):                                                                       # A1 y Bb1 (segunda menor)
        y += np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.06 * tt + rng.uniform(0, 6)))
    t = 2.0
    notas = ["A3", "A#3", "E4", "A3", "C4", "B3", "A3", "G#3"]; k = 0
    while t < dur - 2:
        mandolina(y, notas[k % len(notas)], t, 1.2, 0.5, tremolo=(k % 3 == 0)); k += 1; t += rng.uniform(3.0, 5.5)
    t = 0.5
    while t < dur - 1:                                                                           # latido grave
        poner(y, pulsada(46.0, 0.5, 0.3, 0.99), t, 1.1); t += 2.4
    return y


def pista(modo, dur):
    if modo == "C":                                   # tension: el mismo vals, mas lento y oscuro, con latido y notas graves (siempre audible)
        base = vals(dur, 72, "A"); tens = tension(dur)
        y = base / (np.sqrt(np.mean(base ** 2)) + 1e-9) + 0.35 * tens / (np.sqrt(np.mean(tens ** 2)) + 1e-9)
    elif modo == "A": y = vals(dur, 84, "A")
    elif modo == "B": y = vals(dur, 100, "B")
    else: y = vals(dur, 66, "D")
    # un poco de eco de sala
    for d, g in ((0.19, 0.28), (0.41, 0.16)):
        k = int(d * SR); y[k:] += g * y[:-k]
    y = y - y.mean()                                                       # quita la continua y suaviza el brillo
    k = 3; c = np.cumsum(np.insert(y, 0, 0.0)); suave = np.concatenate([y[: k - 1], (c[k:] - c[:-k]) / k])
    y = 0.55 * y + 0.45 * suave
    return (y / (np.sqrt(np.mean(y ** 2)) + 1e-9)).astype(np.float64)
