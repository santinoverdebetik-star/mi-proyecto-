#!/usr/bin/env python3
"""Arma el video: fotos con zoom/paneo lento (Ken Burns), cortes secos cada 2-4 s, tableros de evidencias del FBI
al inicio de cada Parte, titulo de cada regla, sello (REAL / A MEDIAS / INVENTADA), subtitulos con palabras clave
resaltadas, vineta + grano.  Render en paralelo por trozos.

Uso:
  python3 armar_video.py preparar  IMGS_DIR  TRABAJO_DIR            # gradua las fotos y crea los tableros
  python3 armar_video.py plan      TIMELINE   TRABAJO_DIR            # crea plan.json (cortes y fotos)
  python3 armar_video.py render    TIMELINE   TRABAJO_DIR  T0 T1  N  # renderiza [T0,T1) s en N procesos -> parte_*.mp4
  python3 armar_video.py unir      TRABAJO_DIR MEZCLA.wav  SALIDA.mp4
"""
import bisect, glob, json, math, os, random, re, subprocess, sys, unicodedata
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1280, 720, 25
BW, BH = 1920, 1080                       # tamano base de las fotos graduadas (margen para el zoom)
FSERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FSANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FMONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

TAGS = {  # etiquetas de fotos preferidas por bloque
    "gancho": ["H01", "H03", "G28", "G29", "G12", "G13", "G30", "G03"],
    "sellos": ["G16", "G17", "G15", "G26", "G14"],
    "parte1": ["G14", "G10", "G32", "G06"], "parte2": ["G11", "G01", "G26", "G02"],
    "parte3": ["P3", "G17", "G15", "G26", "G35"], "parte4": ["G03", "G20", "G33", "G25"],
    "parte5": ["G05", "G25", "G01", "G30"],
    1: ["G10", "G14", "G32", "G06"], 2: ["G31", "G35", "G40", "G07"], 3: ["G05", "G25", "G12", "G32"],
    4: ["G18", "G06", "G19", "R4"], 5: ["R5", "G34", "G23"], 6: ["G11", "G01", "R6"], 7: ["G26", "G02", "G21"],
    8: ["R8", "G11", "G37"], 9: ["R9", "G21", "G22", "G04"], 10: ["R10", "G35", "G40", "G19"],
    11: ["R11", "G24", "G33"], 12: ["G09", "G06", "G31", "R12"], 13: ["R13", "G16", "G12", "G30"],
    14: ["G03", "G20", "G33", "R14"], 15: ["R15", "G25", "G32", "G02"], 16: ["R16", "G15", "G26"],
    17: ["R17", "G17", "G15", "G08"], 18: ["G05", "G25", "G01"], 19: ["G30", "G28", "G27", "G04"],
    "cierre": ["C01", "C03", "C05", "C06", "C07", "G04", "G27", "G40"],
}
NUM = {w: i + 1 for i, w in enumerate("uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince "
                                      "dieciséis diecisiete dieciocho diecinueve veinte".split())}
RESALTAR = {"real", "reales", "inventada", "medias", "verdad", "comision", "omerta", "fbi", "dinero", "miedo", "poder",
            "familia", "orgullo", "porque", "caro", "gotti", "castellano", "lo", "piccolo"}


# Huecos para clips / fotos de la serie: (bloque, palabra ancla, aparicion, descripcion de la escena a poner).
# 4 s cada uno; el clip va con la narracion encima. Se activan dejando clips/slot_NN.mp4 (o .jpg) en la carpeta de trabajo.
SLOTS = [
    ("gancho", "striptease", 1, "El Bada Bing, por fuera o por dentro (cualquier episodio)"),
    (1, "carmela", 1, "Paulie y Vito entregan el dinero a Carmela en el hospital (episodio 'Mayham', temporada 6)"),
    (3, "ginny", 2, "Ralph bromea sobre Ginny y Johnny Sack se enfurece (temporada 4, 'The Weight')"),
    (4, "vito", 2, "Vito es descubierto y reaccionan Phil y los de Nueva York (temporada 6)"),
    (6, "barbacoa", 1, "Tony en shorts en la barbacoa y el reproche 'A Don doesn't wear shorts' (verificar episodio)"),
    (7, "boda", 1, "Johnny Sack llora cuando lo arrestan en la boda de su hija (temporada 6)"),
    (8, "boca", 1, "Junior en Boca Ratón (temporada 1, episodio 'Boca')"),
    (9, "santo", 1, "Ceremonia de iniciacion: pinchazo e imagen de santo ardiendo"),
    (10, "traficantes", 1, "Christopher contrata a los traficantes para el trabajo 'de gente de fuera' (temporada 4, 'Whitecaps')"),
    (11, "monopoly", 1, "Pelea de Bobby y Tony tras el Monopoly (episodio 'Soprano Home Movies', 6.13)"),
    (12, "cuchillo", 1, "Silvio y Carlo matan a Fat Dom en Satriale's (episodio 'Cold Stones', 6.11)"),
    (13, "peeps", 1, "Tony Blundetto y el asesinato de Joey Peeps (temporada 5)"),
    (14, "carretera", 1, "Tony y Christopher tras el accidente de auto (episodio 'Kennedy and Heidi', 6.18)"),
    (15, "chris", 1, "J.T. Dolan: 'Chris, you're in the mafia!' (episodio 'Walk Like a Man', temporada 6)"),
    (16, "tribunal", 1, "Johnny Sack ante el tribunal / acuerdo con la fiscalia (temporada 6)"),
    (17, "pussy", 1, "Big Pussy y el FBI (temporada 2)"),
    (18, "coco", 1, "Tony golpea a Coco por lo de Meadow (episodio 'The Second Coming', 6.19)"),
    (19, "harris", 1, "Tony y el agente Harris (temporada 6)"),
]
SLOT_DUR = 4.0
# Fotos historicas reales (dominio publico), en el momento en que el guion nombra al personaje: (bloque, palabra ancla, aparicion, clave de foto)
REAL_DUR = 3.4
REAL_SLOTS = [("parte3", "luciano", 1, "luciano"), ("parte3", "valachi", 1, "valachi1"), ("parte3", "pistone", 1, "pistone"),
              (2, "gotti", 1, "gotti"), (10, "sparks", 1, "sparks"), (10, "castellano", 1, "castellano"),
              (10, "gigante", 1, "gigante"), (9, "sam", 1, "decavalcante"), (17, "gravano", 1, "gravano"), (17, "valachi", 1, "valachi2")]


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


# --------------------------------------------------------------------------- fotos
def graduar(img):
    h, w = img.shape[:2]
    ar = w / h
    if ar >= 1.5:                                             # recorte 16:9 (sesgo vertical hacia arriba)
        nw = min(w, int(h * 16 / 9)); nh = int(nw * 9 / 16)
        x0 = (w - nw) // 2; y0 = int((h - nh) * 0.42)
        img = img[y0:y0 + nh, x0:x0 + nw]
        img = cv2.resize(img, (BW, BH), interpolation=cv2.INTER_AREA if nw > BW else cv2.INTER_CUBIC)
    else:                                                     # 4:3 o mas cuadrada: fondo desenfocado a los costados
        fondo = cv2.resize(img, (BW, BH), interpolation=cv2.INTER_AREA)
        fondo = cv2.GaussianBlur(fondo, (0, 0), 38) * 0.55
        fw = int(w * BH / h); fg = cv2.resize(img, (fw, BH), interpolation=cv2.INTER_AREA)
        x0 = (BW - fw) // 2
        fondo[:, x0:x0 + fw] = fg
        img = fondo.astype(np.uint8)
    x = img.astype(np.float32) / 255.0
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None] / 255.0
    x = gris + (x - gris) * 0.55                              # desaturado
    x *= np.array([0.90, 0.97, 1.07], np.float32)             # tinte calido (BGR)
    x = np.clip((x - 0.5) * 1.10 + 0.5 - 0.035, 0, 1) ** 1.10  # contraste y un poco mas oscuro
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    r = np.sqrt(((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH / 2) / (BH / 2)) ** 2)
    x *= (1 - 0.52 * np.clip(r / 1.35, 0, 1) ** 2.2)[..., None]   # vineta suave
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)


def fuente(ruta, tam):
    return ImageFont.truetype(ruta, tam)


def textura_corcho(rng):
    base = np.zeros((BH, BW, 3), np.float32); base[:] = (60, 105, 160)       # BGR marron corcho
    ruido = rng.normal(0, 1, (BH // 3, BW // 3)).astype(np.float32)
    ruido = cv2.resize(cv2.GaussianBlur(ruido, (0, 0), 1.0), (BW, BH)) * 22
    puntos = (rng.random((BH, BW)) > 0.985).astype(np.float32) * -40
    base += ruido[..., None] + puntos[..., None]
    return np.clip(base, 0, 255).astype(np.uint8)


def tablero(titulo_parte, tarjetas, rng, sellos=False):
    """Tablero de evidencias: corcho, tarjetas inclinadas con chinches e hilo rojo."""
    corcho = Image.fromarray(cv2.cvtColor(textura_corcho(rng), cv2.COLOR_BGR2RGB)).convert("RGBA")
    n = len(tarjetas)
    cw = 480 if n <= 3 else 360; ch = 330 if n <= 3 else 270
    cols = n if n <= 3 else 3
    filas = math.ceil(n / cols)
    pos = []
    for i in range(n):
        f, c = divmod(i, cols)
        enfila = cols if (f < filas - 1 or n % cols == 0) else n % cols
        x0 = (BW - enfila * (cw + 60) + 60) / 2
        pos.append((int(x0 + c * (cw + 60) + rng.integers(-18, 18)), int(300 + f * (ch + 60) + rng.integers(-14, 14))))
    pins = []
    capa_sombra = Image.new("RGBA", corcho.size, (0, 0, 0, 0))
    tarjetas_img = []
    for (x, y), (cab, txt, color) in zip(pos, tarjetas):
        card = Image.new("RGBA", (cw, ch), (233, 224, 196, 255))
        d = ImageDraw.Draw(card)
        d.rectangle([0, 0, cw - 1, ch - 1], outline=(150, 130, 95, 255), width=3)
        d.text((22, 18), cab, font=fuente(FMONO, 30), fill=(150, 30, 30, 255))
        lineas = []; actual = ""
        for pal in txt.split():
            if d.textlength(actual + " " + pal, font=fuente(FSERIF, 31)) > cw - 44 and actual:
                lineas.append(actual); actual = pal
            else: actual = (actual + " " + pal).strip()
        lineas.append(actual)
        for k, l in enumerate(lineas[:6]):
            d.text((22, 70 + k * 40), l, font=fuente(FSERIF, 31), fill=(35, 30, 25, 255))
        if color:                                                      # sello pequeno
            d.rounded_rectangle([cw - 190, ch - 70, cw - 18, ch - 20], radius=6, outline=color + (255,), width=4)
            d.text((cw - 180, ch - 64), sellos if isinstance(sellos, str) else "", font=fuente(FMONO, 28), fill=color + (255,))
        ang = float(rng.uniform(-4.5, 4.5))
        rot = card.rotate(ang, expand=True, resample=Image.BICUBIC)
        sombra = Image.new("RGBA", rot.size, (0, 0, 0, 120)); sombra.putalpha(rot.split()[3].point(lambda v: min(120, v)))
        capa_sombra.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(7)), (x + 8, y + 10))
        tarjetas_img.append((rot, x, y))
        pins.append((x + rot.size[0] // 2 + int(rng.integers(-30, 30)), y + 14))
    corcho.alpha_composite(capa_sombra)
    dh = ImageDraw.Draw(corcho)
    for a, b in zip(pins[:-1], pins[1:]):                              # hilo rojo con leve curva
        mx, my = (a[0] + b[0]) // 2, (a[1] + b[1]) // 2 + 38
        pts = [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t ** 2 * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t ** 2 * b[1])
               for t in np.linspace(0, 1, 30)]
        dh.line(pts, fill=(170, 25, 25, 255), width=5)
    for rot, x, y in tarjetas_img:
        corcho.alpha_composite(rot, (x, y))
    dh = ImageDraw.Draw(corcho)
    for (px, py) in pins:
        dh.ellipse([px - 11, py - 11, px + 11, py + 11], fill=(160, 20, 20, 255), outline=(60, 5, 5, 255), width=2)
        dh.ellipse([px - 6, py - 7, px - 1, py - 2], fill=(235, 130, 130, 255))
    # banda de titulo
    banda = Image.new("RGBA", (BW, 150), (0, 0, 0, 0)); db = ImageDraw.Draw(banda)
    db.rectangle([0, 0, BW, 150], fill=(15, 12, 10, 205))
    db.text((BW // 2, 75), titulo_parte, font=fuente(FSERIF, 56), fill=(245, 240, 228, 255), anchor="mm")
    corcho.alpha_composite(banda, (0, 70))
    img = cv2.cvtColor(np.array(corcho.convert("RGB")), cv2.COLOR_RGB2BGR)
    # oscurecer y vinetear como el resto
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    r = np.sqrt(((xx - BW / 2) / (BW / 2)) ** 2 + ((yy - BH / 2) / (BH / 2)) ** 2)
    v = (1 - 0.5 * np.clip(r / 1.35, 0, 1) ** 2.2)[..., None]
    return (img.astype(np.float32) * 0.8 * v).astype(np.uint8)


def preparar(imgs_dir, trabajo, timeline_json=None):
    os.makedirs(os.path.join(trabajo, "graded"), exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(imgs_dir, "*.jpg"))):
        out = os.path.join(trabajo, "graded", os.path.basename(f))
        if os.path.exists(out): continue
        img = cv2.imread(f)
        if img is None: continue
        cv2.imwrite(out, graduar(img), [cv2.IMWRITE_JPEG_QUALITY, 92]); n += 1
    print("fotos graduadas:", n, "| total:", len(glob.glob(os.path.join(trabajo, 'graded', '*.jpg'))))


def preparar_reales(reales_dir, trabajo):
    os.makedirs(os.path.join(trabajo, "reales"), exist_ok=True)
    n = 0
    for f in sorted(glob.glob(os.path.join(reales_dir, "*.jpg"))):
        img = cv2.imread(f)
        if img is None: continue
        cv2.imwrite(os.path.join(trabajo, "reales", os.path.basename(f)), graduar(img), [cv2.IMWRITE_JPEG_QUALITY, 93]); n += 1
    if os.path.exists(os.path.join(reales_dir, "reales.json")):
        import shutil; shutil.copy(os.path.join(reales_dir, "reales.json"), os.path.join(trabajo, "reales", "reales.json"))
    print("fotos reales graduadas:", n)


def crear_tableros(timeline_json, trabajo):
    tl = json.load(open(timeline_json, encoding="utf-8"))
    rng = np.random.default_rng(5)
    partes, actual = [], None
    for b in tl["bloques"]:
        if b["tipo"] == "parte": actual = {"b": b, "reglas": []}; partes.append(actual)
        elif b["tipo"] == "regla" and actual is not None: actual["reglas"].append(b)
    os.makedirs(os.path.join(trabajo, "tableros"), exist_ok=True)
    for p in partes:
        tit = f"PARTE {NUM[p['b']['n']]}  ·  {p['b']['titulo'].upper().rstrip('.')}"
        cards = [(f"REGLA {NUM[r['n']]}", r["titulo"], None) for r in p["reglas"]]
        cv2.imwrite(os.path.join(trabajo, "tableros", f"parte{NUM[p['b']['n']]}.jpg"), tablero(tit, cards, rng),
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
    # tablero de sellos
    rng2 = np.random.default_rng(9)
    sc = [("SELLO 1", "Existió en la mafia real", (150, 30, 30)), ("SELLO 2", "Existió, pero cambiaba según la familia o el jefe", (120, 80, 20)),
          ("SELLO 3", "Solo vive dentro de la serie", (60, 60, 100))]
    img = tablero("CÓMO LEER ESTE EXPEDIENTE", [(c, t, None) for c, t, _ in sc], rng2)
    # sellos grandes sobre las tarjetas
    cv2.imwrite(os.path.join(trabajo, "tableros", "sellos.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("tableros:", sorted(os.listdir(os.path.join(trabajo, "tableros"))))


# --------------------------------------------------------------------------- plan de cortes
def plan(timeline_json, trabajo, semilla=3):
    rnd = random.Random(semilla)
    tl = json.load(open(timeline_json, encoding="utf-8")); D = tl["duracion"]
    pool = {}
    for f in sorted(glob.glob(os.path.join(trabajo, "graded", "*.jpg"))):
        nombre = os.path.basename(f)
        tag = re.match(r"(?:ov_)?([A-Z]+\d*)_", nombre).group(1)
        pool.setdefault(tag, []).append(nombre)
    todos = [n for v in pool.values() for n in v]
    usos = {n: 0 for n in todos}
    reciente = []
    # bloques con su etiqueta
    bl = []; parte = 0
    for b in tl["bloques"]:
        if b["tipo"] == "parte": parte = NUM[b["n"]]
        clave = ("gancho" if b["tipo"] == "gancho" else "sellos" if b["tipo"] == "sellos" else "cierre" if b["tipo"] == "cierre"
                 else f"parte{NUM[b['n']]}" if b["tipo"] == "parte" else NUM[b["n"]])
        bl.append((b["t0"], b["t1"], clave, b))
    cortes = []; t = 0.0
    def elegir(clave):
        pref = [n for tg in TAGS.get(clave, []) for n in pool.get(tg, [])]
        cand = [n for n in pref if n not in reciente[-14:]] or [n for n in todos if n not in reciente[-14:]] or todos
        minimo = min(usos[n] for n in cand)
        cand = [n for n in cand if usos[n] <= minimo + 1] or cand
        n = rnd.choice(cand); usos[n] += 1; reciente.append(n); return n
    movs = ["zoom_in", "zoom_out", "pan_izq", "pan_der", "zoom_in", "zoom_out", "pan_arr"]
    for t0, t1, clave, b in bl:
        # tablero al inicio de partes (5.5 s) y de los sellos (8 s)
        t = t0
        if b["tipo"] == "parte":
            dur = min(5.8, t1 - t0)
            cortes.append({"t0": t, "t1": t + dur, "img": f"tableros/parte{NUM[b['n']]}.jpg", "mov": "zoom_in", "z": [1.0, 1.06]})
            t += dur
        elif b["tipo"] == "sellos":
            dur = min(9.0, t1 - t0)
            cortes.append({"t0": t, "t1": t + dur, "img": "tableros/sellos.jpg", "mov": "zoom_in", "z": [1.0, 1.06]})
            t += dur
        while t < t1 - 0.01:
            dur = rnd.uniform(2.6, 4.1)
            if t1 - (t + dur) < 2.0: dur = t1 - t
            n = elegir(clave); mov = rnd.choice(movs)
            cortes.append({"t0": round(t, 3), "t1": round(t + dur, 3), "img": "graded/" + n, "mov": mov,
                           "z": [1.0, 1.0 + rnd.uniform(0.10, 0.17)], "fx": rnd.uniform(0.3, 0.7), "fy": rnd.uniform(0.35, 0.6)})
            t += dur
    cortes[-1]["t1"] = D
    # huecos para clips de la serie
    pal = tl["palabras"]
    bloque_de = {}
    for t0_, t1_, clave_, b_ in bl:
        k_ = ("gancho" if b_["tipo"] == "gancho" else NUM[b_["n"]] if b_["tipo"] == "regla"
              else f"parte{NUM[b_['n']]}" if b_["tipo"] == "parte" else None)
        bloque_de[k_] = (t0_, t1_)
    huecos = []
    os.makedirs(os.path.join(trabajo, "slates"), exist_ok=True)
    for k, (bq, ancla, nth, desc) in enumerate(SLOTS, 1):
        a, b_ = bloque_de[bq]
        veces = [w["t0"] for w in pal if a <= w["t0"] < b_ and norm(w["w"]) == ancla]
        ini = veces[min(nth, len(veces)) - 1] - 0.4 if veces else (a + b_) / 2
        ini = max(ini, a + 6.0 if bq != "gancho" else a + 14.0)
        ini = min(ini, b_ - SLOT_DUR - 0.5)
        huecos.append({"id": k, "t0": round(ini, 2), "t1": round(ini + SLOT_DUR, 2), "desc": desc})
    reales_h = []
    ruta_meta = os.path.join(trabajo, "reales", "reales.json")
    meta_reales = json.load(open(ruta_meta, encoding="utf-8")) if os.path.exists(ruta_meta) else {}
    pendientes = []
    for bq, ancla, nth, clave in REAL_SLOTS:
        if clave not in meta_reales or bq not in bloque_de or not os.path.exists(os.path.join(trabajo, "reales", clave + ".jpg")): continue
        a, b_ = bloque_de[bq]
        veces = [w["t0"] for w in pal if a <= w["t0"] < b_ and norm(w["w"]) == ancla]
        if veces: pendientes.append((veces[min(nth, len(veces)) - 1] - 0.3, a, b_, clave))
    prev_fin = 0.0
    for ini, a, b_, clave in sorted(pendientes):
        ini = max(ini, a + 5.0, prev_fin + 0.15)
        for (o0, o1) in [(h["t0"], h["t1"]) for h in huecos] + [(r["t0"], r["t1"]) for r in reales_h]:
            if ini < o1 + 0.1 and ini + REAL_DUR > o0 - 0.1: ini = o1 + 0.15
        ini = min(ini, b_ - REAL_DUR - 0.3)
        reales_h.append({"clave": clave, "t0": round(ini, 2), "t1": round(ini + REAL_DUR, 2), "pie": meta_reales[clave]["pie"]})
        prev_fin = ini + REAL_DUR
    nuevos = []
    for c in cortes:
        partes_ = [c]
        for h in huecos + reales_h:
            sig = []
            for q in partes_:
                if q["t1"] <= h["t0"] or q["t0"] >= h["t1"]: sig.append(q); continue
                if q["t0"] < h["t0"] - 0.3: sig.append(dict(q, t1=h["t0"]))
                if q["t1"] > h["t1"] + 0.3: sig.append(dict(q, t0=h["t1"]))
            partes_ = sig
        nuevos += partes_
    for h in huecos:
        nuevos.append({"t0": h["t0"], "t1": h["t1"], "img": f"slates/slot_{h['id']:02d}.jpg", "mov": "quieto", "z": [1.0, 1.0],
                       "slot": h["id"], "desc": h["desc"]})
        cv2.imwrite(os.path.join(trabajo, "slates", f"slot_{h['id']:02d}.jpg"), slate(h), [cv2.IMWRITE_JPEG_QUALITY, 90])
    for r in reales_h:
        nuevos.append({"t0": r["t0"], "t1": r["t1"], "img": f"reales/{r['clave']}.jpg", "mov": "zoom_in", "z": [1.0, 1.07], "fx": 0.5, "fy": 0.42,
                       "real": r["clave"]})
    cortes = sorted(nuevos, key=lambda c: c["t0"])
    for a_, b_ in zip(cortes[:-1], cortes[1:]):
        a_["t1"] = b_["t0"]
    cortes[-1]["t1"] = D
    with open(os.path.join(trabajo, "clips_serie.csv"), "w", encoding="utf-8") as fh:
        fh.write("hueco,archivo_a_dejar_en_clips/,inicio_s,fin_s,inicio_mmss,escena_a_buscar\n")
        for h in huecos:
            mm = lambda s: f"{int(s // 60):02d}:{s % 60:05.2f}"
            fh.write(f'{h["id"]},slot_{h["id"]:02d}.mp4,{h["t0"]},{h["t1"]},{mm(h["t0"])},"{h["desc"]}"\n')
    # titulos y sellos
    ov = []
    for t0, t1, clave, b in bl:
        if b["tipo"] == "regla":
            ov.append({"tipo": "titulo", "t0": b["t0"] + 0.9, "t1": b["t0"] + 5.4, "cab": f"REGLA {NUM[b['n']]}", "txt": b["titulo"]})
            if "t_sello" in b:
                ov.append({"tipo": "sello", "t0": b["t_sello"], "t1": b["t_sello"] + 3.8, "txt": b["sello"].upper()})
        elif b["tipo"] == "cierre":
            ov.append({"tipo": "titulo", "t0": b["t0"] + 0.4, "t1": b["t0"] + 4.2, "cab": "CIERRE", "txt": "Hagamos cuentas"})
    for r in reales_h:
        ov.append({"tipo": "pie", "t0": r["t0"] + 0.25, "t1": r["t1"] - 0.05, "txt": r["pie"]})
    uso_total = sum(usos.values())
    print("fotos reales colocadas:", [(r["clave"], r["t0"]) for r in reales_h])
    json.dump({"duracion": D, "cortes": cortes, "overlays": ov}, open(os.path.join(trabajo, "plan.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"cortes: {len(cortes)} | duracion media {D / len(cortes):.2f} s | fotos distintas usadas: {sum(1 for v in usos.values() if v)} "
          f"de {len(todos)} | usos por foto (max/med): {max(usos.values())}/{uso_total / max(1, len(todos)):.1f}")


# --------------------------------------------------------------------------- overlays
def slate(h):
    img = Image.new("RGB", (BW, BH), (14, 12, 11)); d = ImageDraw.Draw(img)
    d.rectangle([60, 60, BW - 60, BH - 60], outline=(200, 60, 50), width=6)
    d.text((BW // 2, 230), f"HUECO {h['id']:02d} · CLIP O FOTO DE LA SERIE", font=fuente(FMONO, 58), fill=(230, 80, 66), anchor="mm")
    lineas = []; actual = ""
    for p in h["desc"].split():
        if d.textlength(actual + " " + p, font=fuente(FSERIF, 62)) > BW - 340 and actual: lineas.append(actual); actual = p
        else: actual = (actual + " " + p).strip()
    lineas.append(actual)
    for k, l in enumerate(lineas): d.text((BW // 2, 430 + 86 * k), l, font=fuente(FSERIF, 62), fill=(245, 240, 228), anchor="mm")
    d.text((BW // 2, BH - 330), f"{h['t0']:.1f} s  →  {h['t1']:.1f} s  (3-5 s, con la narracion encima)", font=fuente(FMONO, 40), fill=(170, 160, 140), anchor="mm")
    d.text((BW // 2, BH - 270), f"dejar el archivo como clips/slot_{h['id']:02d}.mp4  (o .jpg)", font=fuente(FMONO, 40), fill=(170, 160, 140), anchor="mm")
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def graduar_cuadro(f):
    """mismo look que las fotos, para un cuadro de clip ya a W x H"""
    x = f.astype(np.float32) / 255.0
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None] / 255.0
    x = g + (x - g) * 0.55
    x *= np.array([0.90, 0.97, 1.07], np.float32)
    x = np.clip((x - 0.5) * 1.10 + 0.5 - 0.035, 0, 1) ** 1.10
    return (np.clip(x * VIGNETA, 0, 1) * 255).astype(np.uint8)


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETA = (1 - 0.52 * np.clip(np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2) / 1.35, 0, 1) ** 2.2)[..., None]


def cargar_clip(trabajo, slot, dur):
    """devuelve ('video', [cuadros]) | ('foto', imagen graduada) | None"""
    for ext in ("mp4", "mov", "mkv", "webm", "avi", "m4v"):
        f = os.path.join(trabajo, "clips", f"slot_{slot:02d}.{ext}")
        if os.path.exists(f):
            cap = cv2.VideoCapture(f); fps = cap.get(cv2.CAP_PROP_FPS) or 25; cuadros = []
            while len(cuadros) < int(dur * FPS) + 5:
                ok, fr = cap.read()
                if not ok: break
                h, w = fr.shape[:2]; k = max(W / w, H / h)
                fr = cv2.resize(fr, (int(w * k) + 1, int(h * k) + 1)); y0 = (fr.shape[0] - H) // 2; x0 = (fr.shape[1] - W) // 2
                cuadros.append(graduar_cuadro(fr[y0:y0 + H, x0:x0 + W]))
                for _ in range(max(0, int(round(fps / FPS)) - 1)): cap.read()
            cap.release()
            if cuadros: return ("video", cuadros)
    for ext in ("jpg", "jpeg", "png"):
        f = os.path.join(trabajo, "clips", f"slot_{slot:02d}.{ext}")
        if os.path.exists(f):
            img = cv2.imread(f)
            if img is not None: return ("foto", graduar(img))
    return None


def render_titulo(cab, txt):
    img = Image.new("RGBA", (W, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f1, f2 = fuente(FMONO, 26), fuente(FSERIF, 50)
    lineas = []; actual = ""
    for p in txt.split():
        if d.textlength(actual + " " + p, font=f2) > W - 140 and actual: lineas.append(actual); actual = p
        else: actual = (actual + " " + p).strip()
    lineas.append(actual)
    alto = 48 + 60 * len(lineas)
    for off, col in (((3, 3), (0, 0, 0, 215)), ((0, 0), None)):
        x = 64 + off[0]
        d.text((x, 12 + off[1]), cab, font=f1, fill=(col or (214, 70, 60, 255)))
        for k, l in enumerate(lineas):
            d.text((x, 48 + 60 * k + off[1]), l, font=f2, fill=(col or (250, 247, 240, 255)))
    return np.array(img.crop((0, 0, W, min(190, alto + 24))))


def render_pie(txt):
    f = fuente(FSERIF, 30); tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10))); w = int(tmp.textlength(txt, font=f))
    img = Image.new("RGBA", (w + 56, 62), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w + 55, 61], fill=(12, 10, 9, 190)); d.rectangle([0, 0, 7, 61], fill=(190, 40, 40, 255))
    d.text((26, 14), txt, font=f, fill=(245, 241, 232, 255))
    return np.array(img)


def render_sello(txt):
    col = {"REAL": (190, 40, 40), "A MEDIAS": (205, 130, 30), "INVENTADA": (70, 100, 190)}.get(txt, (190, 40, 40))
    f = fuente(FMONO, 64); tmp = Image.new("RGBA", (10, 10)); wtxt = int(ImageDraw.Draw(tmp).textlength(txt, font=f))
    img = Image.new("RGBA", (wtxt + 70, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, img.size[0] - 5, 125], radius=10, outline=col + (235,), width=9)
    d.rounded_rectangle([16, 16, img.size[0] - 17, 113], radius=6, outline=col + (200,), width=3)
    d.text((img.size[0] // 2, 66), txt, font=f, fill=col + (235,), anchor="mm")
    img = img.rotate(8, expand=True, resample=Image.BICUBIC)
    a = np.array(img).astype(np.float32)
    mancha = (np.random.default_rng(2).random(a.shape[:2]) > 0.18).astype(np.float32)   # tinta irregular
    a[..., 3] *= (0.55 + 0.45 * mancha)
    return a.astype(np.uint8)


def render_subtitulo(palabras):
    f = fuente(FSANS, 40)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10))); esp = tmp.textlength(" ", font=f)
    anchos = [tmp.textlength(p["w"], font=f) for p in palabras]
    total = sum(anchos) + esp * (len(palabras) - 1)
    img = Image.new("RGBA", (int(total) + 40, 78), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x = 20
    for p, a in zip(palabras, anchos):
        txt = p["w"]; limpio = re.sub(r"[^\wáéíóúñü]", "", txt, flags=re.I)
        caps = limpio.isupper() and len(limpio) >= 3
        res = caps or norm(txt) in RESALTAR
        d.text((x, 14), txt, font=f, fill=(255, 214, 51, 255) if res else (255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
        x += a + esp
    return np.array(img)


def frases(palabras):
    out, cur = [], []
    for i, p in enumerate(palabras):
        cur.append(p)
        fin = bool(re.search(r"[.,;:?!…]$", p["w"])) and len(cur) >= 3
        pausa = i + 1 < len(palabras) and palabras[i + 1]["t0"] - p["t1"] > 0.55
        if len(cur) >= 6 or fin or pausa or i == len(palabras) - 1:
            out.append(cur); cur = []
    return out


def pegar(frame, ov, x, y, alpha=1.0):
    h, w = ov.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    sub = ov[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (sub[..., 3:4].astype(np.float32) / 255.0) * alpha
    reg = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = (reg * (1 - a) + sub[..., 2::-1].astype(np.float32)[..., ::-1][..., [0, 1, 2]] * 0 + (sub[..., :3][..., ::-1]).astype(np.float32) * a).astype(np.uint8)


# --------------------------------------------------------------------------- render
def ease(x):
    return x * x * (3 - 2 * x)


def ventana(c, p):
    z0, z1 = c["z"]; mov = c["mov"]; fx, fy = c.get("fx", 0.5), c.get("fy", 0.5)
    p = ease(p)
    if mov == "quieto": z, cx, cy = 1.0, 0.5, 0.5
    elif mov == "zoom_in": z, cx, cy = z0 + (z1 - z0) * p, 0.5 + (fx - 0.5) * 0.4 * p, 0.5 + (fy - 0.5) * 0.4 * p
    elif mov == "zoom_out": z, cx, cy = z1 - (z1 - z0) * p, 0.5 + (fx - 0.5) * 0.4 * (1 - p), 0.5 + (fy - 0.5) * 0.4 * (1 - p)
    elif mov == "pan_izq": z, cx, cy = z1 * 0.97, 0.62 - 0.24 * p, fy
    elif mov == "pan_der": z, cx, cy = z1 * 0.97, 0.38 + 0.24 * p, fy
    else: z, cx, cy = z1 * 0.97, 0.5, 0.60 - 0.20 * p
    z = max(1.0, z)
    w, h = BW / z, BH / z
    x0 = min(max(cx * BW - w / 2, 0), BW - w); y0 = min(max(cy * BH - h / 2, 0), BH - h)
    return x0, y0, w, h


def render_trozo(args):
    trabajo, ini, fin, idx, mezcla_dummy = args
    plan_ = json.load(open(os.path.join(trabajo, "plan.json"), encoding="utf-8"))
    tl = json.load(open(os.path.join(trabajo, "timeline.json"), encoding="utf-8"))
    cortes = plan_["cortes"]; tiempos = [c["t0"] for c in cortes]
    ov = plan_["overlays"]
    fr = frases(tl["palabras"]); fr_t0 = [f[0]["t0"] for f in fr]
    cache_img, cache_ov, cache_sub, cache_clip = {}, {}, {}, {}
    rng = np.random.default_rng(100 + idx)
    ruido = [rng.normal(128, 40, (H, W, 3)).clip(0, 255).astype(np.uint8) for _ in range(6)]
    salida = os.path.join(trabajo, f"parte_{idx:02d}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-threads", "1", salida],
                          stdin=subprocess.PIPE)
    n0, n1 = int(round(ini * FPS)), int(round(fin * FPS))
    for n in range(n0, n1):
        t = n / FPS
        i = max(0, bisect.bisect_right(tiempos, t) - 1); c = cortes[i]
        clip = None
        if "slot" in c:
            if c["slot"] not in cache_clip: cache_clip[c["slot"]] = cargar_clip(trabajo, c["slot"], c["t1"] - c["t0"])
            clip = cache_clip[c["slot"]]
        p = (t - c["t0"]) / max(0.01, c["t1"] - c["t0"])
        if clip is not None and clip[0] == "video":
            frame = clip[1][min(len(clip[1]) - 1, int((t - c["t0"]) * FPS))].copy()
        else:
            ruta_img = c["img"]
            if clip is not None and clip[0] == "foto": cache_img["__foto%d" % c["slot"]] = clip[1]; ruta_img = "__foto%d" % c["slot"]
            if ruta_img not in cache_img:
                if len(cache_img) > 6: cache_img.pop(next(iter(cache_img)))
                cache_img[ruta_img] = cv2.imread(os.path.join(trabajo, ruta_img))
            base = cache_img[ruta_img]
            cc = c if clip is None or clip[0] != "foto" else dict(c, mov="zoom_in", z=[1.0, 1.1])
            x0, y0, w, h = ventana(cc, min(1, max(0, p)))
            s = W / w
            M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
            frame = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        frame = cv2.addWeighted(frame, 1.0, ruido[n % 6], 0.075, -0.075 * 128)          # grano
        for o in ov:                                                                    # titulos y sellos
            if o["t0"] <= t < o["t1"]:
                k = (o["tipo"], o.get("cab"), o["txt"])
                if k not in cache_ov: cache_ov[k] = (render_titulo(o["cab"], o["txt"]) if o["tipo"] == "titulo" else render_pie(o["txt"]) if o["tipo"] == "pie" else render_sello(o["txt"]))
                dt = min(t - o["t0"], o["t1"] - t)
                a = min(1.0, dt / 0.35)
                if o["tipo"] == "titulo": pegar(frame, cache_ov[k], 0, 70, a)
                elif o["tipo"] == "pie": pegar(frame, cache_ov[k], 48, H - 118, a)
                else:
                    sc = 1.0 + 0.35 * max(0.0, 1 - (t - o["t0"]) / 0.18)                # golpe de sello
                    img = cache_ov[k]
                    if sc != 1.0: img = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
                    pegar(frame, img, W - img.shape[1] - 50, 70, a)
        j = max(0, bisect.bisect_right(fr_t0, t) - 1)                                   # subtitulos
        f_ = fr[j]
        if not os.environ.get("SIN_SUBS") and f_[0]["t0"] - 0.05 <= t < f_[-1]["t1"] + 0.25:
            if j not in cache_sub:
                if len(cache_sub) > 40: cache_sub.pop(next(iter(cache_sub)))
                cache_sub[j] = render_subtitulo(f_)
            sub = cache_sub[j]
            pegar(frame, sub, (W - sub.shape[1]) // 2, H - 118, 1.0)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close(); ff.wait()
    return salida


def render(timeline, trabajo, t0, t1, nproc):
    from multiprocessing import Pool
    t0, t1, nproc = float(t0), float(t1), int(nproc)
    if not os.path.exists(os.path.join(trabajo, "timeline.json")):
        import shutil; shutil.copy(timeline, os.path.join(trabajo, "timeline.json"))
    corte = [t0 + (t1 - t0) * k / nproc for k in range(nproc + 1)]
    corte = [round(c * FPS) / FPS for c in corte]
    with Pool(nproc) as pool:
        for r in pool.imap_unordered(render_trozo, [(trabajo, corte[k], corte[k + 1], k, None) for k in range(nproc)]):
            print("listo", r, flush=True)


def unir(trabajo, mezcla, salida):
    partes = sorted(glob.glob(os.path.join(trabajo, "parte_*.mp4")))
    lista = os.path.join(trabajo, "lista.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-i", mezcla, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida], check=True)
    print("video:", salida, os.path.getsize(salida) // 1024 // 1024, "MB")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "preparar": preparar(sys.argv[2], sys.argv[3])
    elif cmd == "tableros": crear_tableros(sys.argv[2], sys.argv[3])
    elif cmd == "reales": preparar_reales(sys.argv[2], sys.argv[3])
    elif cmd == "plan": plan(sys.argv[2], sys.argv[3])
    elif cmd == "render": render(*sys.argv[2:7])
    elif cmd == "unir": unir(*sys.argv[2:5])
