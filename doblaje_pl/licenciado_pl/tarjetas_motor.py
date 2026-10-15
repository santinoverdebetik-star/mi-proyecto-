# -*- coding: utf-8 -*-
"""Traduce el texto de las tarjetas del video: encuentra cada línea con OCR, la sigue (zoom/desplazamiento lento),
borra el texto original y escribe la traducción con la misma tipografía, color, tamaño y desvanecimiento.
Uso: python tarjetas_motor.py video.mp4 ocr_fino.json carpeta_salida [indices_de_tarjeta]
Salida: carpeta_salida/cNN/%06d.png (recortes ya traducidos) + carpeta_salida/overlays.json (posición y fotogramas de cada tarjeta)."""
import sys, os, json, re, shutil, subprocess, unicodedata, difflib
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tarjetas import CARDS

FPS = 30
FD = '/usr/share/fonts/truetype/dejavu/'
FONTS = {'serif-b': FD + 'DejaVuSerif-Bold.ttf', 'serif': FD + 'DejaVuSerif.ttf', 'sans-b': FD + 'DejaVuSans-Bold.ttf', 'sans': FD + 'DejaVuSans.ttf'}
ETIQUETAS = {"Estado de México", "Penal de Almoloya", "Guatemala", "9 de junio de 1993", "Sudamérica", "Panamá", "Nueva York", "Alexandria, Virginia"}
S = 4          # supersampling del texto


def norm(s):
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if not unicodedata.combining(c)).lower())


def _union(ds):
    xs = [pt[0] for d in ds for pt in d['box']]; ys = [pt[1] for d in ds for pt in d['box']]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return {'t': ds[0]['t'], 'box': [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], 'text': ' '.join(d['text'] for d in ds), 'score': min(d['score'] for d in ds), 'merged': True, 'parts': [id(d) for d in ds]}


def _ratio(n, es):
    r = difflib.SequenceMatcher(None, n, norm(es), autojunk=False).ratio()
    if len(n) < 0.5 * len(norm(es)) and r < 0.8: r *= 0.6
    return r


def asignar(card, dets):
    """Asigna detecciones del OCR a las líneas del config. Une fragmentos de una misma línea (el OCR a veces parte una línea en dos).
    Devuelve (lista de detecciones por línea, detecciones 'protegidas' = texto de la tarjeta que no se traduce)."""
    por_t = {}
    for d in dets: por_t.setdefault(d['t'], []).append(d)
    por = [[] for _ in card['lines']]; prot = []
    ycen = lambda d: (min(p[1] for p in d['box']) + max(p[1] for p in d['box'])) / 2
    xmin = lambda d: min(p[0] for p in d['box'])
    xmax = lambda d: max(p[0] for p in d['box'])
    for t, ds in por_t.items():
        cands = list(ds)
        ordenadas = sorted(ds, key=lambda d: (round(ycen(d) / 12), xmin(d)))
        for i in range(len(ordenadas)):
            grp = [ordenadas[i]]
            for j in range(i + 1, len(ordenadas)):
                if abs(ycen(ordenadas[j]) - ycen(grp[-1])) < 12 and xmin(ordenadas[j]) - xmax(grp[-1]) < 90:
                    grp.append(ordenadas[j]); cands.append(_union(grp))
        mejor = {}
        for c in cands:
            n = norm(c['text'])
            for i, ln in enumerate(card['lines']):
                if ln[1] is None: continue
                r = _ratio(n, ln[0])
                umbral = 0.5 if ln_credito(ln[0]) else 0.62
                if r >= umbral and (i not in mejor or r > mejor[i][0]): mejor[i] = (r, c)
        usadas = set()
        for i, (r, c) in mejor.items():
            por[i].append(c); usadas.add(id(c)); usadas.update(c.get('parts', []))
        for d in ds:
            if id(d) in usadas: continue
            n = norm(d['text'])
            if max((_ratio(n, ln[0]) for ln in card['lines'] if ln[1] is not None), default=0) < 0.4:
                prot.append(d)
    return por, prot


def ln_credito(es): return es.startswith('Mapa base')


def ajuste(dets):
    """Modelo lineal en t de centro x/y, ancho y alto de la línea. Devuelve función t -> (cx, cy, w, h) y (tmin, tmax)."""
    ts = np.array([d['t'] for d in dets])
    xs = np.array([[p[0] for p in d['box']] for d in dets]); ys = np.array([[p[1] for p in d['box']] for d in dets])
    X0, X1, Y0, Y1 = xs.min(1), xs.max(1), ys.min(1), ys.max(1)
    w, h, cx, cy = X1 - X0, Y1 - Y0, (X0 + X1) / 2, (Y0 + Y1) / 2
    ok = np.ones(len(ts), bool)
    if len(ts) >= 4:
        ok = (abs(w - np.median(w)) < 0.2 * np.median(w) + 6) & (abs(cy - np.median(cy)) < 14)
        if ok.sum() < 2: ok[:] = True
    def f(v):
        if ok.sum() >= 3 and ts[ok].max() - ts[ok].min() >= 1.4:
            c = np.polyfit(ts[ok], v[ok], 1)
            return lambda t: np.polyval(c, t)
        m = float(np.median(v[ok])); return lambda t: m
    fc, fy, fw, fh = f(cx), f(cy), f(w), f(h)
    lo, hi = ts.min(), ts.max()
    def modelo(t):
        t = min(max(t, lo - 1.5), hi + 1.5)
        return fc(t), fy(t), fw(t), fh(t)
    return modelo, (float(lo), float(hi)), float(np.median(h)), float(np.median(w))


def fuente(key, size): return ImageFont.truetype(FONTS[key], max(6, int(round(size))))


def elegir_fuente(card, es, med_h, color_sat):
    if card['al'] == 'c':
        if color_sat > 0.45: return 'serif-b'
        return 'sans' if med_h < 27 else 'serif'
    if es in ETIQUETAS: return 'sans-b'
    if color_sat > 0.45 and med_h >= 18 and es.isupper(): return 'sans-b'
    if es[:4].isdigit() and es.isupper() is False and ':' in es[:6] and es.upper() == es: return 'sans-b'
    return 'sans-b' if (es.isupper() and med_h >= 18) else 'sans'


def borrar(reg, mask):
    """Rellena el texto con el fondo cercano (inpaint a baja resolución + difuminado)."""
    h, w = reg.shape[:2]
    sc = 2 if min(h, w) < 70 else 4
    sm = cv2.resize(reg, (max(2, w // sc), max(2, h // sc)), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(mask, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    fill = cv2.inpaint(sm, ms, 3, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (w, h), interpolation=cv2.INTER_CUBIC)
    fill = cv2.GaussianBlur(fill, (0, 0), 2.5)
    a = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 1.6)[..., None]
    return (reg.astype(np.float32) * (1 - a) + fill.astype(np.float32) * a)


def procesar_tarjeta(ci, card, dets, video, salida):
    por, prot = asignar(card, dets)
    lineas = []
    for (es, pl), ds in zip(card['lines'], por):
        if pl is None or pl == es or len(ds) == 0: 
            if len(ds) == 0 and pl not in (None, es): print(f'  c{ci:02d} SIN DETECCIÓN: {es[:40]}')
            continue
        modelo, (lo, hi), med_h, med_w = ajuste(ds)
        lineas.append(dict(es=es, pl=pl, modelo=modelo, lo=lo, hi=hi, med_h=med_h, med_w=med_w, n=len(ds)))
    if not lineas: return None
    t0 = min(l['lo'] for l in lineas) - 1.2; t1 = max(l['hi'] for l in lineas) + 1.2
    n0, n1 = max(0, int(t0 * FPS)), int(t1 * FPS)
    d = os.path.join(salida, f'f{ci:02d}'); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'select=between(n\\,{n0}\\,{n1})', '-vsync', '0', '-start_number', str(n0), f'{d}/%06d.png'], check=True)
    # pasada 1: contraste del texto original en cada fotograma
    for l in lineas: l['pk'] = {}; l['cols'] = []
    for n in range(n0, n1 + 1):
        fr = cv2.imread(f'{d}/{n:06d}.png'); g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32); t = n / FPS
        for l in lineas:
            if not (l['lo'] - 0.6 <= t <= l['hi'] + 0.6): continue
            cx, cy, w, h = l['modelo'](t)
            x0, x1, y0, y1 = [int(v) for v in (cx - w / 2 - 10 - 0.04 * w, cx + w / 2 + 10 + 0.04 * w, cy - h / 2 - 8 - 0.25 * h, cy + h / 2 + 8 + 0.25 * h)]
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(1280, x1), min(720, y1)
            reg = g[y0:y1, x0:x1]
            if reg.size == 0: continue
            bg, pk = np.percentile(reg, 10), np.percentile(reg, 99.6)
            l['pk'][n] = (pk - bg, bg, (x0, y0, x1, y1), None)
            if pk - bg > 40:
                m = reg > bg + 0.5 * (pk - bg)
                if m.sum() > 8:
                    c = np.median(fr[y0:y1, x0:x1][m], axis=0); l['cols'].append(c); l['pk'][n] = (pk - bg, bg, (x0, y0, x1, y1), c)
    for l in lineas:
        v = np.array([p[0] for p in l['pk'].values()]) if l['pk'] else np.array([0.0])
        l['ref'] = max(20.0, float(np.percentile(v, 92)))
        l['color'] = np.median(np.array(l['cols']), axis=0) if l['cols'] else np.array([200, 200, 200.0])
        b, gc, r = l['color']; mx, mn = max(b, gc, r), min(b, gc, r); l['sat'] = (mx - mn) / (mx + 1e-6)
        l['font'] = elegir_fuente(card, l['es'], l['med_h'], l['sat'])
        # tamaño: el que hace que el texto español mida lo que mide el original
        f100 = fuente(l['font'], 100); l['k_es'] = f100.getlength(l['es']) / 100
        bb = f100.getbbox(l['es'], anchor='ls'); l['ink_c'] = ((bb[1] + bb[3]) / 2) / 100
    # extensión del recorte
    rx0, ry0, rx1, ry1 = 1280, 720, 0, 0
    for l in lineas:
        for n, (a, bg, box, _c) in l['pk'].items():
            rx0, ry0, rx1, ry1 = min(rx0, box[0]), min(ry0, box[1]), max(rx1, box[2]), max(ry1, box[3])
    # pasada 2: borrar (todas las líneas) y luego escribir
    pl_ext = []
    for n in range(n0, n1 + 1):
        fr = cv2.imread(f'{d}/{n:06d}.png'); out = fr.astype(np.float32); g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32); t = n / FPS
        activos = []
        for l in lineas:
            if n not in l['pk']: continue
            ctr, bg, (x0, y0, x1, y1), col = l['pk'][n]
            if ctr < 12: continue
            if col is not None and np.linalg.norm(col - l['color']) > 80: continue        # no es el texto de la tarjeta (cambió la escena)
            reg = g[y0:y1, x0:x1]
            m = (reg > bg + 0.20 * ctr).astype(np.uint8) * 255
            for pd in prot:
                if abs(pd['t'] - t) <= 0.6:
                    px = [q[0] for q in pd['box']]; py = [q[1] for q in pd['box']]
                    ax0, ax1, ay0, ay1 = min(px) - 3 - x0, max(px) + 3 - x0, min(py) - 3 - y0, max(py) + 3 - y0
                    m[max(0, ay0):max(0, ay1), max(0, ax0):max(0, ax1)] = 0
            if (m > 0).mean() > 0.40: continue                       # no se puede aislar el texto (fondo muy claro / transición de escena)
            m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
            activos.append((l, ctr, (x0, y0, x1, y1), m))
        for l, ctr, (x0, y0, x1, y1), m in activos:
            fill = borrar(np.clip(out[y0:y1, x0:x1], 0, 255).astype(np.uint8), m)
            # sustituye solo donde había texto (máscara suavizada) para no pisar otras líneas ya tratadas
            a_ = cv2.GaussianBlur((m > 0).astype(np.float32), (0, 0), 1.6)[..., None]
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a_) + fill * a_
        for l, ctr, (x0, y0, x1, y1), m in activos:
            alpha = min(1.0, ctr / l['ref'])
            cx, cy, w, h = l['modelo'](t)
            size = w / l['k_es']
            fz = fuente(l['font'], size * S)
            wp = fz.getlength(l['pl']) / S
            maxw = (1280 * 0.94) if card['al'] == 'c' else (1280 - (cx - w / 2) - 12)
            if wp > maxw:
                size *= maxw / wp; fz = fuente(l['font'], size * S); wp = fz.getlength(l['pl']) / S
            xl = cx - wp / 2 if card['al'] == 'c' else cx - w / 2
            base = cy - l['ink_c'] * size
            pad = 6
            bx0, bx1 = int(max(0, xl - pad)), int(min(1280, xl + wp + pad))
            by0, by1 = int(max(0, base - size * 1.05)), int(min(720, base + size * 0.45))
            cv = Image.new('L', ((bx1 - bx0) * S, (by1 - by0) * S), 0)
            ImageDraw.Draw(cv).text(((xl - bx0) * S, (base - by0) * S), l['pl'], font=fz, fill=255, anchor='ls')
            cov = np.array(cv.resize((bx1 - bx0, by1 - by0), Image.LANCZOS)).astype(np.float32)[..., None] / 255 * alpha
            sub = out[by0:by1, bx0:bx1]
            out[by0:by1, bx0:bx1] = sub * (1 - cov) + l['color'][None, None, :] * cov
            pl_ext.append((bx0, by0, bx1, by1))
        cv2.imwrite(f'{d}/o_{n:06d}.png', np.clip(out, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 1])
        os.remove(f'{d}/{n:06d}.png')
    # recorte final (unión de zonas tocadas)
    for (a, b, c, e) in pl_ext:
        rx0, ry0, rx1, ry1 = min(rx0, a), min(ry0, b), max(rx1, c), max(ry1, e)
    rx0, ry0 = (rx0 // 2) * 2, (ry0 // 2) * 2; rx1, ry1 = ((rx1 + 1) // 2) * 2, ((ry1 + 1) // 2) * 2
    return dict(ci=ci, n0=n0, n1=n1, box=(rx0, ry0, rx1, ry1), lineas=lineas)


def main():
    video, ocr, salida = sys.argv[1:4]
    solo = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    o = json.load(open(ocr)); os.makedirs(salida, exist_ok=True)
    meta_f = os.path.join(salida, 'overlays.json')
    meta = json.load(open(meta_f)) if os.path.exists(meta_f) else {}
    for ci, card in enumerate(CARDS):
        if solo is not None and ci not in solo: continue
        info = procesar_tarjeta(ci, card, o[str(ci)]['dets'], video, salida)
        if info is None: print(f'c{ci:02d}: sin cambios'); continue
        meta[str(ci)] = dict(n0=info['n0'], n1=info['n1'], box=info['box'], lineas=[dict(es=l['es'], pl=l['pl'], font=l['font'], n=l['n'], ref=round(l['ref'], 1)) for l in info['lineas']])
        json.dump(meta, open(meta_f, 'w'), ensure_ascii=False, indent=1)
        print(f'c{ci:02d}: {len(info["lineas"])} líneas, fotogramas {info["n0"]}-{info["n1"]}, recorte {info["box"]}', flush=True)


if __name__ == '__main__':
    main()
