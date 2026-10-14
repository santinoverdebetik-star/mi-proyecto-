#!/usr/bin/env python3
"""Recorre categorias de Wikimedia Commons y descarga fotos de lugares/objetos (sin caras, licencia libre, tono oscuro).
Uso: python3 buscar_categorias.py CARPETA_SALIDA   (anade filas a CARPETA_SALIDA/creditos.csv)"""
import csv, html, os, random, re, sys, time, urllib.parse
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buscar_imagenes import API, BAD_TITLE, OK_LIC, get, tiene_cara

CATS = [
 ("Night photographs of New Jersey", "G01"), ("Streets in New Jersey", "G01"), ("Roads in New Jersey", "G03"),
 ("New Jersey Turnpike", "C03"), ("Night photographs of New York City", "G30"), ("Night photographs of Brooklyn", "G18"),
 ("Rain in New York City", "G02"), ("Fog in New York City", "G18"), ("Diners in New Jersey", "G05"),
 ("Diners in the United States", "G05"), ("Restaurants in New Jersey", "G04"), ("Steakhouses in the United States", "G35"),
 ("Cemeteries in New Jersey", "G22"), ("Piers in New Jersey", "G23"), ("Piers in New York City", "G23"),
 ("Courthouses in New Jersey", "G15"), ("Courtrooms", "G15"), ("Church interiors in the United States", "G21"),
 ("Industrial buildings in New Jersey", "G07"), ("Port Newark-Elizabeth Marine Terminal", "G07"),
 ("Manhattan skyline", "G40"), ("Lakes of New Jersey", "R11"), ("Log cabins in the United States", "G24"),
 ("Forest roads", "G20"), ("Railroad tracks in New Jersey", "G39"), ("Neon signs in the United States", "G30"),
 ("Motels in the United States", "R4"), ("Telephones", "G12"), ("Rotary dial telephones", "G12"),
 ("Typewriters", "G17"), ("Candles", "C07"), ("Votive candles", "R9"), ("Barbed wire", "G08"),
 ("Chain-link fences", "G08"), ("Butcher shops", "G09"), ("Barbershops", "G38"), ("Hospital corridors", "G10"),
 ("Palermo", "G28"), ("Landscapes of Sicily", "G29"), ("Farmhouses in Italy", "H01"), ("Sonoran Desert", "R5"),
 ("Adobe buildings in Arizona", "R5"), ("Prisons in the United States", "R17"), ("Briefcases", "G27"),
 ("Keys", "G32"), ("Cigars", "G13"), ("Ashtrays", "G13"), ("Parking lots", "G06"), ("Highway overpasses", "G19"),
 ("Cranes at ports", "G07"), ("Suburban houses in the United States", "G11"), ("Barbecue grills", "G11"),
 ("Strip malls in the United States", "G06"), ("Snow in New Jersey", "G37"), ("Old Navy? no", "G37"),
 ("Empty roads at night", "G03"), ("Streets at night", "G30"), ("Empty chairs", "C06"), ("Balance scales", "C01"),
 ("Cash registers", "G14"), ("Banknotes of the United States", "G14"), ("Airports at night", "G34"),
 ("Warehouses", "G31"), ("Loading docks", "G31"), ("Hudson River", "G40"), ("Sunrise in New Jersey", "C03"),
 ("Fog", "C05"), ("Roads in fog", "C05"), ("Wooden piers", "G23"), ("Basements", "R9"), ("Staircases", "R9"),
 ("Hotel rooms", "R19"), ("Wedding rings", "R19"), ("Binoculars", "R19"), ("Phone booths", "R13"),
 ("Courthouse steps", "R16"), ("Gavels", "R16"), ("Boardrooms", "R10"), ("Conference rooms", "R10"),
]

def miembros(cat, limite=160):
    out, cont = [], None
    while len(out) < limite:
        p = {"action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": "Category:" + cat,
             "gcmtype": "file", "gcmlimit": "50", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1920"}
        if cont: p.update(cont)
        d = get(API + "?" + urllib.parse.urlencode(p))
        out += [(pg["title"], (pg.get("imageinfo") or [{}])[0]) for pg in d.get("query", {}).get("pages", {}).values()]
        cont = d.get("continue")
        if not cont: break
        time.sleep(1.0)
    return out

def main(out, por_cat=4):
    os.makedirs(out, exist_ok=True); ruta = os.path.join(out, "creditos.csv")
    vistos = set(r[1] for r in csv.reader(open(ruta, encoding="utf-8"))) if os.path.exists(ruta) else set()
    total = 0; random.seed(11)
    for cat, tag in CATS:
        try: cand = miembros(cat)
        except Exception as e: print("ERR", cat, e, flush=True); continue
        random.shuffle(cand); n = 0
        for titulo, ii in cand:
            if n >= por_cat: break
            if titulo in vistos or not ii or ii.get("mime") != "image/jpeg": continue
            w, h = ii.get("width", 0), ii.get("height", 0)
            if w < 1600 or h < 900 or not (1.3 <= w / h <= 2.3): continue
            em = ii.get("extmetadata", {}); lic = em.get("LicenseShortName", {}).get("value", "")
            if not OK_LIC.match(lic) or BAD_TITLE.search(titulo + " " + em.get("ImageDescription", {}).get("value", "")[:200]): continue
            vistos.add(titulo)
            try: data = get(ii["thumburl"], binary=True)
            except Exception: continue
            a = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
            if a is None or not (0.06 <= a.mean() / 255 <= 0.58): continue          # tono oscuro / sobrio
            if tiene_cara(data): continue
            k = 1
            while os.path.exists(os.path.join(out, f"{tag}_{k:02d}.jpg")): k += 1
            nombre = f"{tag}_{k:02d}.jpg"; open(os.path.join(out, nombre), "wb").write(data)
            autor = re.sub(r"<[^>]+>", "", html.unescape(em.get("Artist", {}).get("value", "?")))[:120]
            nuevo = not os.path.exists(ruta)
            with open(ruta, "a", newline="", encoding="utf-8") as fh:
                wr = csv.writer(fh)
                if nuevo: wr.writerow(["archivo", "titulo", "autor", "licencia", "pagina", "consulta"])
                wr.writerow([nombre, titulo, autor, lic, ii.get("descriptionurl", ""), "Category:" + cat])
            n += 1; total += 1; time.sleep(1.0)
        print(f"{cat!r}: {n} (total {total})", flush=True); time.sleep(1.0)
    print("TOTAL", total)

if __name__ == "__main__":
    main(sys.argv[1])
