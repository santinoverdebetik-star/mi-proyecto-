#!/usr/bin/env python3
"""Genera audio con la API de Voizum (https://voizum.com/docs).

Uso:  VOIZUM_API_KEY=... python3 voizum_generar.py texto.txt VOICE_ID salida.mp3 [velocidad]
La clave se lee SOLO de la variable de entorno VOIZUM_API_KEY: no la escribas en archivos ni la subas al repo.
Cobra 60 creditos por 1.000 caracteres (minimo 100). El MP3 se guarda 4 dias en Voizum: descargalo.
"""
import json, os, sys, time, urllib.error, urllib.request

API = "https://voizum.com/api/v1"
KEY = os.environ["VOIZUM_API_KEY"]


class SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # no seguir solo: la clave no debe viajar al almacenamiento
        return None


def llamar(metodo, ruta, cuerpo=None):
    req = urllib.request.Request(API + ruta, method=metodo,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                                 data=json.dumps(cuerpo).encode() if cuerpo is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:300]}")


def descargar(job_id, destino):
    req = urllib.request.Request(f"{API}/tts/{job_id}/audio?download=1", headers={"Authorization": f"Bearer {KEY}"})
    try:
        urllib.request.build_opener(SinRedireccion).open(req, timeout=60)
        sys.exit("se esperaba una redireccion al MP3")
    except urllib.error.HTTPError as e:
        destino_url = e.headers.get("Location")
        if e.code not in (301, 302, 303, 307, 308) or not destino_url:
            sys.exit(f"HTTP {e.code} al pedir el audio")
    with urllib.request.urlopen(destino_url, timeout=120) as r, open(destino, "wb") as f:  # sin cabecera de clave
        f.write(r.read())


if __name__ == "__main__":
    texto = open(sys.argv[1], encoding="utf-8").read().strip()
    cuerpo = {"text": texto, "voice_id": sys.argv[2], "language": "es", "pause_ms": 350}
    if len(sys.argv) > 4:
        cuerpo["speed"] = float(sys.argv[4])
    job = llamar("POST", "/tts", cuerpo)
    print("creado:", job["job_id"], "creditos:", job["credits_charged"])
    while True:
        st = llamar("GET", f"/tts/{job['job_id']}")
        if st["status"] in ("done", "error", "canceled"):
            break
        time.sleep(3)
    print("estado:", st["status"], "duracion:", st.get("duration_seg"))
    if st["status"] == "done":
        descargar(job["job_id"], sys.argv[3])
        print("guardado:", sys.argv[3])
