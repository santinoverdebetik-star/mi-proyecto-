#!/usr/bin/env python3
"""Reemplaza el texto 'NUNCA / LO MOSTRARON' de la miniatura de referencia (assets/ref_pago_original.png) por
'PAGÓ EL' (blanco texturizado) y 'PRECIO' (rojo carmesí con brillo). Borra el texto viejo reconstruyendo el fondo oscuro (inpainting).
Uso: python3 cambiar_texto_pago.py [salida.jpg] [linea1] [linea2]"""
import os, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
ZONA = (20, 425, 1128, 905)                       # x0, y0, x1, y1 donde esta el texto viejo (no toca el rostro)


def borrar_texto(bgr):
    """borra el texto viejo (letras + contorno negro + sombra) con inpainting sobre una mascara muy dilatada y grano"""
    x0, y0, x1, y1 = ZONA
    reg = bgr[y0:y1, x0:x1]
    b, g, r = [reg[..., i].astype(np.int32) for i in range(3)]
    lum = (b + g + r) // 3
    m = ((lum > 120) | ((r > 120) & (g < 95) & (b < 95)) | ((r > 70) & (r - g > 45))).astype(np.uint8) * 255
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61)))          # cubre el contorno negro y la sombra
    full = np.zeros(bgr.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
    full[:y0 + 14] = 0                                                                  # no tocar la foto de arriba
    chico = cv2.resize(bgr, None, fx=0.4, fy=0.4); mchico = cv2.resize(full, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_NEAREST)
    rell = cv2.inpaint(chico, mchico, 12, cv2.INPAINT_TELEA)
    rell = cv2.GaussianBlur(rell, (0, 0), 4)
    grande = cv2.resize(rell, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_CUBIC)
    sel = cv2.GaussianBlur(full.astype(np.float32) / 255.0, (0, 0), 10)
    ruido = np.random.default_rng(2).normal(0, 3.2, bgr.shape[:2])[..., None]
    out = bgr.astype(np.float32) * (1 - sel[..., None]) + (grande + ruido) * sel[..., None]
    out = np.clip(out, 0, 255)
    # resto del contorno viejo justo bajo la foto: se funde con la ultima fila de la foto hacia el fondo
    fila = cv2.GaussianBlur(out[430:437].mean(axis=0, keepdims=True), (0, 0), sigmaX=18)[0]
    xs = np.arange(out.shape[1]); hor = np.clip(np.minimum(xs - 110, 1040 - xs) / 40.0, 0, 1)
    for y in range(438, 488):
        a = ((y - 438) / 50.0) ** 1.3
        mezcla = fila * (1 - a) + out[y] * a
        out[y] = out[y] * (1 - hor[:, None]) + mezcla * hor[:, None]
    out = out.astype(np.uint8)
    # resto vertical rojo de la ultima letra del texto viejo, junto al hombro
    r = np.zeros(out.shape[:2], np.uint8); r[640:725, 1104:1128] = 255
    out = cv2.inpaint(out, r, 6, cv2.INPAINT_TELEA)
    return out


def mascara_texto(s, alto_mayus, ancho_max=None, estrecho=0.74):
    """mascara L del texto en tipografia 'condensada' (Inter Black comprimida en horizontal)"""
    f = ImageFont.truetype(FONT, 600)
    bb = f.getbbox(s); w, h = bb[2] - bb[0], bb[3] - bb[1]
    m = Image.new("L", (w + 40, h + 40), 0); ImageDraw.Draw(m).text((20 - bb[0], 20 - bb[1]), s, font=f, fill=255)
    cap = f.getbbox("H")[3] - f.getbbox("H")[1]
    k = alto_mayus / cap
    nw = int(m.width * k * estrecho); nh = int(m.height * k * 1.08)
    if ancho_max and nw > ancho_max:
        e = ancho_max / nw; nw = int(nw * e)
    return m.resize((nw, nh), Image.LANCZOS)


def arriba(m, cap):
    """filas vacias sobre las mayusculas dentro de la mascara (margen + acento)"""
    a = (np.asarray(m) > 128).sum(axis=1); filas = np.nonzero(a > 0.3 * a.max())[0]            # ignora el acento (poca tinta)
    return int(filas[0]) if len(filas) else 0


def blanco_piedra(m):
    """relleno blanco con manchas oscuras de desgaste (estilo piedra/granulado)"""
    w, h = m.size; r = np.random.default_rng(7)
    base = np.full((h, w), 245, np.float32)
    gran = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 14) * 18
    base += gran
    motas = cv2.GaussianBlur(r.random((h, w)).astype(np.float32), (0, 0), 1.6)
    oscuro = (motas < np.percentile(motas, 5.5)).astype(np.float32)
    oscuro = cv2.GaussianBlur(oscuro, (0, 0), 0.9)
    base = base * (1 - 0.92 * oscuro) + 20 * 0.92 * oscuro
    rayas = cv2.GaussianBlur((r.random((h, w)) < 0.0008).astype(np.float32), (0, 0), sigmaX=9, sigmaY=0.8) * 400
    base -= rayas
    base = np.clip(base, 0, 255).astype(np.uint8)
    rgb = Image.fromarray(np.dstack([base] * 3), "RGB").convert("RGBA"); rgb.putalpha(m)
    return rgb


def rojo_carmesi(m):
    w, h = m.size
    g = np.linspace(0, 1, h)[:, None]
    r_ = (255 - 70 * g) * np.ones((h, w)); g_ = (22 - 22 * g) * np.ones((h, w)); b_ = (18 - 14 * g) * np.ones((h, w))
    ruido = cv2.GaussianBlur(np.random.default_rng(3).normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.0) * 10
    arr = np.clip(np.dstack([r_ + ruido, g_, b_]), 0, 255).astype(np.uint8)
    rgb = Image.fromarray(arr, "RGB").convert("RGBA"); rgb.putalpha(m)
    return rgb


def pegar(base, capa, xy, sombra=True, brillo=None):
    b = base.convert("RGBA")
    if brillo:
        al = capa.split()[3]; gl = Image.new("RGBA", capa.size, brillo + (255,)); gl.putalpha(al.filter(ImageFilter.GaussianBlur(22)).point(lambda v: min(255, int(v * 1.1))))
        b.alpha_composite(gl, xy)
    if sombra:
        sh = Image.new("RGBA", capa.size, (0, 0, 0, 255)); sh.putalpha(capa.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.85)))
        b.alpha_composite(sh, (xy[0] + 6, xy[1] + 9))
    b.alpha_composite(capa, xy)
    return b.convert("RGB")


def linea_brillo(base, x0, x1, y):
    b = base.convert("RGBA"); S = Image.new("RGBA", b.size, (0, 0, 0, 0)); d = ImageDraw.Draw(S)
    d.rounded_rectangle((x0, y - 5, x1, y + 5), 5, fill=(255, 60, 40, 255))
    halo = S.filter(ImageFilter.GaussianBlur(14)); b.alpha_composite(halo); b.alpha_composite(halo); b.alpha_composite(S)
    return b.convert("RGB")


def main(salida, l1="PAGÓ EL", l2="PRECIO"):
    bgr = cv2.imread(os.path.join(AQUI, "assets", "ref_pago_original.png"))
    limpio = borrar_texto(bgr)
    im = Image.fromarray(cv2.cvtColor(limpio, cv2.COLOR_BGR2RGB))
    CAP = 176
    m1 = mascara_texto(l1, CAP, ancho_max=1000); c1 = blanco_piedra(m1)
    m2 = mascara_texto(l2, CAP, ancho_max=1040); c2 = rojo_carmesi(m2)
    cx = 565
    top1, top2 = 480, 692                                           # y de la parte superior de las mayusculas
    im = pegar(im, c1, (cx - c1.width // 2, top1 - arriba(m1, CAP)))
    im = pegar(im, c2, (cx - c2.width // 2, top2 - arriba(m2, CAP)), brillo=(200, 10, 10))
    im = linea_brillo(im, 80, 1000, top2 + CAP + 42)
    im.save(salida, quality=93, optimize=True); print(salida)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else os.path.join(AQUI, "salida", "miniatura_PAGO_PRECIO.jpg"), *(a[1:3]))
