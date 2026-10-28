#!/usr/bin/env python3
"""Busca en Wikimedia Commons fotos REALES de habitaciones y lugares (licencias libres, sin personas) para usar de fondo detras de los clips 3D.
Uso: python3 buscar_fondos_reales.py carpeta_salida   (escribe fondos_raw.json con titulo, autor, licencia y pagina para los creditos)"""
import json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "la_cosa_nuestra", "video"))
from buscar_imagenes import get, tiene_cara, API, OK_LIC
import cv2, numpy as np

MALO = re.compile(r"portrait|people|person|man |men |woman|women|girl|boy|child|crowd|police|soldier|band|concert|wedding|selfie|team|player|mayor|president|"
                  r"logo|map of|diagram|stamp|poster|painting|drawing|illustration|\bsvg\b|screenshot|album|film still|movie|protest|parade|dancing|party|students", re.I)
CONSULTAS = [("living room interior", "sala"), ("living room sofa television", "sala"), ("bedroom interior", "habitacion"), ("hotel room interior", "habitacion"),
             ("home office desk computer", "oficina_casa"), ("open plan office empty", "oficina"), ("kitchen interior", "cocina"),
             ("apartment window night city view", "ventana_noche"), ("suburban street night", "calle_noche"), ("city street night wet", "calle_noche"),
             ("electronics store shelves", "tienda"), ("supermarket aisle", "tienda"), ("warehouse interior shelves", "almacen"), ("factory assembly line", "fabrica"),
             ("server room data center", "datacenter"), ("control room monitors", "datacenter"), ("empty hallway", "pasillo"), ("garage interior workshop", "garaje"),
             ("basement room", "sotano"), ("rooftop city night", "azotea"), ("parking garage", "parking"), ("airport terminal", "aeropuerto"),
             ("train station platform", "estacion"), ("cafe interior", "cafe"), ("electronics workshop bench", "taller"), ("library interior", "biblioteca"),
             ("classroom empty", "aula"), ("subway station", "estacion"), ("shopping mall interior", "centro_comercial"), ("apartment building courtyard", "edificio"),
             ("highway night", "carretera"), ("cell tower field", "antena"), ("small town street dusk", "pueblo"), ("laboratory interior", "laboratorio"),
             ("computer lab", "laboratorio"), ("living room window curtains", "sala"), ("office desk lamp", "oficina_casa"), ("lobby interior", "lobby")]
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
ruta_json = os.path.join(out, "fondos_raw.json")
res = json.load(open(ruta_json)) if os.path.exists(ruta_json) else []
hechas = {r[5] for r in res}; vistos = {r[1] for r in res}
for q, cat in CONSULTAS:
    if q in hechas: continue
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 25,
         "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1920}
    try: d = get(API + "?" + urllib.parse.urlencode(p))
    except Exception as e: print("ERR", q, e, flush=True); time.sleep(8); continue
    n = 0
    for pg in sorted((d.get("query", {}).get("pages", {}) or {}).values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; t = pg["title"]; md = ii.get("extmetadata", {}); lic = md.get("LicenseShortName", {}).get("value", "")
        if not OK_LIC.match(lic) or MALO.search(t) or ii["width"] < 2400 or t in vistos or not t.lower().endswith((".jpg", ".jpeg")): continue
        try: data = get(ii.get("thumburl") or ii["url"], binary=True)
        except Exception: continue
        a = cv2.imdecode(np.frombuffer(data, np.uint8), 1)
        if a is None or tiene_cara(data): continue
        vistos.add(t); nm = f"{cat}_{len([r for r in res if r[6] == cat]) + 1:02d}.jpg"
        open(os.path.join(out, nm), "wb").write(data)
        res.append([nm, t, re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "?"))[:80], lic, ii["descriptionurl"], q, cat]); n += 1
        if n >= 3: break
        time.sleep(0.6)
    json.dump(res, open(ruta_json, "w"), ensure_ascii=False)
    print(q, n, "total", len(res), flush=True); time.sleep(1.5)
print("FIN", len(res))
