#!/usr/bin/env python3
"""Amado Carrillo Fuentes en el mismo estilo que la miniatura de Ovidio con banderas: dos fotos grandes a pantalla completa
fundidas en el centro, rostro grande (en color estimado), nombre con sello de verificado arriba a la izquierda y marco metalico.
Uso: python3 miniatura_amado_estilo.py [carpeta_salida]"""
import os, sys
import numpy as np
from PIL import Image
from crear_miniaturas import *
from miniatura_documental import colorizar
from miniatura_banderas import mitad, insignia, marco


def miniatura(izq, der, cajas, k=(1.0, 1.0), rgb=((1.0, 1.0, 1.04), (1.04, 1.0, 0.96))):
    a = mitad(izq, cajas[0], 760, H, k[0], rgb[0]); b = mitad(der, cajas[1], 760, H, k[1], rgb[1])
    im = Image.new("RGB", (W, H))
    ramp = np.clip((np.linspace(0, 1, 760) - 0.55) / 0.45, 0, 1); ramp = 1 - ramp * ramp * (3 - 2 * ramp)
    m = Image.fromarray((np.tile(ramp, (H, 1)) * 255).astype(np.uint8))
    im.paste(b, (W - 760, 0)); im.paste(a, (0, 0), m)
    im = vineta(im, 0.5)
    cara = colorizar(rostro(650))
    im = con_brillo(im, cara, ((W - cara.width) // 2 + 50, H - cara.height + 18), (0, 0, 0), radio=26, intens=0.85, borde=0)
    sz = 80; nombre = "Amado Carrillo"
    im = texto(im, (36, 16), nombre, sz, BLANCO, trazo=0, sombra=True, ancla="la")
    im = insignia(im, (36 + ancho_texto(nombre, sz, 0) + int(sz * 0.55), 16 + int(sz * 0.64)), int(sz * 0.39))
    return marco(grano(im, 4))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida")
    v = {"A": miniatura("avion_11.jpg", "bg_aerea_mexico.jpg", [(0.20, 0.0, 0.85, 1.0), (0.0, 0.0, 0.8, 0.75)], k=(1.25, 1.1)),
         "B": miniatura("bg_727_noche.jpg", "bg_727_niebla.jpg", [(0.0, 0.1, 0.8, 0.95), (0.25, 0.1, 0.95, 0.95)], k=(1.1, 1.1))}
    for n, im in v.items():
        r = os.path.join(out, f"miniatura_AMADO_estilo_{n}.jpg"); im.save(r, quality=92, optimize=True); print(r)
