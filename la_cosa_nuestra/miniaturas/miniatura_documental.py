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


def oscura(im, k=0.55, color=None):
    a = np.asarray(im).astype(np.float32) * k
    if color: a = a * (np.array(color, np.float32) / 255)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def fondo_collage():
    im = Image.new("RGB", (W, H), (12, 8, 8))
    gris = lambda n: cargar(n).convert("L").convert("RGB")
    piezas = [("R5_02.jpg", (860, 520, 520, 330), 4, 1, (255, 150, 110)), ("ov_G10_05.jpg", (470, 580, 440, 300), -5, 2, None),
              ("avion_11.jpg", (1130, 560, 360, 240), 6, 3, (255, 120, 80)), ("avion_03.jpg", (330, 120, 400, 260), -4, 4, None), ("avion_06.jpg", (700, 130, 380, 250), 3, 5, None), ("avion_02.jpg", (1190, 120, 300, 200), -5, 6, None)]
    for n, (cx, cy, w, h), rot, sd, col in piezas:
        f = cargar(n); f = oscura(f, 0.85, col) if col else oscura(f.convert("L").convert("RGB"), 0.8)
        im = papel_rasgado(im, f, (cx - w // 2, cy - h // 2, w, h), seed=sd, rot=rot, borde=9)
    im = vineta(im, 0.6)
    return Image.fromarray((np.asarray(im).astype(np.float32) * 0.95).astype(np.uint8))


def base():
    im = fondo_collage()
    mug = Image.open(A("mugshot_original.png")).convert("RGB").crop((0, 8, 267, 256)).convert("L").convert("RGB")
    im = expediente(im, (1010, 190), (420, 330), 4, mug)
    return im


def con_cara(im):
    cara = colorizar(rostro(740))
    return con_brillo(im, cara, (10, H - cara.height + 25), (200, 25, 25), radio=22, intens=0.55, borde=11, borde_color=(235, 230, 215))


def va():
    return grano(vineta(con_cara(base()), 0.45), 5)


def vb():
    im = base(); im = con_cara(im)
    im = texto(im, (1255, 395), "AMADO", ajustar("AMADO", 520, 160), BLANCO, trazo=9, ancla="ra")
    im = texto(im, (1255, 525), "CARRILLO", ajustar("CARRILLO", 560, 130), AMARILLO, trazo=9, ancla="ra")
    im = cinta(im, (1010, 665), "LA MUERTE MÁS SOSPECHOSA", sz=34, rot=-1.5)
    im = sangre(im, [(1180, 0, 1280, 40), (0, 640, 60, 700)], n=10, seed=2)
    return grano(vineta(im, 0.45), 5)


def main(out):
    os.makedirs(out, exist_ok=True)
    for n, f in (("miniatura_V4_documental_sin_texto", va), ("miniatura_V5_documental_con_texto", vb)):
        r = os.path.join(out, n + ".jpg"); f().save(r, quality=90, optimize=True); print(r, os.path.getsize(r) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida"))
