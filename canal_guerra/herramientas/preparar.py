#!/usr/bin/env python3
"""Lee canal_guerra/guion/*.txt y genera, en canal_guerra/build/:
  escenas.json   -> datos para Remotion (id, cap, tipo, voz, overlays, imagen...)
  prompts.json   -> para generar_imagenes.py (estilo + descripciones de personajes ya aplicados)
  voz/<cap>.txt  -> texto de cada bloque de voz (para generar_voz.py / Voizum)
  guion.md       -> guion legible con duración estimada
Duración estimada = palabras / 2.72 por segundo (≈163 palabras/min, ritmo medido con la voz elegida).
"""
import json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
GUION = os.path.join(RAIZ, "guion")
BUILD = os.path.join(RAIZ, "build")
PPS = 163 / 60

PERSONAJES = {
    "{PULLER_J}": "a lean young white American Marine officer in his twenties, short dark hair, square jaw, khaki field uniform and campaign hat",
    "{PULLER_M}": "a stocky American Marine colonel in his forties, thick neck, bulldog jaw, steel-gray eyes, weathered face, Marine field uniform",
}
BASE = ("photorealistic cinematic film still, shot on 35mm, muted desaturated sepia-olive color grade, soft volumetric haze, "
        "subtle film grain, period-accurate uniforms and equipment, no text, no watermark, no logos, no gore")
ESTILO = {
    "ia": BASE,
    "retrato": BASE + ", portrait composition",
    "bn": "authentic-looking black-and-white archival photograph, 1940s press-photo style, grain, light scratches and vignette, no text, no gore",
    "mapa": ("antique stylized relief map seen in perspective, shaded terrain and mountains, muted parchment and olive-green tones "
             "(white-blue tones for snow), clean vacant areas for overlays, absolutely no text, no labels, no lettering, no gore"),
    "medallas": BASE + ", still life, macro lens",
}
SIN_IMAGEN = {"frase", "barras", "linea", "anio_solo"}

def parsear():
    escenas, cap, cur = [], "", None
    for f in sorted(os.listdir(GUION)):
        if not f.endswith(".txt"):
            continue
        for linea in open(os.path.join(GUION, f), encoding="utf-8"):
            linea = linea.rstrip("\n")
            if linea.startswith("# CAP"):
                cap = linea[2:].strip()
            elif linea.startswith("#") and not linea.startswith("# "):
                partes = linea[1:].split()
                cur = {"id": partes[0], "cap": cap, "tipo": partes[1], "opts": dict(p.split("=", 1) for p in partes[2:] if "=" in p),
                       "voz": "", "prompt": "", "mapa": "", "ov": ""}
                escenas.append(cur)
            elif cur and re.match(r"^[VPMO]: ", linea):
                clave = {"V": "voz", "P": "prompt", "M": "mapa", "O": "ov"}[linea[0]]
                cur[clave] = linea[3:].strip()
    return escenas

def construir(escenas):
    ids = {e["id"] for e in escenas}
    t = 0.0
    for e in escenas:
        e["palabras"] = len(e["voz"].split())
        e["dur"] = round(e["palabras"] / PPS + 0.35, 2)      # 0,35 s de respiro entre planos
        e["inicio"] = round(t, 2)
        t += e["dur"]
        p = e["prompt"]
        e["reusa"] = p[1:] if p.startswith("=") else ""
        if e["reusa"] and e["reusa"] not in ids:
            sys.exit(f"{e['id']}: reusa un id que no existe ({e['reusa']})")
        e["imagen"] = (e["reusa"] or e["id"]) if e["tipo"] in ESTILO and p else ""
        e["overlays"] = [dict(zip(("k", "v"), o.strip().split("=", 1))) for o in e["ov"].split(";") if "=" in o]
    return escenas, t

def main():
    esc, total = construir(parsear())
    os.makedirs(os.path.join(BUILD, "voz"), exist_ok=True)
    json.dump(esc, open(os.path.join(BUILD, "escenas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    pr = []
    for e in esc:
        if e["prompt"] and not e["reusa"] and e["tipo"] in ESTILO:
            txt = e["prompt"]
            for k, v in PERSONAJES.items():
                txt = txt.replace(k, v)
            if e["tipo"] == "mapa" and e["mapa"]:
                txt += ". Composition keeps clear space for later markers: " + e["mapa"].split(";")[0].replace("bandera", "marker")
            pr.append({"id": e["id"], "prompt": f"{txt}. {ESTILO[e['tipo']]}", "aspect": "16:9"})
    json.dump(pr, open(os.path.join(BUILD, "prompts.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    caps = {}
    for e in esc:
        caps.setdefault(e["cap"], []).append(e)
    md = ["# Guion — Los 4 movimientos tácticos legendarios de Chesty Puller\n"]
    for i, (c, es) in enumerate(caps.items()):
        txt = "\n\n".join(x["voz"] for x in es)
        open(os.path.join(BUILD, "voz", f"{i:02d}.txt"), "w", encoding="utf-8").write(txt)
        w = sum(x["palabras"] for x in es)
        md.append(f"\n## {c}  ·  {w} palabras  ·  ≈ {w/PPS/60:.1f} min\n")
        for x in es:
            md.append(f"**{x['id']}** *({x['tipo']})* — {x['voz']}\n")
    open(os.path.join(BUILD, "guion.md"), "w", encoding="utf-8").write("\n".join(md))
    pal = sum(e["palabras"] for e in esc)
    print(f"{len(esc)} planos · {pal} palabras · duración estimada {total/60:.1f} min · imágenes nuevas {len(pr)} (reutilizadas {sum(1 for e in esc if e['reusa'])})")
    for c, es in caps.items():
        print(f"  {c[:48]:50s} {sum(x['palabras'] for x in es):5d} pal  {sum(x['dur'] for x in es)/60:5.1f} min  {len(es):3d} planos")

if __name__ == "__main__":
    main()
