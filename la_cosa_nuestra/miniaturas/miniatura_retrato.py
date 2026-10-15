#!/usr/bin/env python3
"""Miniatura estilo 'retrato documental': rostro grande recortado al centro, dos fotos laterales oscuras que se funden con el fondo,
gradacion de color fria y una etiqueta con el nombre. Uso: python3 miniatura_retrato.py [carpeta_salida]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from miniatura_documental import colorizar
from miniatura_ovidio import cara_ovidio
from crear_miniaturas import *
from miniatura_documental import realzar


def graduar(im, k=0.6, rgb=(0.86, 1.0, 1.06)):
    a = np.asarray(realzar(im, 1.0, 0.85, 1.15)).astype(np.float32) * k * np.array(rgb, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def panel(base, nombre, lado, ancho=760, k=0.62, desenfoque=1.6):
    f = graduar(cover(cargar(nombre), ancho, H), k).filter(ImageFilter.GaussianBlur(desenfoque))
    x = np.linspace(0, 1, ancho); r = np.clip((x - 0.28) / 0.72, 0, 1); r = 1 - r * r * (3 - 2 * r)      # 1 -> 0 (suave)
    m = np.tile(r, (H, 1))
    if lado == "der": m = m[:, ::-1]
    m = Image.fromarray((m * 255).astype(np.uint8))
    base.paste(f, (0 if lado == "izq" else W - ancho, 0), m)
    return base


def etiqueta(im, xy, s, sz=46):
    f = font(sz); bb = f.getbbox(s); w, h = bb[2] - bb[0] + 56, bb[3] - bb[1] + 30
    capa = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((26, 28, 26 + w, 28 + h), 14, fill=(0, 0, 0, 160)); capa = capa.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(capa)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 14, fill=(14, 14, 14, 235), outline=(230, 30, 30, 255), width=4)
    d.text((20 + 28 - bb[0], 20 + 15 - bb[1]), s, font=f, fill=(255, 255, 255, 255))
    b = im.convert("RGBA"); b.alpha_composite(capa, (int(xy[0]), int(xy[1]))); return b.convert("RGB")


def armar(fondo, izq, der, cara, nombre, altura_cara=730, tag=None):
    im = graduar(cover(cargar(fondo), W, H), 0.5)
    im = panel(im, izq, "izq"); im = panel(im, der, "der")
    im = vineta(im, 0.55)
    x = (W - cara.width) // 2
    im = con_brillo(im, cara, (x, H - cara.height + 20), (0, 0, 0), radio=26, intens=1.0, borde=0)
    if tag: im = etiqueta(im, (tag[0], tag[1]), nombre)
    return grano(im, 5)


def main(out):
    os.makedirs(out, exist_ok=True)
    ov = cara_ovidio(660)
    tareas = {
        "miniatura_RETRATO_Ovidio_A": armar("bg_capitolio_noche.jpg", "bg_blindado_mx.jpg", "bg_justicia.jpg", ov, "OvidioGuzmán", tag=(60, 560)),
        "miniatura_RETRATO_Ovidio_B": armar("bg_muro.jpg", "bg_vehiculo_mx.jpg", "bg_capitolio.jpg", ov, "OvidioGuzmán", tag=(60, 560)),
        "miniatura_RETRATO_Amado": armar("bg_727_niebla.jpg", "bg_727_noche.jpg", "bg_aerea_mexico.jpg", colorizar(rostro(680)), "AmadoCarrillo", tag=(60, 560)),
    }
    for n, im in tareas.items():
        r = os.path.join(out, n + ".jpg"); im.save(r, quality=90, optimize=True); print(r)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "salida"))
