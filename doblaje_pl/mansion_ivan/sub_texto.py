"""Traduce al polaco el texto del botón animado 'Subscribe / Subscribed': rellena el texto original con el color plano del botón y escribe el polaco."""
import cv2, numpy as np, glob, os, sys
from PIL import Image, ImageDraw, ImageFont
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
TXT = {'rojo': 'Subskrybuj', 'gris': 'Subskrybujesz'}
S = 4

def detectar(im):
    """Devuelve (tipo, x0,y0,x1,y1) del botón rojo o gris dentro del recorte, o None."""
    b, g, r = [im[..., i].astype(np.int16) for i in range(3)]
    rojo = ((r > 190) & (g < 90) & (b < 110)).astype(np.uint8)
    gris = ((abs(r - g) < 10) & (abs(g - b) < 10) & (r > 60) & (r < 110)).astype(np.uint8)
    # el gris es el color del 'Subscribed'; limitamos a la zona donde vive el botón
    best = None
    for tipo, m in (('rojo', rojo), ('gris', gris)):
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            x, y, w, h, a = st[i]
            if w >= 30 and h >= 12 and a / (w * h) > 0.80 and 1.8 < w / h < 8 and 40 < x + w / 2 - 0 < 340:
                if best is None or a > best[5]: best = (tipo, x, y, x + w, y + h, a)
    return best

def procesar(im):
    d = detectar(im)
    if d is None: return im
    tipo, x0, y0, x1, y1, _ = d
    base = im.copy()
    reg = im[y0:y1, x0:x1].astype(np.float32)
    mn = reg.min(axis=2)
    cuerpo = np.median(reg.reshape(-1, 3)[mn.reshape(-1) < (150 if tipo == 'rojo' else 120)], axis=0) if (mn < (150 if tipo == 'rojo' else 120)).any() else reg.mean(axis=(0, 1))
    texto = (mn > (170 if tipo == 'rojo' else 140)).astype(np.uint8)
    # el borde redondeado exterior no cuenta: solo letras dentro
    inner = np.zeros_like(texto); inner[2:-2, 4:-4] = 1
    texto = cv2.dilate(texto * inner, np.ones((3, 3), np.uint8))
    # cursor: píxeles casi negros dentro del botón (borde del puntero); se restaura al final
    oscuro = ((reg.max(axis=2) < 55)).astype(np.uint8)
    cur = np.zeros_like(oscuro)
    if oscuro.sum() > 12:
        pts = cv2.findNonZero(oscuro); hull = cv2.convexHull(pts)
        cv2.fillConvexPoly(cur, hull, 1); cur = cv2.dilate(cur, np.ones((5, 5), np.uint8))
    out = base.astype(np.float32)
    r = out[y0:y1, x0:x1]
    r[texto > 0] = cuerpo
    # texto polaco
    w, h = x1 - x0, y1 - y0
    txt = TXT[tipo]
    size = h * 0.50 * S
    while True:
        f = ImageFont.truetype(FONT, int(size))
        tw = f.getlength(txt)
        if tw <= (w - 14) * S or size < 8: break
        size -= 2
    cap = Image.new('L', (w * S, h * S), 0)
    ImageDraw.Draw(cap).text((w * S / 2, h * S / 2 + h * S * 0.02), txt, font=f, fill=255, anchor='mm')
    cap = np.array(cap.resize((w, h), Image.LANCZOS)).astype(np.float32)[..., None] / 255
    r[:] = r * (1 - cap) + 255 * cap
    # restaurar cursor
    orig = im[y0:y1, x0:x1].astype(np.float32)
    r[cur > 0] = orig[cur > 0]
    out[y0:y1, x0:x1] = r
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    only = sys.argv[1:]
    for ent, sal in (('sub_in', 'sub_out'), ('sub_in2', 'sub_out2')):
        for f in sorted(glob.glob(ent + '/*.png')):
            if only and not any(o in f for o in only): continue
            cv2.imwrite(f.replace(ent, sal), procesar(cv2.imread(f)))
