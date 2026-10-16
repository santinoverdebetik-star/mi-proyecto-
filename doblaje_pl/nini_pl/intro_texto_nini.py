"""Reemplaza el texto de apertura (ES) por el polaco: borra el texto, suaviza la banda y escribe el nuevo con el mismo efecto de aparición."""
import cv2, numpy as np, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
L1 = sys.argv[1] if len(sys.argv) > 1 else 'KRĄŻY NAZWISKO, KTÓRE BUDZI ZARÓWNO'
L2 = sys.argv[2] if len(sys.argv) > 2 else 'STRACH, JAK I DZIWNĄ FASCYNACJĘ'
FPS = 30
F0, F1 = 1146, 1300
# aparición: línea 1 de 5.5 s a 6.9 s, línea 2 de 6.9 s a 9.0 s (medido sobre el original)
T1 = (5.5, 6.8); T2 = (6.9, 9.0)
Y1, Y2, CX, MAXW = 327, 392, 640, 960

def ajustar(txt, size):
    f = ImageFont.truetype(FONT, size)
    return f, f.getlength(txt)

def capa_texto(txt, yc, size=44):
    """RGBA grande con el texto centrado en yc; reduce el tamaño si no cabe."""
    while True:
        f, w = ajustar(txt, size)
        if w <= MAXW: break
        size -= 1
    # espaciado de letras ligero
    img = Image.new('L', (1280, 720), 0)
    d = ImageDraw.Draw(img)
    x = CX - w / 2
    d.text((x, yc), txt, font=f, fill=255, anchor='lm')
    return np.array(img).astype(np.float32) / 255, (x, x + w)

def nucleo(im):
    y0, y1, x0, x1 = 295, 435, 120, 1160
    reg = im[y0:y1, x0:x1].astype(np.float32)
    core = ((reg.min(axis=2) > 175) & ((reg.max(axis=2) - reg.min(axis=2)) < 70)).astype(np.uint8)
    m = np.zeros(im.shape[:2], np.uint8); m[y0:y1, x0:x1] = core * 255
    return m

FINAL = None
FRENTE = {}
def _frente_linea(m, y0, y1, x_ini, hueco=45):
    """Frente = columna más a la derecha del tramo continuo de letras blancas que empieza en x_ini (huecos < `hueco` px)."""
    cols = (m[y0:y1] > 0).sum(axis=0) >= 6
    x, ult = x_ini - 20, None
    while x < 1280:
        if cols[x]: ult = x
        elif ult is not None and x - ult > hueco: break
        elif ult is None and x > x_ini + 40: break
        x += 1
    return ult or 0

def medir_frentes():
    """Frente de aparición real del texto original en cada fotograma, monótono."""
    f1 = f2 = 0
    for n in range(F0, F1 + 1):
        m = nucleo(cv2.imread('seg_in/%05d.png' % n))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        f1 = max(f1, _frente_linea(m, 308, 348, 200)); f2 = max(f2, _frente_linea(m, 370, 414, 162))
        FRENTE[n] = (f1, f2)

def mascara_original(im, n):
    global FINAL
    if FINAL is None:
        FINAL = nucleo(cv2.imread('seg_in/%05d.png' % F1))                 # posición exacta de todas las letras (estáticas)
        medir_frentes()
    m = nucleo(im)
    f1, f2 = FRENTE[n]
    if f1 > 900 and f2 == 0: f2 = 1            # la 2ª línea ya empieza a insinuarse (letras grises) aunque aún no hay núcleo blanco
    for (y0, y1), xf, mg in (((295, 358), f1, 260), ((358, 435), f2, 450)):
        if xf > 0:
            xf = min(1280, xf + mg)
            sub = np.zeros_like(FINAL); sub[y0:y1, :xf] = FINAL[y0:y1, :xf]
            m = np.maximum(m, sub)
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))

def limpiar(im, n):
    m = mascara_original(im, n)
    if m.max() == 0: return im, m
    ch = 4
    sm = cv2.resize(im, (1280 // ch, 720 // ch), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (1280 // ch, 720 // ch), interpolation=cv2.INTER_NEAREST)
    fill = cv2.inpaint(sm, ms, 4, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (1280, 720), interpolation=cv2.INTER_CUBIC)
    fill = cv2.GaussianBlur(fill, (0, 0), 6)
    a = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 7)[..., None]
    out = im.astype(np.float32) * (1 - a) + fill.astype(np.float32) * a
    return out, m

def render(n, im):
    t = n / FPS
    out, m = limpiar(im, n)
    out = np.asarray(out, np.float32)
    # banda oscura suave tras el texto (como una sombra para que se lea)
    band = np.zeros((720, 1280), np.float32); band[300:430, 130:1150] = 1
    band = cv2.GaussianBlur(band, (0, 0), 30)[..., None]
    out = out * (1 - 0.35 * band)
    for txt, yc, (ta, tb) in ((L1, Y1, T1), (L2, Y2, T2)):
        capa, (xa, xb) = capa_texto(txt, yc)
        fo = FRENTE[n][0 if yc == Y1 else 1]
        if fo <= 0: continue
        p = np.clip((fo - (200 if yc == Y1 else 162)) / ((1064 - 200) if yc == Y1 else (1115 - 162)), 0, 1.15)
        frente = xa - 60 + p * ((xb - xa) + 120)                        # borde de aparición con degradado suave
        col = np.arange(1280, dtype=np.float32)[None, :]
        rev = np.clip((frente - col) / 70, 0, 1)
        capa = capa * rev
        glow = cv2.GaussianBlur(capa, (0, 0), 7)[..., None]
        out = out + glow * 150 * 0.85
        c = capa[..., None]
        out = out * (1 - c) + 255 * c
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    os.makedirs('seg_out', exist_ok=True)
    only = [int(x) for x in os.environ.get('ONLY', '').split(',') if x]
    for n in (only or range(F0, F1 + 1)):
        im = cv2.imread(f'seg_in/{n:05d}.png')
        cv2.imwrite(f'seg_out/{n:05d}.png', render(n, im))
