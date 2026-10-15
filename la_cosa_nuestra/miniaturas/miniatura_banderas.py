#!/usr/bin/env python3
"""Miniatura Ovidio: bandera de EE.UU. a la izquierda, Palacio Nacional con la bandera de Mexico a la derecha, rostro completo al centro.
Uso: python3 miniatura_banderas.py [carpeta_salida]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from crear_miniaturas import *
from miniatura_documental import realzar


def rostro_ovidio(altura):
    im = Image.open(A("ovidio_recorte2.png")).convert("RGBA")
    ys, xs = np.nonzero(np.asarray(im.split()[3]) > 20)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 90, 2))
    rgb = realzar(rgb, 1.02, 1.12, 1.1); rgb.putalpha(im.split()[3])
    return rgb.resize((int(rgb.width * altura / rgb.height), altura), Image.LANCZOS)


def mitad(nombre, caja, w, h, k, rgb):
    im = cargar(nombre); x0, y0, x1, y1 = caja
    im = im.crop((int(im.width * x0), int(im.height * y0), int(im.width * x1), int(im.height * y1)))
    im = cover(im, w, h)
    a = np.asarray(realzar(im, 1.0, 1.1, 1.12)).astype(np.float32) * k * np.array(rgb, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def grunge(im, seed=2, fuerza=0.22):
    """aspecto de bandera vieja: manchas de desgaste, grano de papel y colores algo apagados"""
    import cv2
    a = np.asarray(im).astype(np.float32); r = np.random.default_rng(seed)
    g = a.mean(axis=2, keepdims=True); a = g + (a - g) * 0.82
    gran = cv2.GaussianBlur(r.normal(0, 1, a.shape[:2]).astype(np.float32), (0, 0), 25) * 60
    fino = cv2.GaussianBlur(r.normal(0, 1, a.shape[:2]).astype(np.float32), (0, 0), 1.0) * 10
    pliegue = (r.random(a.shape[:2]) < 0.0006).astype(np.float32); pliegue = cv2.GaussianBlur(pliegue, (0, 0), 2.5) * 900
    a = a * (1 - fuerza) + (a + gran[..., None] + fino[..., None] + pliegue[..., None]) * fuerza + 6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def insignia(im, centro, r=40):
    """sello azul de cuenta verificada"""
    S = 4; capa = Image.new("RGBA", (2 * r * S + 8, 2 * r * S + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(capa); c = r * S + 4
    import math
    pts = [(c + (r * S * (0.88 + 0.12 * math.cos(8 * t))) * math.cos(t), c + (r * S * (0.88 + 0.12 * math.cos(8 * t))) * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 400)]
    d.polygon(pts, fill=(29, 155, 240, 255))
    d.line([(c - 0.36 * r * S, c + 0.02 * r * S), (c - 0.1 * r * S, c + 0.28 * r * S), (c + 0.4 * r * S, c - 0.26 * r * S)], fill=(255, 255, 255, 255), width=int(0.16 * r * S), joint="curve")
    capa = capa.resize((capa.width // S, capa.height // S), Image.LANCZOS)
    b = im.convert("RGBA"); b.alpha_composite(capa, (int(centro[0] - capa.width / 2), int(centro[1] - capa.height / 2))); return b.convert("RGB")


def marco(im, g=9):
    d = ImageDraw.Draw(im)
    for i in range(g):
        v = int(170 - 8 * abs(i - g / 2) * 2); d.rectangle((i, i, W - 1 - i, H - 1 - i), outline=(v, v, v + 6))
    return im


def miniatura(variante="A"):
    izq = grunge(mitad("bg_bandera_eeuu.jpg", (0.17, 0.20, 0.60, 0.62), 760, H, 1.05, (1.0, 1.0, 1.04)))
    if variante == "A": der = mitad("bg_palacio_bandera.jpg", (0.12, 0.0, 0.88, 1.0), 760, H, 1.05, (0.94, 1.0, 1.12))
    else: der = mitad("bg_palacio_bandera2.jpg", (0.0, 0.20, 0.36, 0.66), 760, H, 1.05, (1.03, 1.0, 0.97))
    im = Image.new("RGB", (W, H))
    ramp = np.clip((np.linspace(0, 1, 760) - 0.55) / 0.45, 0, 1); ramp = 1 - ramp * ramp * (3 - 2 * ramp)
    m = Image.fromarray((np.tile(ramp, (H, 1)) * 255).astype(np.uint8))
    im.paste(der, (W - 760, 0)); im.paste(izq, (0, 0), m)
    im = vineta(im, 0.45)
    cara = rostro_ovidio(610)
    x = (W - cara.width) // 2 + 30
    im = con_brillo(im, cara, (x, H - cara.height + 14), (0, 0, 0), radio=26, intens=0.85, borde=0)
    sz = 80; nombre = "Ovidio Guzmán"
    im = texto(im, (36, 16), nombre, sz, BLANCO, trazo=0, sombra=True, ancla="la")
    wtxt = ancho_texto(nombre, sz, 0)
    im = insignia(im, (40 + wtxt + int(sz * 0.55), 14 + int(sz * 0.64)), int(sz * 0.39))
    return marco(grano(im, 4))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
    for v in "AB":
        r = os.path.join(out, f"miniatura_OVIDIO_banderas_{v}.jpg"); miniatura(v).save(r, quality=92, optimize=True); print(r)
