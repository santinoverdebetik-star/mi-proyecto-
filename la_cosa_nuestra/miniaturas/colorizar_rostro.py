#!/usr/bin/env python3
"""Colorizacion estimada de la ficha en blanco y negro de Amado Carrillo: piel con matices (frente mas calida, mejillas rosadas,
labios), pelo/barba/cejas en marron oscuro y ojos castanos. No es el color real (no existe foto a color): es una estimacion."""
import numpy as np, cv2
from PIL import Image

PIEL = [(0, (26, 17, 14)), (60, (86, 54, 40)), (110, (138, 92, 68)), (160, (184, 130, 98)), (210, (216, 164, 128)), (255, (238, 196, 162))]
PELO = [(0, (8, 6, 6)), (45, (32, 24, 20)), (80, (58, 44, 36)), (120, (94, 74, 60)), (255, (140, 112, 92))]


def rampa(g, tabla):
    xs = [p for p, _ in tabla]
    return np.stack([np.interp(g, xs, [c[i] for _, c in tabla]) for i in range(3)], -1)


def mancha(h, w, cx, cy, rx, ry):
    yy, xx = np.mgrid[0:h, 0:w]
    return np.exp(-(((xx / w - cx) / rx) ** 2 + ((yy / h - cy) / ry) ** 2))


def colorizar(cara):
    rgba = np.asarray(cara.convert("RGBA")).astype(np.float32); g = rgba[..., 0]; al = rgba[..., 3]
    h, w = g.shape
    gs = cv2.GaussianBlur(g, (0, 0), 6)
    es_piel = np.clip((gs - 70) / 60, 0, 1)[..., None]                        # zonas claras = piel; oscuras = pelo/barba/cejas
    es_piel = es_piel * np.clip(1.0 - 1.2 * mancha(h, w, 0.5, 0.12, 0.55, 0.12), 0, 1)[..., None] + 0 * es_piel
    gp = 255 * (g / 255.0) ** 1.22                                           # baja un poco los medios (el blanco y negro esta muy quemado)
    piel, pelo = rampa(gp, PIEL), rampa(g, PELO)
    out = piel * es_piel + pelo * (1 - es_piel)
    # matices de la piel
    frente = mancha(h, w, 0.5, 0.30, 0.30, 0.10)[..., None]; out += frente * es_piel * np.array([6, 3, -6])        # frente algo mas calida
    mej = (mancha(h, w, 0.27, 0.58, 0.10, 0.07) + mancha(h, w, 0.73, 0.58, 0.10, 0.07))[..., None]
    out += mej * es_piel * np.array([13, -5, -2]) * (g[..., None] / 255.0)                                          # rubor
    nariz = mancha(h, w, 0.5, 0.58, 0.07, 0.07)[..., None]; out += nariz * es_piel * np.array([14, -4, -2])
    labio = mancha(h, w, 0.5, 0.765, 0.07, 0.018)[..., None]; out += labio * es_piel * np.array([24, -10, -6]) * (g[..., None] / 255.0)
    ojeras = (mancha(h, w, 0.34, 0.50, 0.08, 0.025) + mancha(h, w, 0.65, 0.50, 0.08, 0.025))[..., None]; out += ojeras * es_piel * np.array([-6, -10, -2])
    # ojos castanos: iris oscuro cerca de los ojos con un tono marron
    ojo = (mancha(h, w, 0.335, 0.455, 0.035, 0.022) + mancha(h, w, 0.65, 0.455, 0.035, 0.022))[..., None]
    out += ojo * (1 - np.clip(g[..., None] / 140, 0, 1)) * np.array([28, 10, -4])
    # blancos de los ojos y dientes: casi neutros
    blanco = np.clip((g - 225) / 25, 0, 1)[..., None]; out = out * (1 - 0.45 * blanco) + 238 * 0.45 * blanco
    out = np.clip(out, 0, 255)
    return Image.fromarray(np.dstack([out, al]).astype(np.uint8), "RGBA")
