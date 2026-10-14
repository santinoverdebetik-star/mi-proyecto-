#!/usr/bin/env python3
"""Descarga fotos historicas REALES de la mafia desde Wikimedia Commons (dominio publico / CC BY-SA) para el video.
Uso: python3 buscar_reales.py CARPETA   -> CARPETA/<clave>.jpg y CARPETA/reales.json (pie de foto, licencia, pagina)"""
import json, os, re, sys, time, html, urllib.parse, urllib.request
UA = {"User-Agent": "LaCosaNuestraDraft/1.0 (video draft; images from Wikimedia Commons)"}
API = "https://commons.wikimedia.org/w/api.php"
# clave, consulta, texto que debe tener el titulo del archivo, indice de resultado (si hay varios iguales), pie de foto
REALES = [
    ("luciano", "Lucky Luciano mugshot 1931", "mugshot 1931.jpg", 0, "Lucky Luciano · ficha policial, 1931"),
    ("valachi1", "Valachi Senate hearing 1963", "Valachi", 0, "Joseph Valachi declara ante el Senado de EE. UU., 1963"),
    ("valachi2", "Valachi Senate hearing 1963", "Valachi", 2, "Joseph Valachi, 1963"),
    ("castellano", "Paul Castellano", "Paul Castellano GX.jpg", 0, "Paul Castellano"),
    ("gotti", "John Gotti FBI mugshot", "JohnGottiFBIFullMugshot", 0, "John Gotti · ficha del FBI"),
    ("gigante", "Vincent Gigante mugshot 1960", "mugshot, 1960", 0, "Vincent Gigante · ficha policial, 1960"),
    ("gravano", "Sammy Gravano arrest photo 1990", "Sammy Gravano (arrest photo", 0, "Sammy Gravano · foto de arresto, 1990"),
    ("pistone", "Joseph Pistone FBI", "JosephPistone.jpg", 0, "Joseph Pistone, agente del FBI (\"Donnie Brasco\")"),
    ("decavalcante", "DeCavalcante July 1969", "DeCavalcanteJuly1969", 0, "Sam DeCavalcante, 1969"),
    ("sparks", "Sparks Steak House Manhattan", "Sparks Steak House (Manhattan, New York) 002.jpg", 0, "Sparks Steak House, Manhattan"),
]
def get(u, binary=False):
    for i in range(5):
        try:
            d = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
            return d if binary else json.loads(d)
        except Exception:
            time.sleep(4 * (i + 1))
    raise RuntimeError("sin respuesta: " + u[:80])
def main(out):
    os.makedirs(out, exist_ok=True)
    ruta_meta = os.path.join(out, "reales.json")
    meta = json.load(open(ruta_meta, encoding="utf-8")) if os.path.exists(ruta_meta) else {}
    for clave, q, sub, idx, pie in REALES:
        if clave in meta and os.path.exists(os.path.join(out, clave + ".jpg")): continue
        try: _uno(out, meta, clave, q, sub, idx, pie)
        except Exception as e: print("FALLO", clave, str(e)[:60], flush=True)
        json.dump(meta, open(ruta_meta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def _uno(out, meta, clave, q, sub, idx, pie):
    if True:
        p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": "6",
             "gsrlimit": "10", "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "1800"}
        pgs = sorted(get(API + "?" + urllib.parse.urlencode(p)).get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99))
        ok = [pg for pg in pgs if sub.lower() in pg["title"].lower()]
        if len(ok) <= idx: print("NO ENCONTRADA", clave); return
        pg = ok[idx]; ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {}); lic = em.get("LicenseShortName", {}).get("value", "?")
        data = get(ii["thumburl"], binary=True); open(os.path.join(out, clave + ".jpg"), "wb").write(data)
        autor = re.sub(r"<[^>]+>", "", html.unescape(em.get("Artist", {}).get("value", "?")))[:100]
        meta[clave] = {"pie": pie, "titulo": pg["title"], "licencia": lic, "autor": autor, "pagina": ii.get("descriptionurl", ""), "ancho": ii["width"], "alto": ii["height"]}
        print(f"{clave}: {pg['title'][5:60]} | {lic} | {ii['width']}x{ii['height']}", flush=True); time.sleep(2.5)
if __name__ == "__main__":
    main(sys.argv[1])
