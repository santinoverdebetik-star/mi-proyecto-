#!/usr/bin/env python3
"""Miniatura 'Ovidio: hizo rendirse a todo un gobierno... y termino rendiendose ante EE.UU.' (sin texto, collage documental).
Mitad 'gobierno mexicano' (ejercito, Palacio Nacional) y mitad 'EE.UU.' (Capitolio, Departamento de Justicia)."""
import os, sys
import numpy as np
from PIL import Image
from miniatura_documental import *

CONFIGS = {
    "A": ("bg_capitolio.jpg", [("bg_blindado_mx.jpg", (900, 185, 800, 390), -2, 4), ("bg_justicia.jpg", (700, 545, 640, 350), 3, 3),
                               ("bg_edificio_mx.jpg", (1110, 545, 540, 350), -3, 5)]),
    "B": ("bg_capitolio_noche.jpg", [("bg_aeropuerto_culiacan.jpg", (900, 185, 800, 390), -2, 4), ("bg_vehiculo_mx.jpg", (700, 545, 640, 350), 3, 3),
                                     ("bg_muro.jpg", (1110, 545, 540, 350), -3, 5)]),
}


def cara_ovidio(altura):
    im = Image.open(A("ovidio_recorte.png")).convert("RGBA")
    ys, xs = np.nonzero(np.asarray(im.split()[3]) > 20)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    rgb = realzar(im.convert("RGB"), 1.0, 1.1, 1.12); rgb.putalpha(im.split()[3])
    return rgb.resize((int(rgb.width * altura / rgb.height), altura), Image.LANCZOS)


def miniatura(var):
    fondo, piezas = CONFIGS[var]
    im = realzar(cover(cargar(fondo), W, H), 0.8, 1.0, 1.05)
    for nom, (cx, cy, w, h), rot, sd in piezas:
        im = papel_rasgado(im, realzar(cargar(nom)), (cx - w // 2, cy - h // 2, w, h), seed=sd, rot=rot, borde=8)
    im = expediente(vineta(im, 0.3), (1090, 175), (350, 280), 5, None)
    cara = cara_ovidio(700)
    im = con_brillo(im, cara, (15, H - cara.height + 30), (200, 25, 25), radio=22, intens=0.55, borde=11, borde_color=(235, 230, 215))
    return grano(vineta(im, 0.3), 4)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
    for v in CONFIGS:
        r = os.path.join(out, f"miniatura_OVIDIO_sin_texto_{v}.jpg"); miniatura(v).save(r, quality=90, optimize=True); print(r)
