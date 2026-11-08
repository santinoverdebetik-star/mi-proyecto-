#!/usr/bin/env python3
"""Render INCREMENTAL por escena: cada escena se renderiza una sola vez y se guarda en video/out/cache/ (clave = contenido de la escena + codigo de ese tipo de escena).
Si cambias solo unas escenas (o solo el audio) no se vuelve a renderizar lo demas. Si se corta, se vuelve a ejecutar y sigue donde quedo.
Uso: python3 render_incremental.py [props.json] [nombre] [escala]   ->  video/out/<nombre>.mp4"""
import hashlib, json, math, os, shutil, subprocess, sys, glob
AQUI = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(os.path.dirname(AQUI), "video")
props = sys.argv[1] if len(sys.argv) > 1 else "props_prueba4.json"; nombre = sys.argv[2] if len(sys.argv) > 2 else "prueba4"; esc = sys.argv[3] if len(sys.argv) > 3 else "0.5"
os.chdir(V); os.makedirs("out/cache", exist_ok=True)
env = dict(os.environ, CHROMIUM_PATH=os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"))
BASE = ["src/Capas.tsx", "src/estilo.ts"]
CODIGO = {"3d": ["src/escenas/Escena3D.tsx", "src/escenas/Objetos3D.tsx", "src/escenas/Objetos3D_b.tsx", "src/escenas/Realismo.tsx"], "foto": ["src/escenas/Foto.tsx"],
          "titular": ["src/escenas/Titular.tsx"], "blender": ["../blender/gen_clip.py"], "diagrama": ["src/escenas/Diagrama.tsx"], "imagen": ["src/escenas/Imagen.tsx"]}
GRADE = "grade-v1"
GRADE_FILTRO = ("[0:v]format=gbrp,split=3[a][b][c];[b]curves=all='0/0 0.5/0 0.75/0.5 1/1',gblur=sigma=10[glow];[a][glow]blend=all_mode=screen:all_opacity=0.5[bl];[c]gblur=sigma=4[blur];"
                "[1:v]format=gbrp[mask];[bl][blur][mask]maskedmerge,format=yuv420p,vignette=PI/5,eq=contrast=1.08:saturation=1.05:brightness=0.02:gamma=1.1[o]")
def codigo(tipo):
    h = hashlib.sha1(GRADE.encode())
    for f in BASE + CODIGO.get(tipo, ["src/escenas/Inserto.tsx"]) + glob.glob("public/fuentes/*"):
        if os.path.exists(f): h.update(open(f, "rb").read())
    return h.hexdigest()
cod = {}
d = json.load(open(props)); escenas = d["escenas"]; FPS = 30
HASTA = float(sys.argv[4]) if len(sys.argv) > 4 else None                         # prueba parcial: solo las escenas que empiezan antes de HASTA segundos
if HASTA:
    acum, n_ok = 0.0, 0
    for e in escenas:
        if acum >= HASTA: break
        acum += e["dur"]; n_ok += 1
    escenas = escenas[:n_ok]; d = dict(d, escenas=escenas); props_dur = acum
ini, f0 = [], 0
for e in escenas: n = round(e["dur"] * FPS); ini.append((f0, n)); f0 += n
def clave(e):
    c = cod.setdefault(e["tipo"], codigo(e["tipo"]))
    return hashlib.sha1((json.dumps(e, sort_keys=True) + c + esc).encode()).hexdigest()[:16]
SOLO = os.environ.get("SOLO", "")                                  # SOLO=blender -> solo los clips de Blender; SOLO=resto -> todo menos Blender (para repartir el trabajo)
faltan = [i for i, e in enumerate(escenas) if not os.path.exists(f"out/cache/{clave(e)}.mp4") and (SOLO != "blender" or e["tipo"] == "blender") and (SOLO != "resto" or e["tipo"] != "blender")]
print(f"{len(escenas)} escenas, {len(faltan)} por renderizar, {len(escenas) - len(faltan)} en cache", flush=True)
if faltan:
    if any(escenas[i]["tipo"] != "blender" for i in faltan): subprocess.run(["npx", "remotion", "bundle", "src/index.ts", "--out-dir=out/bundle", "--log=error"], check=True, env=env)
    for k, i in enumerate(faltan):
        a, n = ini[i]; destino = f"out/cache/{clave(escenas[i])}.mp4"
        if escenas[i]["tipo"] == "blender":                                 # clip fotorrealista: Blender (Cycles) a 10 fps -> mezcla a 30 fps + bloom, viñeta, grano y fundido
            e = escenas[i]; W, H = int(1920 * float(esc)), int(1080 * float(esc)); fr = int(math.ceil(e["dur"] * 10)) + 2; carp = f"out/bl/{clave(e)}"
            shutil.rmtree(carp, ignore_errors=True); os.makedirs(carp, exist_ok=True)
            json.dump({"props": e["props"], "seed": e["seed"], "paleta": e.get("paleta"), "frames": fr, "samples": int(os.environ.get("BL_SAMPLES", "14")), "bounces": 3, "adapt": 0.05, "clamp": 2, "res": [int(W * 2 / 3) // 2 * 2, int(H * 2 / 3) // 2 * 2], "salida": carp}, open(carp + "/spec.json", "w"))
            r = subprocess.run(["python3", "../blender/gen_clip.py", carp + "/spec.json"], env=dict(env, ASSETS=os.path.abspath("../blender/assets")), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode: sys.exit(f"fallo Blender en la escena {i}")
            fx = ["format=gbrp", "split[a][b]", "[b]curves=all='0/0 0.55/0 0.8/0.5 1/1',gblur=sigma=8[g]", "[a][g]blend=all_mode=screen:all_opacity=0.35", "format=yuv420p", "vignette=PI/5.5", "noise=alls=6:allf=t"]
            vf = "framerate=fps=30:interp_start=0:interp_end=255:scene=100,tpad=stop_mode=clone:stop=10,scale=%d:%d:flags=lanczos,format=gbrp,split[a][b];[b]curves=all='0/0 0.55/0 0.8/0.5 1/1',gblur=sigma=8[g];[a][g]blend=all_mode=screen:all_opacity=0.35,format=yuv420p,vignette=PI/5.5,noise=alls=6:allf=t" % (W, H)
            if e.get("trans") == "fundido": vf += f",fade=t=in:st=0:d=0.45,fade=t=out:st={max(0, n / 30 - 0.4):.2f}:d=0.4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "10", "-i", carp + "/f_%04d.png", "-vf", vf, "-frames:v", str(n), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30", destino + ".tmp.mp4"], check=True)
            os.replace(destino + ".tmp.mp4", destino); print(f"escena {i} (blender:{"+".join(e['props'])}) lista [{k + 1}/{len(faltan)}]", flush=True); continue
        rf = int(escenas[i].get("rf", 1))
        pr, fr = props, f"{a}-{a + n - 1}"
        if rf > 1:                                                       # --every-nth-frame se cuelga si el rango no empieza en 0: se renderiza la escena sola (fotogramas 0..n-1)
            pr = f"out/una_{clave(escenas[i])}.json"; json.dump({"escenas": [escenas[i]]}, open(pr, "w")); fr = f"0-{n - 1}"
        cmd = ["npx", "remotion", "render", "out/bundle", "Historia", destino + ".tmp.mp4", f"--props={pr}", f"--scale={esc}", "--concurrency=4", "--crf=22",
               f"--frames={fr}", "--muted", "--log=error"] + ([f"--every-nth-frame={rf}"] if rf > 1 else [])
        for intento in range(3):                                         # vigilante: si un render se cuelga (pasó tras reiniciar el contenedor) se corta y se reintenta
            try:
                r = subprocess.run(cmd, env=env, timeout=240 + n * 4 / rf); break
            except subprocess.TimeoutExpired:
                print(f"escena {i}: render colgado, reintento {intento + 1}", flush=True)
                subprocess.run(["pkill", "-x", "headless_shell."]); subprocess.run(["pkill", "-f", "remotion render"])
        else: sys.exit(f"fallo en la escena {i}")
        if r.returncode: sys.exit(f"fallo en la escena {i}")
        if rf > 1:                                                     # se renderizo a 30/rf fps: se mezcla (blend) hasta 30 fps con exactamente n fotogramas
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", destino + ".tmp.mp4", "-vf", "framerate=fps=30:interp_start=0:interp_end=255:scene=100,tpad=stop_mode=clone:stop=8",
                            "-frames:v", str(n), "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", destino + ".tmp2.mp4"], check=True)
            os.replace(destino + ".tmp2.mp4", destino + ".tmp.mp4")
        if escenas[i]["tipo"] == "3d":                                    # etapa de postproduccion: resplandor (bloom), profundidad de campo tipo tilt-shift y vineta
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", destino + ".tmp.mp4", "-loop", "1", "-framerate", "30", "-i", "public/mascara_dof.png", "-filter_complex", GRADE_FILTRO,
                            "-map", "[o]", "-frames:v", str(n), "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", destino + ".tmp3.mp4"], check=True)
            os.replace(destino + ".tmp3.mp4", destino + ".tmp.mp4")
        os.replace(destino + ".tmp.mp4", destino); print(f"escena {i} ({escenas[i]['tipo']}) lista [{k + 1}/{len(faltan)}]", flush=True)
lista = "out/lista_" + nombre + ".txt"
open(lista, "w").write("".join(f"file 'cache/{clave(e)}.mp4'\n" for e in escenas))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-preset", "veryfast", f"out/{nombre}_mudo.mp4"], check=True)
audio = "public/" + d.get("voz", "")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"out/{nombre}_mudo.mp4", "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", f"out/{nombre}.mp4"], check=True)
print(f"LISTO out/{nombre}.mp4", flush=True)
