#!/usr/bin/env python3
"""Miniaturas 1280x720 para 'El Señor de los Cielos' (Amado Carrillo Fuentes). Diseño propio inspirado en el estilo de
las miniaturas de referencia (rostro recortado con brillo rojo, número/texto enorme, círculo rojo, papel rasgado, sangre).
Uso: python3 crear_miniaturas.py [carpeta_salida]"""
import math, os, random, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(AQUI, "assets", n)
W, H = 1280, 720
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
ROJO = (214, 24, 24); AMARILLO = (255, 214, 10); BLANCO = (255, 255, 255)


def font(sz): return ImageFont.truetype(FONT, sz)


def cover(im, w, h, cx=0.5, cy=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x = int((im.width - w) * cx); y = int((im.height - h) * cy)
    return im.crop((x, y, x + w, y + h))


def cargar(n): return Image.open(A(n)).convert("RGB")


def vineta(im, fuerza=0.75):
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.sqrt(((xx - a.shape[1] / 2) / (a.shape[1] / 2)) ** 2 + ((yy - a.shape[0] / 2) / (a.shape[0] / 2)) ** 2)
    m = 1 - fuerza * np.clip(d - 0.45, 0, 1) ** 1.4
    return Image.fromarray(np.clip(a * m[..., None], 0, 255).astype(np.uint8))


def grano(im, s=7, seed=3):
    a = np.asarray(im).astype(np.float32)
    r = np.random.default_rng(seed).normal(0, s, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + r, 0, 255).astype(np.uint8))


def tinte(im, color, k):
    """mezcla multiplicativa con un color (gradacion de color)"""
    a = np.asarray(im).astype(np.float32) / 255
    c = np.array(color, np.float32) / 255
    return Image.fromarray(np.clip(a * (1 - k + k * c * 1.6) * 255, 0, 255).astype(np.uint8))


def rostro(altura):
    """recorte del rostro con bordes limpios (quita los restos de las rejillas del fondo)"""
    im = Image.open(A("cara_recorte.png")).convert("RGBA")
    al = np.asarray(im.split()[3])
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    al = cv2.morphologyEx(al, cv2.MORPH_OPEN, k)
    n, lab, st, _ = cv2.connectedComponentsWithStats((al > 128).astype(np.uint8))
    if n > 1:
        al = np.where(lab == 1 + np.argmax(st[1:, 4]), al, 0).astype(np.uint8)
    al = cv2.GaussianBlur(al, (0, 0), 2.2)
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    g = rgb.mean(axis=2, keepdims=True)
    g = np.clip((g - 20) * 1.18, 0, 255)                          # mas contraste, blanco y negro duro
    out = Image.fromarray(np.dstack([np.repeat(g, 3, 2), al[..., None]]).astype(np.uint8), "RGBA")
    ys, xs = np.nonzero(al > 20)
    out = out.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return out.resize((int(out.width * altura / out.height), altura), Image.LANCZOS)


def con_brillo(base, cara, pos, color=ROJO, radio=26, intens=1.0, borde=0, borde_color=BLANCO):
    """pega 'cara' (RGBA) en 'base' con halo de color y, opcionalmente, contorno tipo sticker"""
    x, y = pos
    al = cara.split()[3]
    capa = Image.new("L", base.size, 0); capa.paste(al, (x, y))
    base = base.convert("RGBA")
    halo = capa.filter(ImageFilter.MaxFilter(2 * (radio // 3) + 1)).filter(ImageFilter.GaussianBlur(radio))
    halo = halo.point(lambda v: min(255, int(v * 1.6 * intens)))
    base.alpha_composite(Image.composite(Image.new("RGBA", base.size, color + (255,)), Image.new("RGBA", base.size, (0, 0, 0, 0)), halo))
    if borde:
        cnt = capa.filter(ImageFilter.MaxFilter(2 * borde + 1)).filter(ImageFilter.GaussianBlur(1.2))
        sombra = cnt.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6))
        base.alpha_composite(Image.composite(Image.new("RGBA", base.size, (0, 0, 0, 255)), Image.new("RGBA", base.size, (0, 0, 0, 0)), sombra), (8, 10))
        base.alpha_composite(Image.composite(Image.new("RGBA", base.size, borde_color + (255,)), Image.new("RGBA", base.size, (0, 0, 0, 0)), cnt))
    base.alpha_composite(cara, (x, y))
    return base.convert("RGB")


def texto(im, xy, s, sz, color=BLANCO, trazo=8, trazo_color=(0, 0, 0), ancla="la", sombra=True, rot=0, espaciado=0):
    """texto grande con contorno y sombra; rot gira el texto alrededor de su centro"""
    f = font(sz)
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    if sombra:
        d.text((xy[0] + 6, xy[1] + 8), s, font=f, fill=(0, 0, 0, 200), anchor=ancla, stroke_width=trazo, stroke_fill=(0, 0, 0, 200))
        capa = capa.filter(ImageFilter.GaussianBlur(4)); d = ImageDraw.Draw(capa)
    d.text(xy, s, font=f, fill=color + (255,), anchor=ancla, stroke_width=trazo, stroke_fill=trazo_color + (255,))
    if rot:
        capa = capa.rotate(rot, center=xy, resample=Image.BICUBIC)
    base = im.convert("RGBA"); base.alpha_composite(capa)
    return base.convert("RGB")


def ancho_texto(s, sz, trazo=8):
    b = font(sz).getbbox(s, stroke_width=trazo)
    return b[2] - b[0]


def ajustar(s, ancho, sz0=300, trazo_k=0.06):
    sz = sz0
    while sz > 20 and ancho_texto(s, sz, int(sz * trazo_k)) > ancho: sz -= 4
    return sz


def sangre(im, regiones, n=40, seed=5, color=(150, 8, 10)):
    """salpicaduras y goteos rojos en las zonas indicadas [(x0,y0,x1,y1), ...]"""
    r = random.Random(seed)
    S = 2; capa = Image.new("RGBA", (im.width * S, im.height * S), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for (x0, y0, x1, y1) in regiones:
        for _ in range(n):
            cx, cy = r.uniform(x0, x1) * S, r.uniform(y0, y1) * S; rad = r.choice([2, 3, 4, 6, 9, 14]) * S / 2
            d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color + (235,))
            if r.random() < 0.3:                                    # goteo
                largo = r.uniform(18, 70) * S; ancho = rad * 0.7
                d.rounded_rectangle((cx - ancho / 2, cy, cx + ancho / 2, cy + largo), radius=ancho / 2, fill=color + (235,))
                d.ellipse((cx - ancho * 0.8, cy + largo - ancho * 0.8, cx + ancho * 0.8, cy + largo + ancho * 0.8), fill=color + (235,))
            for _ in range(r.randint(0, 3)):                        # gotitas alrededor
                a = r.uniform(0, 6.28); q = rad * r.uniform(1.5, 3.5); rr = r.uniform(1, 3) * S
                d.ellipse((cx + math.cos(a) * q - rr, cy + math.sin(a) * q - rr, cx + math.cos(a) * q + rr, cy + math.sin(a) * q + rr), fill=color + (235,))
    capa = capa.resize(im.size, Image.LANCZOS)
    base = im.convert("RGBA"); base.alpha_composite(capa)
    return base.convert("RGB")


def rasgado(w, h, seed=1, amp=9, paso=14):
    """mascara L de un trozo de papel con los bordes rasgados"""
    r = random.Random(seed); pts = []
    for x in range(0, w, paso): pts.append((x, r.uniform(-amp, amp)))
    for y in range(0, h, paso): pts.append((w + r.uniform(-amp, amp), y))
    for x in range(w, 0, -paso): pts.append((x, h + r.uniform(-amp, amp)))
    for y in range(h, 0, -paso): pts.append((r.uniform(-amp, amp), y))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x + 0, y + 0) for x, y in pts], fill=255)
    return m


def papel_rasgado(base, foto, caja, seed=1, rot=0, borde=10):
    """pega 'foto' (RGB) con borde de papel blanco rasgado y sombra en 'caja' = (x, y, w, h)"""
    x, y, w, h = caja
    foto = cover(foto, w, h)
    mf = rasgado(w, h, seed, amp=6, paso=12)
    W2, H2 = w + 2 * borde, h + 2 * borde
    mp = rasgado(W2, H2, seed + 7, amp=8, paso=10)
    papel = Image.new("RGBA", (W2, H2), (238, 232, 218, 255)); papel.putalpha(mp)
    papel.paste(foto, (borde, borde), mf)
    sh = Image.new("RGBA", (W2 + 60, H2 + 60), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (W2, H2), (0, 0, 0, 190)), (30, 30), mp)
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    pieza = Image.new("RGBA", (W2 + 60, H2 + 60), (0, 0, 0, 0)); pieza.alpha_composite(sh, (10, 12)); pieza.alpha_composite(papel, (30, 30))
    if rot: pieza = pieza.rotate(rot, resample=Image.BICUBIC, expand=True)
    b = base.convert("RGBA"); cx, cy = x + w // 2, y + h // 2
    b.alpha_composite(pieza, (cx - pieza.width // 2, cy - pieza.height // 2))
    return b.convert("RGB")


def circulo_flecha(im, centro, rx, ry, flecha_desde=None, grosor=9, rot=-12):
    S = 3; capa = Image.new("RGBA", (im.width * S, im.height * S), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    cx, cy = centro[0] * S, centro[1] * S
    pts = []
    for i in range(0, 400):
        a = i / 400 * 2 * math.pi * 1.06 + 0.4
        k = 1 + 0.015 * math.sin(a * 5)
        x, y = rx * S * k * math.cos(a), ry * S * k * math.sin(a)
        c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts.append((cx + x * c - y * s_, cy + x * s_ + y * c))
    d.line(pts, fill=(235, 25, 25, 255), width=grosor * S, joint="curve")
    if flecha_desde:
        fx, fy = flecha_desde[0] * S, flecha_desde[1] * S
        ang = math.atan2(cy - fy, cx - fx); fin = (cx - math.cos(ang) * (rx * S * 1.12), cy - math.sin(ang) * (ry * S * 1.12))
        d.line([(fx, fy), fin], fill=(235, 25, 25, 255), width=grosor * S)
        for da in (2.6, -2.6):
            d.line([fin, (fin[0] + math.cos(ang + da) * 55 * S, fin[1] + math.sin(ang + da) * 55 * S)], fill=(235, 25, 25, 255), width=grosor * S)
    capa = capa.resize(im.size, Image.LANCZOS)
    sh = capa.filter(ImageFilter.GaussianBlur(5))
    b = im.convert("RGBA"); b.alpha_composite(Image.new("RGBA", im.size, (0, 0, 0, 0)))
    b.alpha_composite(capa); return b.convert("RGB")


def cinta(im, xy, s, sz=44, bg=ROJO, fg=BLANCO, rot=-3, pad=(26, 12)):
    f = font(sz); bb = f.getbbox(s)
    w, h = bb[2] - bb[0] + 2 * pad[0], bb[3] - bb[1] + 2 * pad[1]
    capa = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    d.rectangle((24, 26, 24 + w, 26 + h), fill=(0, 0, 0, 170)); capa = capa.filter(ImageFilter.GaussianBlur(6)); d = ImageDraw.Draw(capa)
    d.rectangle((20, 20, 20 + w, 20 + h), fill=bg + (255,))
    d.text((20 + pad[0] - bb[0], 20 + pad[1] - bb[1]), s, font=f, fill=fg + (255,))
    capa = capa.rotate(rot, resample=Image.BICUBIC, expand=True)
    b = im.convert("RGBA"); b.alpha_composite(capa, (int(xy[0] - capa.width / 2), int(xy[1] - capa.height / 2))); return b.convert("RGB")


def sello(im, xy, s, sz=70, color=(200, 20, 20), rot=-8):
    f = font(sz); bb = f.getbbox(s); w, h = bb[2] - bb[0] + 50, bb[3] - bb[1] + 36
    capa = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    d.rectangle((10, 10, 10 + w, 10 + h), outline=color + (235,), width=9)
    d.rectangle((22, 22, w - 2, h - 2), outline=color + (235,), width=3)
    d.text((10 + 25 - bb[0], 10 + 18 - bb[1]), s, font=f, fill=color + (235,))
    ruido = np.random.default_rng(4).random((capa.height, capa.width)) < 0.12       # tinta desgastada
    al = np.asarray(capa.split()[3]).copy(); al[ruido] = (al[ruido] * 0.25).astype(np.uint8)
    capa.putalpha(Image.fromarray(al)); capa = capa.rotate(rot, resample=Image.BICUBIC, expand=True)
    b = im.convert("RGBA"); b.alpha_composite(capa, (int(xy[0] - capa.width / 2), int(xy[1] - capa.height / 2))); return b.convert("RGB")


# --------------------------------------------------------------------------------------------- V1
def v1():
    fondo = cover(cargar("avion_11.jpg"), W, H, 0.5, 0.55)
    fondo = tinte(fondo, (255, 90, 40), 0.45)
    a = np.asarray(fondo).astype(np.float32); a = np.clip((a - 10) * 1.55, 0, 255)
    fondo = vineta(Image.fromarray(a.astype(np.uint8)), 0.75)
    fondo = fondo.filter(ImageFilter.GaussianBlur(1.2))
    im = grano(fondo, 6)
    cara = rostro(700)
    im = con_brillo(im, cara, (-30, H - cara.height + 30), ROJO, radio=34, intens=1.1, borde=0)
    # texto derecha
    x = 640
    im = texto(im, (x, 40), "EL SEÑOR", ajustar("EL SEÑOR", 600, 190), BLANCO, trazo=9)
    sz2 = ajustar("DE LOS", 600, 190)
    im = texto(im, (x, 40 + int(sz2 * 0.98)), "DE LOS", sz2, BLANCO, trazo=9)
    sz3 = ajustar("CIELOS", 620, 260)
    im = texto(im, (x, 40 + int(sz2 * 1.9)), "CIELOS", sz3, AMARILLO, trazo=11)
    im = cinta(im, (930, 672), "LA MUERTE MÁS SOSPECHOSA", sz=40, rot=-2)
    im = circulo_flecha(im, (1080, 520), 150, 70, None, rot=-8) if False else im
    im = sangre(im, [(560, 640, 1260, 710), (0, 0, 80, 60)], n=18, seed=11)
    return im


# --------------------------------------------------------------------------------------------- V2
def v2():
    im = Image.new("RGB", (W, H), (14, 6, 6))
    izq = cargar("avion_06.jpg")
    izq = izq.resize((1620, 1080), Image.LANCZOS).crop((620, 60, 1380, 780)).convert("L").convert("RGB")
    a = np.asarray(izq).astype(np.float32); a = np.clip((a - 40) * 1.35, 0, 255); izq = Image.fromarray(a.astype(np.uint8))
    izq = grano(izq, 8)
    im.paste(vineta(izq, 0.5), (0, 0))
    # panel rojo con el rostro
    der = Image.new("RGB", (W, H), (150, 10, 12))
    gr = np.asarray(der).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt(((xx - 1000) / 520.0) ** 2 + ((yy - 330) / 520.0) ** 2)
    gr = gr * (1.35 - 0.9 * np.clip(d, 0, 1))[..., None]
    der = Image.fromarray(np.clip(gr, 0, 255).astype(np.uint8))
    mask = rasgado(W, H, 3, amp=0)
    panel_m = Image.new("L", (W, H), 0)
    r = random.Random(9); pts = [(560, 0)]
    for y in range(0, H + 1, 16): pts.append((560 + 40 * math.sin(y / 70) + r.uniform(-9, 9), y))
    pts += [(W, H), (W, 0)]
    ImageDraw.Draw(panel_m).polygon(pts, fill=255)
    sh = panel_m.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.7))
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), (-14, 0), sh)
    im.paste(der, (0, 0), panel_m)
    cara = rostro(690)
    im = con_brillo(im, cara, (W - cara.width - 10, H - cara.height + 20), (255, 60, 30), radio=30, intens=0.9, borde=0)
    # circulo rojo sobre el avion
    im = circulo_flecha(im, (300, 560), 290, 100, None, grosor=10, rot=-4)
    # numero grande + texto
    im = texto(im, (24, 232), "1997", 235, AMARILLO, trazo=12, ancla="ls")
    im = texto(im, (30, 345), "LA MUERTE MÁS", ajustar("LA MUERTE MÁS", 700, 110), BLANCO, trazo=7, ancla="ls")
    im = texto(im, (30, 460), "SOSPECHOSA", ajustar("SOSPECHOSA", 700, 140), (255, 70, 60), trazo=8, ancla="ls")
    im = sangre(im, [(540, 0, 640, 40), (560, 600, 640, 700)], n=14, seed=21)
    return im


# --------------------------------------------------------------------------------------------- V3
def corcho():
    r = np.random.default_rng(8)
    base = np.zeros((H, W, 3), np.float32) + np.array([62, 98, 150], np.float32)[None, None, ::-1] * 0 + np.array([118, 80, 48], np.float32)
    ruido = cv2.GaussianBlur(r.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2) * 28
    gran = cv2.GaussianBlur(r.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 18) * 40
    pun = (r.random((H, W)) < 0.012).astype(np.float32); pun = cv2.GaussianBlur(pun, (0, 0), 1.6) * 90
    a = np.clip(base + ruido[..., None] + gran[..., None] - pun[..., None], 0, 255).astype(np.uint8)
    return vineta(Image.fromarray(a), 0.9)


def polaroid(base, foto, xy, tam, rot, seed, marco=(240, 236, 226)):
    w, h = tam; borde = 16
    pieza = Image.new("RGBA", (w + 2 * borde, h + 2 * borde + 56), marco + (255,)); pieza.paste(cover(foto, w, h), (borde, borde))
    sh = Image.new("RGBA", (pieza.width + 60, pieza.height + 60), (0, 0, 0, 0)); sh.paste(Image.new("RGBA", pieza.size, (0, 0, 0, 200)), (30, 30))
    sh = sh.filter(ImageFilter.GaussianBlur(12)); can = Image.new("RGBA", sh.size, (0, 0, 0, 0)); can.alpha_composite(sh, (8, 10)); can.alpha_composite(pieza, (30, 30))
    can = can.rotate(rot, resample=Image.BICUBIC, expand=True)
    b = base.convert("RGBA"); b.alpha_composite(can, (int(xy[0] - can.width / 2), int(xy[1] - can.height / 2))); return b.convert("RGB")


def chincheta(im, xy, color=(210, 20, 20)):
    d = ImageDraw.Draw(im, "RGBA"); x, y = xy
    d.ellipse((x - 14, y - 10, x + 18, y + 22), fill=(0, 0, 0, 90))
    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color + (255,)); d.ellipse((x - 8, y - 9, x - 1, y - 2), fill=(255, 255, 255, 170))
    return im


def hilo(im, a, b, color=(200, 18, 18)):
    d = ImageDraw.Draw(im, "RGBA")
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 28
    pts = [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t * t * b[1]) for t in np.linspace(0, 1, 60)]
    d.line([(x + 3, y + 5) for x, y in pts], fill=(0, 0, 0, 110), width=6)
    d.line(pts, fill=color + (255,), width=5); return im


def v3():
    im = corcho()
    # foto del rostro (original, no recortada) como ficha policial
    orig = Image.open(A("mugshot_original.png")).convert("RGB").crop((0, 8, 267, 256)).resize((267 * 2, 240 * 2), Image.LANCZOS)
    orig = orig.convert("L").convert("RGB")
    avion = cargar("avion_03.jpg")
    cielo = cargar("avion_02.jpg").convert("L").convert("RGB")
    p1 = (270, 295)
    im = polaroid(im, orig, p1, (390, 410), -4, 1)
    im = polaroid(im, avion, (700, 262), (360, 235), -3, 3)
    im = polaroid(im, cielo, (1070, 345), (360, 235), 4, 2)
    a1, a2, a3 = (p1[0] + 120, p1[1] - 255), (700 - 100, 262 - 140), (1070 + 60, 345 - 150)
    im = hilo(im, a1, a2); im = hilo(im, (700 + 120, 262 - 140), a3)
    for p in (a1, a2, (700 + 120, 262 - 140), a3): im = chincheta(im, p)
    # sello y titulares
    im = texto(im, (640, 575), "SEÑOR DE LOS CIELOS", ajustar("SEÑOR DE LOS CIELOS", 1180, 110), BLANCO, trazo=8, ancla="mm")
    im = sello(im, (790, 48), "ARCHIVO ABIERTO", sz=44, rot=-2)
    im = cinta(im, (640, 665), "¿MUERTE O FUGA?", sz=56, rot=-1.5, bg=(18, 18, 18), fg=AMARILLO)
    im = circulo_flecha(im, (1030, 395), 100, 52, None, grosor=7, rot=-8) if False else im
    return im


def main(out):
    os.makedirs(out, exist_ok=True)
    for nombre, f in (("miniatura_V1_cinematica", v1), ("miniatura_V2_dividida", v2), ("miniatura_V3_corcho", v3)):
        im = f()
        ruta = os.path.join(out, nombre + ".jpg")
        im.save(ruta, quality=90, optimize=True)
        print(ruta, os.path.getsize(ruta) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida"))
