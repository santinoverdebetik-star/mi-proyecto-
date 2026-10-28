#!/usr/bin/env python3
"""Render INCREMENTAL por escena: cada escena se renderiza una sola vez y se guarda en video/out/cache/ (clave = contenido de la escena + codigo de ese tipo de escena).
Si cambias solo unas escenas (o solo el audio) no se vuelve a renderizar lo demas. Si se corta, se vuelve a ejecutar y sigue donde quedo.
Uso: python3 render_incremental.py [props.json] [nombre] [escala]   ->  video/out/<nombre>.mp4"""
import hashlib, json, os, subprocess, sys, glob
AQUI = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(os.path.dirname(AQUI), "video")
props = sys.argv[1] if len(sys.argv) > 1 else "props_prueba4.json"; nombre = sys.argv[2] if len(sys.argv) > 2 else "prueba4"; esc = sys.argv[3] if len(sys.argv) > 3 else "0.5"
os.chdir(V); os.makedirs("out/cache", exist_ok=True)
env = dict(os.environ, CHROMIUM_PATH=os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"))
BASE = ["src/Capas.tsx", "src/estilo.ts"]
CODIGO = {"3d": ["src/escenas/Escena3D.tsx", "src/escenas/Objetos3D.tsx", "src/escenas/Objetos3D_b.tsx", "src/escenas/Realismo.tsx"], "foto": ["src/escenas/Foto.tsx"],
          "titular": ["src/escenas/Titular.tsx"], "diagrama": ["src/escenas/Diagrama.tsx"], "imagen": ["src/escenas/Imagen.tsx"]}
def codigo(tipo):
    h = hashlib.sha1()
    for f in BASE + CODIGO.get(tipo, ["src/escenas/Inserto.tsx"]) + glob.glob("public/fuentes/*"):
        if os.path.exists(f): h.update(open(f, "rb").read())
    return h.hexdigest()
cod = {}
d = json.load(open(props)); escenas = d["escenas"]; FPS = 30
ini, f0 = [], 0
for e in escenas: n = round(e["dur"] * FPS); ini.append((f0, n)); f0 += n
def clave(e):
    c = cod.setdefault(e["tipo"], codigo(e["tipo"]))
    return hashlib.sha1((json.dumps(e, sort_keys=True) + c + esc).encode()).hexdigest()[:16]
faltan = [i for i, e in enumerate(escenas) if not os.path.exists(f"out/cache/{clave(e)}.mp4")]
print(f"{len(escenas)} escenas, {len(faltan)} por renderizar, {len(escenas) - len(faltan)} en cache", flush=True)
if faltan:
    subprocess.run(["npx", "remotion", "bundle", "src/index.ts", "--out-dir=out/bundle", "--log=error"], check=True, env=env)
    for k, i in enumerate(faltan):
        a, n = ini[i]; destino = f"out/cache/{clave(escenas[i])}.mp4"
        r = subprocess.run(["npx", "remotion", "render", "out/bundle", "Historia", destino + ".tmp.mp4", f"--props={props}", f"--scale={esc}", "--concurrency=4", "--crf=22",
                            f"--frames={a}-{a + n - 1}", "--muted", "--log=error"], env=env)
        if r.returncode: sys.exit(f"fallo en la escena {i}")
        os.replace(destino + ".tmp.mp4", destino); print(f"escena {i} ({escenas[i]['tipo']}) lista [{k + 1}/{len(faltan)}]", flush=True)
lista = "out/lista_" + nombre + ".txt"
open(lista, "w").write("".join(f"file 'cache/{clave(e)}.mp4'\n" for e in escenas))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", f"out/{nombre}_mudo.mp4"], check=True)
audio = "public/" + d.get("voz", "")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"out/{nombre}_mudo.mp4", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"out/{nombre}.mp4"], check=True)
print(f"LISTO out/{nombre}.mp4", flush=True)
