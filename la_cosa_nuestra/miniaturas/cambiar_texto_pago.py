#!/usr/bin/env python3
"""Reemplaza el texto 'NUNCA / LO MOSTRARON' de la miniatura de referencia (assets/ref_pago_original.png) por otro texto con el MISMO formato:
linea 1 en blanco desgastado con contorno negro grueso, linea 2 en rojo con contorno negro y brillo, y la linea roja brillante debajo.
El texto viejo se borra con negro nitido (sin difuminar el fondo).
Uso: python3 cambiar_texto_pago.py [salida.jpg] [linea1] [linea2]"""
import os, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
ZONA = (20, 440, 1128, 905)                       # x0, y0, x1, y1 donde esta el texto viejo (no toca el rostro)


def borrar_texto(bgr):
    """tapa solo las letras viejas (con su contorno) con negro y grano; el resto de la imagen queda tal cual, sin desenfoque"""
    x0, y0, x1, y1 = ZONA
    reg = bgr[y0:y1, x0:x1].astype(np.int32)
    b, g, r = reg[..., 0], reg[..., 1], reg[..., 2]
    lum = (b + g + r) // 3
    blanco = (lum > 150) & (np.abs(r - b) < 40)                                 # letras blancas
    rojo = (r > 110) & (g < 100) & (b < 100)                                    # letras rojas y brillo
    m = (blanco | rojo).astype(np.uint8) * 255
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    m[(xx + x0 > 1030) & (yy + y0 < 650)] = 0                                    # no tocar la oreja / cuello del rostro
    m[(xx + x0 > 1030) & (yy + y0 > 640)] = 0                                    # el hombro se trata aparte (abajo)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))   # cubre el contorno negro y la sombra
    full = np.zeros(bgr.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
    sel = cv2.GaussianBlur(full.astype(np.float32) / 255.0, (0, 0), 2.5)
    ruido = np.clip(np.random.default_rng(2).normal(4, 2.2, bgr.shape[:2]), 0, 14)[..., None]
    out = bgr.astype(np.float32) * (1 - sel[..., None]) + np.repeat(ruido, 3, 2) * sel[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    # zona del hombro (x > 1030): se restaura el original y solo se quita el resto rojo/negro de la ultima letra con inpainting local
    X = 1030; Y0, Y1 = 640, 860
    sub = bgr[Y0:Y1, X:1130].copy(); b_, g_, r_ = [sub[..., i].astype(np.int32) for i in range(3)]
    resto = ((r_ > 90) & (r_ - g_ > 45) & (r_ - b_ > 45)).astype(np.uint8) * 255
    resto = cv2.dilate(resto, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
    out[Y0:Y1, X:1130] = cv2.inpaint(sub, resto, 7, cv2.INPAINT_TELEA)
    return out


def mascara_texto(s, cap, ancho):
    """mascara L del texto en tipografia pesada: alto de mayusculas = cap, ancho total = ancho"""
    f = ImageFont.truetype(FONT, 600)
    bb = f.getbbox(s); w, h = bb[2] - bb[0], bb[3] - bb[1]
    m = Image.new("L", (w + 40, h + 40), 0); ImageDraw.Draw(m).text((20 - bb[0], 20 - bb[1]), s, font=f, fill=255)
    capb = f.getbbox("H"); capb = capb[3] - capb[1]
    k = cap / capb
    nh = int(m.height * k)
    nw = int((m.width - 40) * ancho / (m.width - 40) * 1.0) if False else int(ancho * (m.width / (m.width - 40)))
    return m.resize((nw, nh), Image.LANCZOS)


def arriba(m):
    """fila donde empiezan las mayusculas (ignora acentos)"""
    a = (np.asarray(m) > 128).sum(axis=1); filas = np.nonzero(a > 0.3 * a.max())[0]
    return int(filas[0]) if len(filas) else 0


def contorno(m, grosor):
    """mascara agrandada para el contorno negro"""
    return m.filter(ImageFilter.MaxFilter(2 * grosor + 1)).filter(ImageFilter.GaussianBlur(1.2))


def capa_blanca(m):
    """letras blancas con desgaste gris claro y rayones, contorno negro grueso"""
    w, h = m.size; r = np.random.default_rng(7)
    base = np.full((h, w), 247, np.float32)
    gran = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 9) * 16
    fino = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.3) * 16
    base += gran + fino
    motas = cv2.GaussianBlur(r.random((h, w)).astype(np.float32), (0, 0), 1.2)
    oscuro = cv2.GaussianBlur((motas < np.percentile(motas, 2.2)).astype(np.float32), (0, 0), 0.8)
    base = base * (1 - 0.55 * oscuro) + 60 * 0.55 * oscuro
    base = np.clip(base, 0, 255).astype(np.uint8)
    cara = Image.fromarray(np.dstack([base] * 3), "RGB").convert("RGBA"); cara.putalpha(m)
    return cara


def capa_roja(m):
    w, h = m.size
    t = np.linspace(0, 1, h)[:, None]
    R = (255 - 35 * t) * np.ones((h, w)); G = (28 - 28 * t) * np.ones((h, w)); B = (14 - 14 * t) * np.ones((h, w))
    ruido = cv2.GaussianBlur(np.random.default_rng(3).normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.0) * 8
    arr = np.clip(np.dstack([R + ruido, G, B]), 0, 255).astype(np.uint8)
    cara = Image.fromarray(arr, "RGB").convert("RGBA"); cara.putalpha(m)
    return cara


def pegar(base, cara, m, xy, grosor, brillo=None, gl=24):
    """pega letras con contorno negro grueso, sombra y (opcional) brillo de color; usa margen para que no se corte el halo"""
    P = 70
    mp = Image.new("L", (m.width + 2 * P, m.height + 2 * P), 0); mp.paste(m, (P, P))
    cp = Image.new("RGBA", mp.size, (0, 0, 0, 0)); cp.paste(cara, (P, P))
    b = base.convert("RGBA"); x, y = xy[0] - P, xy[1] - P
    cnt = contorno(mp, grosor)
    if brillo:
        halo = Image.new("RGBA", mp.size, brillo + (255,)); halo.putalpha(cnt.filter(ImageFilter.GaussianBlur(gl)).point(lambda v: min(255, int(v * 1.4))))
        b.alpha_composite(halo, (x, y)); b.alpha_composite(halo, (x, y))
    sh = Image.new("RGBA", mp.size, (0, 0, 0, 255)); sh.putalpha(cnt.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.9)))
    b.alpha_composite(sh, (x + 5, y + 9))
    neg = Image.new("RGBA", mp.size, (0, 0, 0, 255)); neg.putalpha(cnt)
    b.alpha_composite(neg, (x, y)); b.alpha_composite(cp, (x, y))
    return b.convert("RGB")


def linea_brillo(base, cx, ancho, y):
    """linea roja/naranja brillante, mas gruesa en el centro, con halo"""
    b = base.convert("RGBA"); S = 3
    capa = Image.new("RGBA", (b.width * S, 80 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for i in range(0, ancho * S, 2):
        t = i / (ancho * S); grosor = (1 - abs(2 * t - 1) ** 2.2) * 6 * S + 0.8 * S
        col = (255, int(60 + 120 * (1 - abs(2 * t - 1))), int(30 + 40 * (1 - abs(2 * t - 1))), 255)
        d.line([(cx * S - ancho * S / 2 + i, 40 * S - grosor / 2), (cx * S - ancho * S / 2 + i, 40 * S + grosor / 2)], fill=col, width=3)
    capa = capa.resize((b.width, 80), Image.LANCZOS)
    halo = capa.filter(ImageFilter.GaussianBlur(10)); b.alpha_composite(halo, (0, y - 40)); b.alpha_composite(halo, (0, y - 40)); b.alpha_composite(capa, (0, y - 40))
    return b.convert("RGB")


def main(salida, l1="PAGÓ EL", l2="PRECIO"):
    bgr = cv2.imread(os.path.join(AQUI, "assets", "ref_pago_original.png"))
    im = Image.fromarray(cv2.cvtColor(borrar_texto(bgr), cv2.COLOR_BGR2RGB))
    CAP = 182
    m1 = mascara_texto(l1, CAP, 850); m2 = mascara_texto(l2, CAP, 930)
    cx = 565; top1, top2 = 462, 668
    im = pegar(im, capa_blanca(m1), m1, (cx - m1.width // 2, top1 - arriba(m1)), grosor=7)
    im = pegar(im, capa_roja(m2), m2, (cx - m2.width // 2, top2 - arriba(m2)), grosor=6, brillo=(255, 20, 10), gl=22)
    im = linea_brillo(im, cx, 960, 880)
    im.save(salida, quality=93, optimize=True); print(salida)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else os.path.join(AQUI, "salida", "miniatura_PAGO_PRECIO.jpg"), *(a[1:3]))
