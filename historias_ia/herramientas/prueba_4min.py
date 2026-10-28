#!/usr/bin/env python3
"""Arma la PRUEBA DE ~4 MINUTOS de 'Los virus de IA ya casi estan aqui' de punta a punta:
  1) toma las primeras escenas del guion (../GUION_VIRUS_IA.md) hasta ~4 min,
  2) genera la voz con Voizum (UN solo trabajo; no se cobran minimos por frase),
  3) alinea la voz con el texto (faster-whisper) para saber cuando empieza cada linea,
  4) escribe los props de Remotion con la duracion exacta de cada escena,
  5) mezcla voz + musica oscura + transiciones glitch + golpes.
Uso:
  export VOIZUM_API_KEY=...        # NUNCA en archivos
  python3 prueba_4min.py --listar-voces                  # muestra las voces cuyo nombre contiene 'martin'
  python3 prueba_4min.py --voz-id ID_DE_MARTIN [--lineas 52]
  python3 prueba_4min.py --audio voz_existente.mp3       # salta Voizum (p. ej. para probar el flujo con otra voz)
Despues:  cd ../video && CHROMIUM_PATH=... npx remotion render src/index.ts Historia out/prueba4.mp4 --props=props_prueba4.json --scale=0.5 --concurrency=4"""
import argparse, difflib, json, os, re, subprocess, sys, time, unicodedata, urllib.error, urllib.request
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_muestra as am  # noqa: E402

RAIZ = os.path.dirname(AQUI)
API = "https://voizum.com/api/v1"
FPS = 30


# ---------------------------------------------------------------- guion -> bloques
def leer_bloques(n_lineas):
    s = open(os.path.join(RAIZ, "GUION_VIRUS_IA.md"), encoding="utf-8").read().split("# VERIFICACIÓN DE HECHOS")[0]
    bloques, tag, lineas, total = [], None, [], 0
    for l in s.split("\n"):
        t = l.strip()
        m = re.match(r"<!--\s*(.*?)\s*-->", t)
        if m:
            if lineas: bloques.append((tag, lineas)); lineas = []
            tag = m.group(1); continue
        if not t or t.startswith("#") or t == "---" or t.startswith(("Voz:", "Las líneas", "Guion **")): continue
        if total >= n_lineas: break
        lineas.append(t); total += 1
    if lineas: bloques.append((tag, lineas))
    return [b for b in bloques if b[1]]


PROHIBIDOS = {"ojo", "nucleo"}                    # el usuario no los quiere NUNCA (pedido V5): se sustituyen
ALIAS = {"laptop": "contagio", "pantalla": "pantalla_rota", "ojo": "camara", "nucleo": "placa"}
TODOS_3D = ["globo", "cable", "codigo", "sala", "estanteria", "avalancha", "casas_red", "fabrica", "candado", "apagon", "intrusion", "contagio", "caja_led",
            "caja_tv", "red", "manometro", "radar", "duplicacion", "rack", "cajas15", "puerta", "pantalla_rota", "router", "camara", "movil", "pc_antiguo", "reloj",
            "calendario", "placa", "llave", "dominos", "escudo", "dinero", "hdmi", "password", "engranajes", "latido", "paquetes", "antena", "lupa", "mando", "nube",
            "tv_play"]
FAMILIA = {"candado_agujero": "candado"}          # candado y candado_agujero cuentan como el mismo clip
MAX_USOS = 1                                      # REGLA DEL USUARIO (para todos los videos): ningun clip 3D se repite
MAX_CLIP = 5.0                                    # pedido del usuario: clips 3D ~2 s mas cortos (antes 7 s)
OBJ_CATS = {  # objeto 3D -> tipos de lugar real donde tiene sentido verlo (el primero es el preferido)
    "sala": ["sala"], "caja_tv": ["sala"], "caja_led": ["sala", "oficina_casa"], "reloj": ["sala", "oficina_casa"], "ojo": ["pasillo", "lobby"],
    "intrusion": ["oficina_casa", "sala"], "contagio": ["oficina_casa", "biblioteca"], "dominos": ["aula", "biblioteca"], "nucleo": ["datacenter", "pasillo"],
    "engranajes": ["fabrica"], "placa": ["fabrica", "datacenter"], "manometro": ["fabrica", "pasillo"], "lupa": ["biblioteca", "aula"], "escudo": ["lobby", "estacion"],
    "globo": ["aula", "biblioteca"], "calendario": ["oficina_casa", "aula"], "casas_red": ["ventana_noche", "calle_noche"], "antena": ["ventana_noche", "calle_noche"],
    "cable": ["oficina_casa", "datacenter"], "estanteria": ["tienda"], "hdmi": ["sala"], "tv_play": ["sala", "cafe"], "nube": ["ventana_noche", "aeropuerto"],
    "fabrica": ["fabrica"], "paquetes": ["datacenter", "centro_comercial"], "dinero": ["tienda", "cafe"], "codigo": ["oficina_casa", "datacenter"],
    "avalancha": ["datacenter", "centro_comercial"], "password": ["oficina_casa", "sala"], "candado": ["pasillo", "calle_noche"], "candado_agujero": ["pasillo"],
    "puerta": ["pasillo", "lobby"], "apagon": ["centro_comercial", "estacion"], "latido": ["pasillo", "sala"], "red": ["ventana_noche", "calle_noche"],
    "radar": ["ventana_noche", "aeropuerto"], "duplicacion": ["aula", "biblioteca"], "rack": ["datacenter"], "cajas15": ["tienda", "fabrica"],
    "pantalla_rota": ["pasillo", "estacion"], "router": ["sala", "pasillo"], "camara": ["calle_noche", "lobby", "estacion"], "movil": ["cafe", "sala"],
    "pc_antiguo": ["biblioteca", "aula"], "llave": ["pasillo", "lobby"], "mando": ["sala"],
}
# objeto 3D -> categorias de FOTO real de ese objeto (public/fotos/fotos.json); si no hay, se usan lugares (OBJ_CATS) y por ultimo cualquiera
FOTO_PREF = {
    "router": ["router"], "camara": ["camara"], "movil": ["movil"], "pc_antiguo": ["laptop", "teclado"], "placa": ["placa"], "cable": ["cable", "fibra"],
    "hdmi": ["hdmi"], "mando": ["mando"], "globo": ["globo"], "lupa": ["lupa"], "calendario": ["calendario"], "antena": ["antena"], "usb": ["usb"],
    "rack": ["datacenter", "disco"], "nucleo": ["placa", "disco"], "paquetes": ["datacenter", "fibra"], "avalancha": ["datacenter"], "codigo": ["teclado", "laptop"],
    "contagio": ["laptop", "teclado"], "intrusion": ["laptop", "teclado"], "caja_tv": ["caja_tv", "tv_sala"], "caja_led": ["caja_tv", "tv_sala"],
    "tv_play": ["tv_sala", "tv_vieja"], "candado": ["candado"], "candado_agujero": ["candado"], "llave": ["llave", "candado"], "password": ["teclado", "candado"],
    "dinero": ["dinero"], "reloj": ["reloj"], "engranajes": ["engranajes"], "casas_red": ["antena"], "red": ["fibra", "cable"], "radar": ["antena"],
    "escudo": ["candado"], "duplicacion": ["disco", "usb"], "latido": ["semaforo"], "nube": ["datacenter"], "apagon": ["enchufe"], "ojo": ["camara"],
    "sala": ["tv_sala"], "dominos": ["engranajes"], "manometro": ["engranajes"], "puerta": ["candado"],
}
DUR_3D, DUR_FOTO = 2.6, 2.4                       # ritmo rapido: 3D corto, foto real entre medio


def cargar_pool(raiz_video):
    """{archivo(relativo a public): categoria} de fotos reales: objetos (public/fotos) + lugares nitidos (public/fondos_raw)"""
    pool = {}
    rf = os.path.join(raiz_video, "public", "fotos", "fotos.json")
    if os.path.exists(rf): pool.update(json.load(open(rf)))
    rl = os.path.join(raiz_video, "public", "fondos", "fondos.json")
    if os.path.exists(rl):
        for k, c in json.load(open(rl)).items():
            if os.path.exists(os.path.join(raiz_video, "public", "fondos_raw", os.path.basename(k))): pool["fondos_raw/" + os.path.basename(k)] = c
    return pool


POS = ["50% 50%", "35% 55%", "65% 50%", "50% 40%", "40% 60%", "60% 45%"]


def asignar_fondos(escenas, raiz_video):
    """foto REAL de fondo para cada clip 3D (habitacion o lugar acorde al objeto) y para los titulares; no se repite foto mientras queden sin usar"""
    ruta = os.path.join(raiz_video, "public", "fondos", "fondos.json")
    if not os.path.exists(ruta): print("AVISO: no hay fondos reales (public/fondos/fondos.json)"); return
    mapa = json.load(open(ruta)); usos = {f: 0 for f in mapa}; ult = None
    def elegir(cats):
        cand = [f for f, c in mapa.items() if c in cats] or list(mapa)
        cand.sort(key=lambda f: (usos[f], f == ult))
        return cand[0]
    for i, e in enumerate(escenas):
        if e["tipo"] == "3d": cats = OBJ_CATS.get(e["objeto"], ["sala"])
        elif e["tipo"] == "titular": cats = ["calle_noche", "ventana_noche", "estacion", "centro_comercial"]
        else: continue
        f = elegir(cats); usos[f] += 1; ult = f; e["fondo"] = f
        if e["tipo"] == "3d": e["fondoPos"] = POS[i % len(POS)]


DIAG_CASA = {"tipo": "diagrama", "titulo": "Una casa. Cinco dispositivos.", "nodos": [
    {"id": "casa", "x": 960, "y": 520, "icono": "casa", "etiqueta": "tu casa"}, {"id": "tv", "x": 960, "y": 880, "icono": "tv", "etiqueta": "caja tv"},
    {"id": "pc", "x": 1400, "y": 780, "icono": "pc", "etiqueta": "laptop"}, {"id": "movil", "x": 1460, "y": 330, "icono": "movil", "etiqueta": "móvil"},
    {"id": "cam", "x": 460, "y": 330, "icono": "camara", "etiqueta": "cámara"}, {"id": "router", "x": 500, "y": 780, "icono": "router", "etiqueta": "router"}],
    "enlaces": [["casa", "tv"], ["casa", "pc"], ["casa", "movil"], ["casa", "cam"], ["casa", "router"]], "infecta": ["tv", "pc", "router"]}
DIAG_PROXY = {"tipo": "diagrama", "titulo": "Tu conexión, alquilada", "nodos": [
    {"id": "casa", "x": 480, "y": 540, "icono": "casa", "etiqueta": "tu casa"}, {"id": "nube", "x": 960, "y": 540, "icono": "nube", "etiqueta": "proxy"},
    {"id": "pc", "x": 1440, "y": 540, "icono": "pc", "etiqueta": "desconocido"}],
    "enlaces": [["casa", "nube"], ["nube", "pc"]], "infecta": ["nube", "pc"]}


def escena_de(tag):
    luz = "noche"
    m = re.search(r"·\s*(noche|media|clara)", tag or "")
    if m: luz = m.group(1)
    t = (tag or "")
    if t.startswith("titular"):
        txt = re.sub(r"^titular:\s*", "", t.split("·")[0]).strip()
        txt, _, extra = txt.partition("|")
        lineas = [x.strip() for x in txt.split("/")]
        return {"tipo": "titular", "lineas": lineas, "resalta": len(lineas) - 1, "lado": "izq", "_golpe": True,
                "_relleno": [ALIAS.get(o.strip(), o.strip()) for o in extra.split("+") if o.strip()]}
    if t.startswith("diagrama"):
        d = dict(DIAG_PROXY if ("proxy" in t or "alquila" in t) else DIAG_CASA); d["_golpe"] = False
        return d
    # "3D a+b+c (comentario) . luz": varios objetos alternos para el mismo bloque
    cuerpo = re.sub(r"\(.*?\)", "", t.split("·")[0]); cuerpo = re.sub(r"^3D\s+", "", cuerpo, flags=re.I).strip()
    objs = []
    for o in [x.strip().lower() for x in cuerpo.split("+") if x.strip()]:
        o = ALIAS.get(o.split()[0], o.split()[0])
        if o == "candado" and "agujero" in t.lower(): o = "candado_agujero"
        objs.append(o)
    return {"tipo": "3d", "objetos": objs or ["caja_tv"], "luz": luz, "_golpe": False}


# ---------------------------------------------------------------- voizum
def llamar(metodo, ruta, key, cuerpo=None):
    req = urllib.request.Request(API + ruta, method=metodo, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                                 data=json.dumps(cuerpo).encode() if cuerpo is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Voizum HTTP {e.code}: {e.read().decode()[:300]}")


def listar_voces(key, filtro="martin"):
    d = llamar("GET", "/voices", key)
    lista = d if isinstance(d, list) else (d.get("voices") or d.get("data") or d.get("items") or [])
    norm = lambda x: unicodedata.normalize("NFD", str(x).lower()).encode("ascii", "ignore").decode()
    res = [v for v in lista if filtro in norm(json.dumps(v, ensure_ascii=False))]
    for v in res: print(json.dumps(v, ensure_ascii=False)[:300])
    print(f"{len(res)} voces con '{filtro}' de {len(lista)}"); return res


def voz_voizum(texto, voice_id, salida, key, velocidad=None):
    cuerpo = {"text": texto, "voice_id": voice_id, "language": "es", "pause_ms": 350}
    if velocidad: cuerpo["speed"] = velocidad
    job = llamar("POST", "/tts", key, cuerpo)
    print("creado", job["job_id"], "creditos", job.get("credits_charged"), flush=True)
    while True:
        st = llamar("GET", f"/tts/{job['job_id']}", key)
        if st["status"] in ("done", "error", "canceled"): break
        time.sleep(3)
    if st["status"] != "done": sys.exit(f"Voizum termino con estado {st['status']}")
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    req = urllib.request.Request(f"{API}/tts/{job['job_id']}/audio?download=1", headers={"Authorization": f"Bearer {key}"})
    try:
        urllib.request.build_opener(NoRedir).open(req, timeout=60); sys.exit("se esperaba redireccion")
    except urllib.error.HTTPError as e:
        destino = e.headers.get("Location")
        if e.code not in (301, 302, 303, 307, 308) or not destino: sys.exit(f"HTTP {e.code} al pedir el audio")
    with urllib.request.urlopen(destino, timeout=180) as r, open(salida, "wb") as f: f.write(r.read())   # sin cabecera de clave


# ---------------------------------------------------------------- alineacion
def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def alinear(audio, lineas):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=3)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    seg, info = m.transcribe(np.frombuffer(raw, np.float32), language="es", word_timestamps=True, beam_size=3, vad_filter=False)
    W = [(w.word.strip(), w.start, w.end) for s in seg for w in (s.words or []) if norm(w.word)]
    S = [(tok, li) for li, l in enumerate(lineas) for tok in l.split() if norm(tok)]
    sn, wn = [norm(t) for t, _ in S], [norm(w) for w, _, _ in W]
    t0 = [None] * len(S)
    for a, b, n in difflib.SequenceMatcher(None, sn, wn, autojunk=False).get_matching_blocks():
        for k in range(n): t0[a + k] = W[b + k][1]
    prev = 0.0                                                   # interpola las palabras sin pareja
    for i in range(len(S)):
        if t0[i] is None:
            j = i
            while j < len(S) and t0[j] is None: j += 1
            nxt = t0[j] if j < len(S) else info.duration
            for k in range(i, j): t0[k] = prev + (nxt - prev) * (k - i + 1) / (j - i + 1)
        prev = t0[i]
    inicio = {}
    for (tok, li), t in zip(S, t0): inicio.setdefault(li, t)
    print(f"palabras guion {len(S)} / whisper {len(W)}", flush=True)
    return [inicio[i] for i in range(len(lineas))], info.duration


# ---------------------------------------------------------------- mezcla + props
def mezclar(audio, inicios_escena, golpes, salida_mp3, segmentos=None, nivel_musica=0.10, bajar_desde=((166.0, 0.8),)):
    """voz + MUSICA DE AVENTURA audible (se baja un poco mientras habla la voz, 'ducking') + glitch en cada corte + riser/golpe en titulares"""
    import musica_aventura as mus
    SR = am.SR
    voz = am.leer(audio); D = len(voz) / SR; v_rms = float(np.sqrt(np.mean(voz ** 2)) + 1e-9)
    m = mus.pista(D + 2, segmentos)[: len(voz)]; m *= v_rms * nivel_musica
    env = am.lp(np.abs(voz), int(0.12 * SR)); env = np.clip(env / (0.6 * env.max() + 1e-9), 0, 1)
    for t_b, g_b in bajar_desde:                                   # pedido del usuario: bajar un poco la musica desde 2:46 (rampa de 2 s)
        rampa = np.clip((np.arange(len(m)) / SR - t_b) / 2.0, 0, 1); m *= 1 - (1 - g_b) * rampa
    m *= 1 - 0.40 * env                                           # ducking: -40 % mientras suena la voz, la musica "respira" en las pausas
    fx = np.zeros(len(voz))
    def poner(x, t, g):
        i = max(0, int(t * SR))
        if i < len(fx): fx[i:i + len(x)] += g * x[: len(fx) - i]
    for k, t in enumerate(inicios_escena):
        if k: g = am.glitch(); poner(g, t, 0.5 * v_rms / np.sqrt(np.mean(g ** 2)))
    for t in golpes:
        r = am.riser(); h = am.hit()
        poner(r, t - 2.0, 0.5 * v_rms / 0.2); poner(h, t + 0.05, 0.7 * v_rms / np.sqrt(np.mean(h ** 2)))
    mez = voz + m + fx
    fade = np.minimum(1, np.minimum(np.arange(len(mez)) / (1.5 * SR), (len(mez) - np.arange(len(mez))) / (2.0 * SR)))
    mez *= fade; mez *= 0.9 / max(0.9, np.abs(mez).max())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
                    "-c:a", "libmp3lame", "-q:a", "2", salida_mp3], input=(mez * 32767).astype("<i2").tobytes(), check=True)
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listar-voces", action="store_true"); ap.add_argument("--voz-id"); ap.add_argument("--audio")
    ap.add_argument("--lineas", type=int, default=52); ap.add_argument("--velocidad", type=float)
    ap.add_argument("--salida", default=os.path.join(RAIZ, "video"))
    a = ap.parse_args()
    key = os.environ.get("VOIZUM_API_KEY")
    if a.listar_voces:
        if not key: sys.exit("Falta VOIZUM_API_KEY en el entorno")
        listar_voces(key); return
    bloques = leer_bloques(a.lineas)
    lineas = [l for _, ls in bloques for l in ls]
    texto = "\n".join(lineas)
    print(f"{len(bloques)} bloques, {len(lineas)} lineas, {len(texto)} caracteres (~{len(texto) * 60 / 1000:.0f} creditos Voizum)")
    pub = os.path.join(a.salida, "public", "prueba4"); os.makedirs(pub, exist_ok=True)
    audio = a.audio or os.path.join(pub, "voz.mp3")
    if not a.audio:
        if not key or not a.voz_id: sys.exit("Faltan VOIZUM_API_KEY y --voz-id (usa --listar-voces para encontrar a Martin)")
        voz_voizum(texto, a.voz_id, audio, key, a.velocidad)
    ini_lin, dur = alinear(audio, lineas)
    # bloque -> escena (inicio = primera linea del bloque); bloques largos se parten en tramos de <= 9,5 s con la camara invertida
    escenas, inicios, golpes, k = [], [], [], 0
    usos = {}; prev = [None]
    fam = lambda o: FAMILIA.get(o, o)
    def elegir(pref):
        """objeto 3D del siguiente clip: el preferido si no llego al tope; si no, el menos usado distinto del anterior"""
        pref = [o for o in dict.fromkeys(pref) if o not in PROHIBIDOS]
        for o in pref:
            if usos.get(fam(o), 0) < MAX_USOS and fam(o) != fam(prev[0] or ""): return o
        cand = [o for o in TODOS_3D if fam(o) != fam(prev[0] or "")]
        cand.sort(key=lambda o: (usos.get(fam(o), 0), TODOS_3D.index(o)))
        return cand[0]
    pool = cargar_pool(a.salida); usos_f = {}; nfoto = [0]; bloque = [0]
    fxdir = os.path.join(a.salida, "public", "fotos_fx")             # imagenes de ImageFX (IMAGENES_IMAGEFX_PROMPTS.md): tienen prioridad
    fx = {}
    if os.path.isdir(fxdir):
        for n in sorted(os.listdir(fxdir)):
            m = re.match(r"b(\d+)_(\d+)\.(jpg|png)$", n)
            if m: fx.setdefault(int(m.group(1)), []).append("fotos_fx/" + n)
    print(f"imagenes ImageFX: {sum(len(v) for v in fx.values())}")
    print(f"pool de fotos reales: {len(pool)}")
    def elegir_foto(obj):
        cats = FOTO_PREF.get(obj, []); lug = OBJ_CATS.get(obj, [])
        for grupo in (cats, lug, None):
            cand = [f for f, c in pool.items() if (grupo is None or c in grupo) and usos_f.get(f, 0) == 0]
            if cand:
                cand.sort(key=lambda f: (0 if pool[f] == (cats or lug or [""])[0] else 1, f))
                f = cand[(nfoto[0] * 7) % len(cand)] if len(cand) > 1 else cand[0]
                usos_f[f] = 1; return f
        if pool: print("AVISO: se repite una foto (faltan fotos en el pool)")
        f = min(pool, key=lambda k: usos_f.get(k, 0)); usos_f[f] = usos_f.get(f, 0) + 1; return f
    def trozos(ta, tb, pref, luz):
        """el tramo se parte en clips cortos que se alternan: 3D (~3 s) / FOTO real (~2,2 s) del mismo tema"""
        total = tb - ta; piezas = []; x = 0.0; i = 0
        while x < total - 0.01:
            d = DUR_3D if i % 2 == 0 else DUR_FOTO
            if total - x - d < 1.3: d = total - x                          # sin migajas al final
            piezas.append(("3d" if i % 2 == 0 else "foto", d)); x += d; i += 1
        if len(piezas) > 1 and piezas[-1][0] == "foto" and piezas[-1][1] < 1.0: piezas[-2] = (piezas[-2][0], piezas[-2][1] + piezas[-1][1]); piezas.pop()
        esc = total / sum(d for _, d in piezas); x = ta; j = 0; ult = None
        for tipo, d in piezas:
            d *= esc
            if tipo == "3d":
                o = elegir(pref[j % len(pref):] + pref[:j % len(pref)] if pref else [])
                e = {"tipo": "3d", "objeto": o, "luz": luz, "dur": round(d, 3)}
                if usos.get(fam(o), 0) >= MAX_USOS: print("AVISO: se repite el clip", o, "(la biblioteca 3D no alcanza: crear mas objetos)")
                usos[fam(o)] = usos.get(fam(o), 0) + 1; prev[0] = o; ult = o; j += 1
            else:
                sig = (pref[j % len(pref)] if pref else None) or ult
                f = fx[bloque[0]].pop(0) if fx.get(bloque[0]) else elegir_foto(ult or sig or "sala"); nfoto[0] += 1
                e = {"tipo": "foto", "archivo": f, "luz": luz, "v": nfoto[0], "pos": POS[nfoto[0] % len(POS)], "dur": round(d, 3)}
            escenas.append(e); inicios.append(x); x += d
    for bi, (tag, ls) in enumerate(bloques):
        t_ini = ini_lin[k]; t_fin = ini_lin[k + len(ls)] if k + len(ls) < len(lineas) else dur; k += len(ls)
        base = escena_de(tag); tipo = base["tipo"]; bloque[0] = bi + 1
        if tipo == "3d":
            trozos(t_ini, t_fin, base["objetos"], base["luz"])
        else:
            tope = 4.5 if tipo == "titular" else 8.0
            t_med = min(t_fin, t_ini + tope) if (t_fin - t_ini) > tope + 1.5 else t_fin
            e = {x: v for x, v in base.items() if not x.startswith("_")}; e["dur"] = round(t_med - t_ini, 3)
            escenas.append(e); inicios.append(t_ini); prev[0] = None
            if base.get("_golpe"): golpes.append(t_ini + 0.1)
            if t_fin - t_med > 0.05:                               # el titular/diagrama no se queda quieto toda la frase: sigue un clip 3D variado
                trozos(t_med, t_fin, base.get("_relleno", []), "media")
    escenas[0]["dur"] = round(escenas[0]["dur"] + inicios[0], 3); inicios[0] = 0.0       # cubre el silencio inicial
    mp3 = os.path.join(pub, "mezcla.mp3")
    segs = [(inicios[i], (inicios[i + 1] if i + 1 < len(inicios) else dur), escenas[i].get("luz", "media")) for i in range(len(escenas))]
    D = mezclar(audio, inicios, golpes, mp3, segs)
    props = {"escenas": escenas, "voz": "prueba4/mezcla.mp3"}
    ruta = os.path.join(a.salida, "props_prueba4.json"); json.dump(props, open(ruta, "w"), ensure_ascii=False, indent=1)
    print(f"LISTO: {len(escenas)} escenas, audio {D / 60:.1f} min -> {ruta}")
    print("Siguiente: cd ../video && npx remotion render src/index.ts Historia out/prueba4.mp4 --props=props_prueba4.json --scale=0.5 --concurrency=4")


if __name__ == "__main__":
    main()
