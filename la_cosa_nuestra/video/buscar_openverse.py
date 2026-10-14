#!/usr/bin/env python3
"""Completa la busqueda de imagenes con Openverse (licencias CC0 / dominio publico / CC BY, solo fotografias, sin caras).
Uso: python3 buscar_openverse.py CARPETA_SALIDA   (escribe creditos_openverse.csv en esa carpeta)"""
import csv, html, os, sys, time, urllib.parse
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buscar_imagenes import BAD_TITLE, TEMAS, get, tiene_cara

API = "https://api.openverse.org/v1/images/"
# consultas cortas y amplias (Openverse devuelve pocos resultados con frases largas)
QUERIES = [(q, t) for t, qs in TEMAS.items() for q in qs]


def main(out, por_consulta=4):
    os.makedirs(out, exist_ok=True)
    vistos, filas = set(), []
    for q, tag in QUERIES:
        p = {"q": q, "license": "cc0,pdm,by", "category": "photograph", "extension": "jpg",
             "page_size": "20", "mature": "false"}
        try:
            res = get(API + "?" + urllib.parse.urlencode(p)).get("results", [])
        except Exception as e:
            print("ERR", q, e, flush=True); continue
        n = 0
        for r in res:
            if n >= por_consulta:
                break
            u, tit = r.get("url"), r.get("title") or ""
            etiquetas = " ".join(t.get("name", "") for t in (r.get("tags") or []))
            if not u or u in vistos or BAD_TITLE.search(tit + " " + etiquetas):
                continue
            vistos.add(u)
            try:
                data = get(u, binary=True)
            except Exception:
                continue
            a = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if a is None or a.shape[1] < 1000 or a.shape[0] < 560 or not (1.3 <= a.shape[1] / a.shape[0] <= 2.3):
                continue
            if tiene_cara(data):
                continue
            nombre = f"ov_{tag}_{len([f for f in filas if f[0].startswith('ov_' + tag)]) + 1:02d}.jpg"
            open(os.path.join(out, nombre), "wb").write(data)
            fila = [nombre, html.unescape(tit)[:120], (r.get("creator") or "?")[:100],
                    f"{r.get('license', '').upper()} {r.get('license_version', '')}".strip(),
                    r.get("foreign_landing_url", ""), q]
            filas.append(fila)
            ruta = os.path.join(out, "creditos_openverse.csv")
            nuevo = not os.path.exists(ruta)
            with open(ruta, "a", newline="", encoding="utf-8") as fh:
                w_ = csv.writer(fh)
                if nuevo: w_.writerow(["archivo", "titulo", "autor", "licencia", "pagina", "consulta"])
                w_.writerow(fila)
            n += 1
            time.sleep(0.3)
        print(f"{q!r}: {n} (total {len(filas)})", flush=True)
        time.sleep(0.4)
    print("TOTAL", len(filas))


if __name__ == "__main__":
    main(sys.argv[1])
