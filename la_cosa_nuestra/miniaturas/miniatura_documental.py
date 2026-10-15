#!/usr/bin/env python3
"""Miniatura estilo 'collage documental' (fotos rasgadas, expediente de fondo, rostro grande en COLOR).
El color del rostro es una colorizacion estimada (mapa de color por luminosidad) sobre la ficha en blanco y negro.
Uso: python3 miniatura_documental.py [carpeta_salida]"""
import os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from crear_miniaturas import *

RAMPA = [(0, (8, 7, 8)), (50, (46, 34, 30)), (110, (130, 94, 80)), (170, (190, 146, 124)), (215, (222, 180, 156)), (255, (240, 212, 192))]


def colorizar(cara):
    rgba = np.asarray(cara).astype(np.float32); g = rgba[..., 0]
    xs = [p for p, _ in RAMPA]
    out = np.stack([np.interp(g, xs, [c[i] for _, c in RAMPA]) for i in range(3)], -1)
    ojos = np.clip((g - 215) / 30, 0, 1)[..., None]                         # blancos mas neutros (ojos, dientes)
    out = out * (1 - 0.35 * ojos) + 240 * 0.35 * ojos
    h = np.zeros_like(g); h[g < 55] = 1                                     # pelo/barba: marron muy oscuro, no negro puro
    out = out + h[..., None] * np.array([10, 5, 2])
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), rgba[..., 3]]).astype(np.uint8), "RGBA")


def tira_texto(d, x, y, w, color, seed, n, alto=7, sep=17):
    r = random.Random(seed)
    for i in range(n):
        d.rectangle((x, y + i * sep, x + w * r.uniform(0.45, 1.0), y + i * sep + alto), fill=color)


def expediente(base, xy, tam, rot, mug, rojo=True):
    w, h = tam
    pg = Image.new("RGBA", (w, h), (232, 226, 208, 255)); d = ImageDraw.Draw(pg)
    d.rectangle((0, 0, w, 36), fill=(200, 190, 168, 255)); tira_texto(d, 16, 10, w * 0.5, (90, 80, 70, 255), 1, 1, 14)
    tira_texto(d, 16, 60, w * 0.55, (120, 112, 100, 255), 2, 9)
    tira_texto(d, 16, h - 120, w - 40, (120, 112, 100, 255), 3, 6)
    if rojo:
        for yy, ww in ((88, 150), (122, 110), (190, 170)): d.rectangle((16, yy, 16 + ww, yy + 11), fill=(40, 40, 40, 255))
    m = mug.resize((int(w * 0.32), int(w * 0.32 * 1.15)), Image.LANCZOS)
    pg.paste(m, (w - m.width - 20, 54))
    d.rectangle((w - m.width - 20, 54, w - 20, 54 + m.height), outline=(60, 60, 60, 255), width=2)
    sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); sh.paste(Image.new("RGBA", (w, h), (0, 0, 0, 200)), (30, 30)); sh = sh.filter(ImageFilter.GaussianBlur(12))
    can = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0)); can.alpha_composite(sh, (8, 10)); can.alpha_composite(pg, (30, 30))
    can = can.rotate(rot, resample=Image.BICUBIC, expand=True)
    b = base.convert("RGBA"); b.alpha_composite(can, (int(xy[0] - can.width / 2), int(xy[1] - can.height / 2))); return b.convert("RGB")


def realzar(im, brillo=1.0, sat=1.12, contraste=1.1):
    a = np.asarray(im).astype(np.float32)
    g = a.mean(axis=2, keepdims=True); a = g + (a - g) * sat
    a = (a - 128) * contraste + 128 + (brillo - 1) * 128
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fondo_collage(var="A"):
    """collage a pantalla completa: una foto de fondo que llena el cuadro + fotos grandes rasgadas que casi lo cubren"""
    if var == "A":
        fondo, piezas = "bg_727_niebla.jpg", [("bg_aerea_mexico.jpg", (900, 185, 800, 390), -2, 4), ("bg_learjet.jpg", (700, 545, 640, 350), 3, 3),
                                              ("bg_727_noche.jpg", (1110, 545, 540, 350), -3, 5)]
    else:
        fondo, piezas = "bg_skyline.jpg", [("bg_torre.jpg", (900, 185, 800, 390), -2, 4), ("bg_727_noche.jpg", (700, 545, 640, 350), 3, 3),
                                           ("bg_727_niebla.jpg", (1110, 545, 540, 350), -3, 5)]
    im = realzar(cover(cargar(fondo), W, H), 0.78, 1.0, 1.05)
    for nom, (cx, cy, w, h), rot, sd in piezas:
        im = papel_rasgado(im, realzar(cargar(nom)), (cx - w // 2, cy - h // 2, w, h), seed=sd, rot=rot, borde=8)
    return vineta(im, 0.3)


def base(var="A"):
    im = fondo_collage(var)
    mug = Image.open(A("mugshot_original.png")).convert("RGB").crop((0, 8, 267, 256)).convert("L").convert("RGB")
    return expediente(im, (1090, 175), (350, 280), 5, mug)


def con_cara(im):
    cara = colorizar(rostro(740))
    return con_brillo(im, cara, (10, H - cara.height + 25), (200, 25, 25), radio=22, intens=0.55, borde=11, borde_color=(235, 230, 215))


def va(var="A"):
    return grano(vineta(con_cara(base(var)), 0.3), 4)


def main(out):
    os.makedirs(out, exist_ok=True)
    for n, f in (("miniatura_V6_documental_sin_texto_A", lambda: va("A")), ("miniatura_V6_documental_sin_texto_B", lambda: va("B"))):
        r = os.path.join(out, n + ".jpg"); f().save(r, quality=90, optimize=True); print(r, os.path.getsize(r) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida"))
