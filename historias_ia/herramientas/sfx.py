"""Efectos de sonido sinteticos (numpy) para las pantallas y transiciones: whoosh, pop, blips de 8 bits, ding, ping de radar, tecleo."""
import numpy as np
SR = 44100
rng = np.random.default_rng(7)

def _env(n, a=0.01, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)

def whoosh(d=0.5, f0=400, f1=5000):
    n = int(d * SR); x = rng.standard_normal(n); y = np.zeros(n); s = 0.0
    fc = np.geomspace(f0, f1, n) if f1 > f0 else np.geomspace(f0, f1, n)
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    for i in range(n): s += a[i] * (x[i] - s); y[i] = s
    hp = y - np.convolve(y, np.ones(200) / 200, mode="same")                  # quita graves
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.6
    return hp * env / (np.abs(hp * env).max() + 1e-9)

def pop(f=520):
    n = int(0.16 * SR); t = np.arange(n) / SR
    fr = f * np.exp(-t * 9) + 140; ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * _env(n, 0.002, 0.045)

def blips(notas=(523, 659, 784), paso=0.045):
    out = np.zeros(int((paso * len(notas) + 0.08) * SR))
    for k, f in enumerate(notas):
        n = int(paso * 1.4 * SR); t = np.arange(n) / SR
        w = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 * _env(n, 0.002, 0.05)
        i = int(k * paso * SR); out[i:i + n] += w[: len(out) - i]
    return out

def ding(f=1320):
    n = int(0.7 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t)) * _env(n, 0.003, 0.18)

def ping(f=880):
    n = int(0.6 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * _env(n, 0.004, 0.14)

def tick():
    n = int(0.012 * SR); return rng.standard_normal(n) * _env(n, 0.0005, 0.003)

def golpe_grave():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (70 * np.exp(-t * 6) + 38) * t * 1.0) * _env(n, 0.002, 0.14)
