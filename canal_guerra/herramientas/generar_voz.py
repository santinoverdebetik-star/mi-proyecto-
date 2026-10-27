#!/usr/bin/env python3
"""Genera la narración con la API de Voizum, un MP3 por bloque de build/voz/NN.txt.
Clave: variable VOIZUM_API_KEY o --clave-archivo (archivo FUERA del repo). Nunca se guarda en el repo.
Reanudable: salta los bloques cuyo MP3 ya existe. Los MP3 de Voizum caducan a los 4 días: descárgalos y guárdalos.
"""
import argparse, glob, json, os, sys, time, urllib.request, urllib.error
BASE = "https://voizum.com/api/v1"
VOZ_SALVATORE = "c9ee4c92-a6dc-4e2d-8a53-2a04e990658f"

def api(clave, metodo, ruta, cuerpo=None, binario=False):
    req = urllib.request.Request(BASE + ruta, method=metodo,
                                 data=json.dumps(cuerpo).encode() if cuerpo is not None else None,
                                 headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = r.read()
            return r.status, (d if binario else json.loads(d or b"{}"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--entrada", default=os.path.join(os.path.dirname(__file__), "..", "build", "voz"))
    p.add_argument("--voz", default=VOZ_SALVATORE)
    p.add_argument("--clave-archivo")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--pause-ms", type=int, default=None)
    a = p.parse_args()
    clave = os.environ.get("VOIZUM_API_KEY") or (open(a.clave_archivo).read().strip() if a.clave_archivo else "")
    if not clave:
        sys.exit("Falta la clave (VOIZUM_API_KEY o --clave-archivo)")
    cod, cuenta = api(clave, "GET", "/account")
    if cod != 200:
        sys.exit(f"Clave rechazada: {cuenta}")
    txts = sorted(glob.glob(os.path.join(a.entrada, "*.txt")))
    necesarios = sum(max(100, round(len(open(t, encoding='utf-8').read()) * 0.06)) for t in txts
                     if not os.path.exists(t[:-4] + ".mp3"))
    print(f"Créditos: {cuenta['credits_remaining']} · necesarios ≈ {necesarios}")
    if necesarios > cuenta["credits_remaining"]:
        sys.exit("Créditos insuficientes")
    jobs = {}
    for t in txts:
        mp3 = t[:-4] + ".mp3"
        if os.path.exists(mp3):
            print(os.path.basename(mp3), "ya existe"); continue
        cuerpo = {"text": open(t, encoding="utf-8").read().strip(), "voice_id": a.voz, "language": "es",
                  "loudness_normalization": True, "speed": a.speed}
        if a.pause_ms is not None:
            cuerpo["pause_ms"] = a.pause_ms
        cod, r = api(clave, "POST", "/tts", cuerpo)
        if cod not in (200, 201, 202):
            sys.exit(f"{t}: {cod} {r}")
        jobs[r["job_id"]] = mp3
        print(os.path.basename(t), "->", r["job_id"], r.get("credits_charged"), "créditos")
        time.sleep(4)                               # límite: 20 creaciones por minuto
    while jobs:
        time.sleep(5)
        for j, mp3 in list(jobs.items()):
            cod, s = api(clave, "GET", f"/tts/{j}")
            if s.get("status") == "done":
                cod, d = api(clave, "GET", f"/tts/{j}/audio?download=1", binario=True)
                open(mp3, "wb").write(d); print("listo", os.path.basename(mp3), len(d) // 1024, "KB"); del jobs[j]
            elif s.get("status") in ("error", "canceled"):
                sys.exit(f"{mp3}: {s}")
if __name__ == "__main__":
    main()
