#!/usr/bin/env python3
"""Genera las imágenes del video con el Webhook API de G-Labs Studio.

Se ejecuta EN TU PC (el servidor de G-Labs escucha en 127.0.0.1 de tu computadora):
  1. Abre G-Labs Studio -> pestaña Webhook -> Start (plan MAX).
  2. Pon la clave en una variable de entorno (no la escribas en archivos del repo):
       Windows (PowerShell):  $env:GLABS_API_KEY="tu_clave"
       macOS/Linux:           export GLABS_API_KEY="tu_clave"
  3. python generar_imagenes.py prompts.json --salida imagenes

prompts.json = lista de {"id": "012", "prompt": "...", "aspect": "16:9"}.
Es reanudable: salta las imágenes que ya existen en la carpeta de salida.
Solo usa la librería estándar de Python 3.8+.
"""
import argparse, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def llamar(base, clave, metodo, ruta, cuerpo=None, timeout=60):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(base + ruta, data=datos, method=metodo,
                                 headers={"X-API-Key": clave, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {"error": str(e)}

def generar(item, a):
    destino = os.path.join(a.salida, f"{item['id']}.png")
    if os.path.exists(destino):
        return item["id"], "ya existía"
    cuerpo = {"prompt": item["prompt"], "model": a.modelo, "aspect_ratio": item.get("aspect", a.aspecto)}
    if a.upscale:
        cuerpo["upscale"] = [a.upscale]
    ultimo = ""
    for intento in range(1, a.reintentos + 2):
        cod, r = llamar(a.url, a.clave, "POST", "/api/image/generate", cuerpo)
        if cod != 202:
            ultimo = f"{cod} {r.get('error', r)}"
            if cod in (400, 401, 403):          # error del prompt o de la clave: reintentar no ayuda
                break
            time.sleep(5)
            continue
        tid = r["task_id"]
        t0 = time.time()
        while time.time() - t0 < a.espera:
            time.sleep(4)
            cod, s = llamar(a.url, a.clave, "GET", f"/api/status/{tid}")
            if s.get("status") == "completed" and s.get("results"):
                # la URL de descarga trae el host del servidor; se reemplaza por el que usamos
                u = urlparse(s["results"][-1])
                with urllib.request.urlopen(a.url + u.path, timeout=120) as f, open(destino + ".tmp", "wb") as o:
                    o.write(f.read())
                os.replace(destino + ".tmp", destino)
                return item["id"], "ok"
            if s.get("status") == "failed":
                ultimo = f"{s.get('error_code')} {s.get('error')}"
                break
        else:
            ultimo = "tiempo de espera agotado"
    return item["id"], "FALLÓ: " + ultimo

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("prompts")
    p.add_argument("--salida", default="imagenes")
    p.add_argument("--url", default="http://127.0.0.1:8765")
    p.add_argument("--clave", default=os.environ.get("GLABS_API_KEY", ""))
    p.add_argument("--modelo", default="nano_banana_pro",
                   help="nano_banana_pro | nano_banana_2 | nano_banana_2_lite | nano_pics")
    p.add_argument("--aspecto", default="16:9")
    p.add_argument("--upscale", choices=["2K", "4K"], help="4K requiere cuenta ULTRA")
    p.add_argument("--hilos", type=int, default=4)
    p.add_argument("--reintentos", type=int, default=2)
    p.add_argument("--espera", type=int, default=600, help="segundos máx. por imagen")
    p.add_argument("--solo", help="ids separados por coma (para regenerar algunas)")
    a = p.parse_args()
    a.url = a.url.rstrip("/")
    if not a.clave:
        sys.exit("Falta la clave: define GLABS_API_KEY o usa --clave")
    items = json.load(open(a.prompts, encoding="utf-8"))
    if a.solo:
        ids = set(a.solo.split(","))
        items = [i for i in items if i["id"] in ids]
        for i in items:                           # regenerar = borrar la anterior
            f = os.path.join(a.salida, f"{i['id']}.png")
            if os.path.exists(f):
                os.remove(f)
    os.makedirs(a.salida, exist_ok=True)
    try:
        with urllib.request.urlopen(a.url + "/api/health", timeout=10) as r:
            print("Servidor G-Labs:", r.read().decode()[:200])
    except Exception as e:
        sys.exit(f"No llego a {a.url} ({e}). ¿Está abierta la app y pulsado Start en la pestaña Webhook?")
    fallos = 0
    with ThreadPoolExecutor(a.hilos) as ex:
        for n, (id_, estado) in enumerate(ex.map(lambda i: generar(i, a), items), 1):
            print(f"[{n}/{len(items)}] {id_}: {estado}", flush=True)
            fallos += estado.startswith("FALLÓ")
    print(f"Listo. {len(items) - fallos} imágenes, {fallos} fallos. Carpeta: {a.salida}")

if __name__ == "__main__":
    main()
