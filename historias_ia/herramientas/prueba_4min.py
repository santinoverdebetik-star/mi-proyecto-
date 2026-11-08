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
import visuales as VIS  # noqa: E402
import random as _random  # noqa: E402
R_BL = _random.Random(3)

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


GANCHO = ["Las cosas que «solo pasan en el laboratorio» tienen un hábito: dejan de ser solo de laboratorio.",
           "Quince cajas baratas de televisión. Una inteligencia artificial repartida entre todas.",
           "Ahora imagina que esa inteligencia aprendiera a copiarse sola."]
CONTROL = r"fuera de control|se copia|copiarse|gusano|infect|sin un humano|por si mismo|sola\b|peligro|miedo|ochenta|dos millones|ataque|contagi|obedece|roba"
PROHIBIDOS = set()                                # el usuario levanto la prohibicion de ojo/nucleo/red (V15)                    # el usuario no los quiere NUNCA (pedido V5): se sustituyen
ALIAS = {"laptop": "contagio", "pantalla": "pantalla_rota"}
TODOS_3D = ["globo", "cable", "codigo", "sala", "estanteria", "avalancha", "casas_red", "fabrica", "candado", "apagon", "intrusion", "contagio", "caja_led",
            "caja_tv", "manometro", "radar", "duplicacion", "rack", "cajas15", "puerta", "pantalla_rota", "router", "camara", "movil", "pc_antiguo", "reloj",
            "calendario", "placa", "llave", "dominos", "escudo", "dinero", "hdmi", "password", "engranajes", "latido", "paquetes", "antena", "lupa", "mando", "nube",
            "tv_play", "ojo", "nucleo", "red"]
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
DUR_3D, DUR_FOTO = 7.5, 3.2                     # pedido V11: los 3D duran MAS (salas ~9,5 s, objetos ~7 s); insertos cortos
DUR_SALA = 10.5
BL_HASTA = 300.0                                   # pedido: los primeros 5 minutos van en BLENDER (fotorrealista); despues, 3D en codigo
DUR_BL = 4.5                                       # pedido: escenas de ~4 s en pantalla
GEN_FAM = ["hogar", "lab", "srv", "ofi", "fab", "mapa", "calle", "tienda"]
SALAS_TIROS = {f: [] for f in GEN_FAM}                                   # pedido V12: ningun ambiente 3D se repite: cada sala se GENERA con una semilla nueva
SALA_IDS = set()
GEN_N = [0]
LAB3_USADO = [0]                     # pedido V7: clips 3D 2 s mas largos; entre ellos se intercalan insertos variados (no solo fotos)
# inserto que sigue a cada clip 3D: grafico Remotion afin al objeto que se acaba de ver (pedido V8: poco texto; las fotos reales, solo de vez en cuando)
INS_OBJ = {"radar": ["radar", "antena", "camara", "lupa"], "globo2d": ["globo", "casas_red", "nube", "red", "paquetes", "dinero", "calendario"],
           "cuadricula": ["dominos", "contagio", "intrusion", "duplicacion", "cajas15", "estanteria", "pc_antiguo", "pantalla_rota"],
           "barras": ["avalancha", "apagon", "latido", "manometro", "engranajes", "fabrica", "reloj"], "lluvia": ["codigo", "password", "candado", "llave", "placa", "hdmi", "cable", "escudo", "puerta"],
           "flujo": ["router", "movil", "caja_tv", "caja_led", "sala", "tv_play", "mando"], "roja": ["router", "caja_tv", "hdmi", "cable", "hogar2", "hogar3", "tv_play", "estanteria", "srv2", "map1", "lab3"], "terminal": ["intrusion", "codigo", "pc_antiguo", "contagio", "rack"]}
ROTA = ["flujo", "radar", "cuadricula", "globo2d", "barras", "lluvia", "terminal"]                       # ritmo rapido: 3D corto, foto real entre medio


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
    if t.startswith("comparar"):
        cuerpo, _, extra = re.sub(r"^comparar:\s*", "", t.split("·")[0]).partition(">>")
        a, b = [[x.strip() for x in lado.split("|")] for lado in cuerpo.split("||")]
        tema = (re.search(r"·\s*(rojo|azul|oscuro)", t) or [None, "rojo"])[1]
        return {"tipo": "comparar", "izq": dict(zip(("icono", "titulo", "valor"), a)), "der": dict(zip(("icono", "titulo", "valor"), b)), "tema": tema, "_golpe": False,
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


def voz_voizum(texto, voice_id, salida, key, velocidad=None, pausa=350):
    cuerpo = {"text": texto, "voice_id": voice_id, "language": "es", "pause_ms": pausa}
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
def mezclar(audio, inicios_escena, golpes, salida_mp3, segmentos=None, nivel_musica=0.16, bajar_desde=(), escenas=None):
    """voz + MUSICA DE AVENTURA audible (se baja un poco mientras habla la voz, 'ducking') + glitch en cada corte + riser/golpe en titulares"""
    import musica_oscura as mus                                    # V13: ambiente oscuro continuo como la referencia 3 (sin melodia ni bateria)
    SR = am.SR
    voz = am.leer(audio); D = len(voz) / SR; v_rms = float(np.sqrt(np.mean(voz ** 2)) + 1e-9)
    m = mus.pista(D + 2, segmentos)[: len(voz)]; m *= v_rms * nivel_musica
    env = am.lp(np.abs(voz), int(0.12 * SR)); env = np.clip(env / (0.6 * env.max() + 1e-9), 0, 1)
    for t_b, g_b in bajar_desde:                                   # pedido del usuario: bajar un poco la musica desde 2:46 (rampa de 2 s)
        rampa = np.clip((np.arange(len(m)) / SR - t_b) / 2.0, 0, 1); m *= 1 - (1 - g_b) * rampa
    dip = np.zeros(len(m))
    for t_g in golpes:                                             # SILENCIO antes de cada revelacion: la musica se apaga ~1,4 s y vuelve con el golpe
        i0, i1 = max(0, int((t_g - 1.4) * SR)), min(len(m), int(t_g * SR)); dip[i0:i1] = 1
    dip = np.convolve(dip, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same"); m *= 1 - 0.97 * np.clip(dip, 0, 1)
    m *= 1 - 0.35 * env                                           # ducking: -40 % mientras suena la voz, la musica "respira" en las pausas
    fx = np.zeros(len(voz))
    def poner(x, t, g):
        i = max(0, int(t * SR))
        if i < len(fx): fx[i:i + len(x)] += g * x[: len(fx) - i]
    import sfx
    nrm = lambda x: x / (np.abs(x).max() + 1e-9)
    G = lambda x, g: g * v_rms * nrm(x)
    for k, t in enumerate(inicios_escena):
        e = escenas[k] if escenas else {}; tr = e.get("trans", "pixel"); tp = e.get("tipo")
        if k:                                                          # sonido de la transicion (0,12 s antes del corte, que es donde empieza el efecto)
            t0 = max(0, t - 0.12)
            if tr == "corte": pass
            elif tr == "fundido": poner(G(sfx.whoosh(0.7, 120, 1200), 0.14), max(0, t - 0.45), 1)
            elif tr == "pixel": poner(G(sfx.blips((523, 659, 880, 1047), 0.04), 0.30), t0, 1); poner(G(sfx.whoosh(0.35, 700, 6000), 0.16), t0, 1)
            elif tr in ("barras", "cortina"): poner(G(sfx.whoosh(0.5, 300, 4500), 0.30), t0, 1)
            elif tr == "persianas": poner(G(sfx.whoosh(0.4, 600, 5500), 0.22), t0, 1); poner(G(sfx.blips((330, 392, 330, 392), 0.035), 0.18), t0 + 0.05, 1)
            elif tr == "rgb": g_ = am.glitch(); poner(g_, t0, 0.22 * v_rms / np.sqrt(np.mean(g_ ** 2))); poner(G(sfx.whoosh(0.3, 800, 7000), 0.18), t0, 1)
            else: poner(G(sfx.whoosh(0.45, 500, 7000), 0.26), t0, 1); poner(G(sfx.golpe_grave(), 0.34), t, 1)
        if tp == "comparar":
            poner(G(sfx.pop(480), 0.42), t + 0.12, 1); poner(G(sfx.pop(620), 0.42), t + 0.32, 1); poner(G(sfx.blips((784, 988, 1319), 0.05), 0.30), t + 0.62, 1)
        elif tp == "dato": poner(G(sfx.ding(), 0.34), t + 0.25, 1)
        elif tp == "terminal":
            for j in range(34): poner(G(sfx.tick(), 0.20), t + 0.25 + j * 0.065, 1)
        elif tp == "radar":
            for j in range(2): poner(G(sfx.ping(880), 0.24), t + 0.2 + j * 1.2, 1)
        elif tp == "cuadricula":
            for j in range(7): poner(G(sfx.blips((392 * 1.12 ** j,), 0.04), 0.20), t + 0.25 + j * 0.2, 1)
        elif tp == "barras":
            for j in range(5): poner(G(sfx.pop(300 + j * 40), 0.22), t + 0.2 + j * 0.35, 1)
    for t in golpes:
        r = am.riser(); h = am.hit()
        g2 = am.glitch(); poner(g2, t - 0.03, 0.34 * v_rms / np.sqrt(np.mean(g2 ** 2))); poner(h, t + 0.05, 0.4 * v_rms / np.sqrt(np.mean(h ** 2)))
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
    ap.add_argument("--pausa", type=int, default=350); ap.add_argument("--proyecto", default="prueba4"); ap.add_argument("--solo-voz", action="store_true"); ap.add_argument("--gancho", action="store_true")
    ap.add_argument("--salida", default=os.path.join(RAIZ, "video"))
    a = ap.parse_args()
    key = os.environ.get("VOIZUM_API_KEY")
    if a.listar_voces:
        if not key: sys.exit("Falta VOIZUM_API_KEY en el entorno")
        listar_voces(key); return
    bloques = leer_bloques(a.lineas)
    n_guion = sum(len(ls) for _, ls in bloques)
    if a.gancho: bloques = [("gancho", GANCHO)] + bloques
    lineas = [l for _, ls in bloques for l in ls]
    texto = "\n".join(lineas)
    print(f"{len(bloques)} bloques, {len(lineas)} lineas, {len(texto)} caracteres (~{len(texto) * 60 / 1000:.0f} creditos Voizum)")
    pub = os.path.join(a.salida, "public", a.proyecto); os.makedirs(pub, exist_ok=True)
    audio = a.audio or os.path.join(pub, "voz_total.mp3" if a.gancho else "voz.mp3")
    if not a.audio:
        if not key or not a.voz_id: sys.exit("Faltan VOIZUM_API_KEY y --voz-id (usa --listar-voces para encontrar a Martin)")
        voz_voizum(texto, a.voz_id, audio, key, a.velocidad, a.pausa)
        if a.solo_voz: print("voz lista:", audio); return
    cache_al = os.path.join(pub, "alineacion.json")
    if a.gancho:                                                       # gancho (alineado aparte) + guion (alineacion en cache) desplazado
        g_mp3 = os.path.join(pub, "gancho.mp3"); off = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", g_mp3], capture_output=True, text=True).stdout) + 0.9
        cg = os.path.join(pub, "alineacion_gancho.json")
        if os.path.exists(cg): ini_g = json.load(open(cg))
        else: ini_g, _ = alinear(g_mp3, GANCHO); json.dump(ini_g, open(cg, "w"))
        d_al = json.load(open(cache_al)); assert len(d_al["ini"]) == n_guion, "la alineacion en cache no coincide con el guion"
        ini_lin = list(ini_g) + [x + off for x in d_al["ini"]]; dur = off + d_al["dur"]
    elif os.path.exists(cache_al):
        d_al = json.load(open(cache_al))
        if len(d_al["ini"]) == len(lineas): ini_lin, dur = d_al["ini"], d_al["dur"]
        else: ini_lin, dur = alinear(audio, lineas); json.dump({"ini": ini_lin, "dur": dur}, open(cache_al, "w"))
    else:
        ini_lin, dur = alinear(audio, lineas); json.dump({"ini": ini_lin, "dur": dur}, open(cache_al, "w"))
    # bloque -> escena (inicio = primera linea del bloque); bloques largos se parten en tramos de <= 9,5 s con la camara invertida
    escenas, inicios, golpes, k = [], [], [], 0
    usos = {}; prev = [None]
    fam = lambda o: FAMILIA.get(o, o)
    rec_fam = []
    def sala_siguiente(fam_):
        if fam_ not in GEN_FAM: return None
        GEN_N[0] += 1
        return f"gen:{fam_}:{ctl_actual[0]}{GEN_N[0]}"
    usos_mesa = {}; ult_mesa = [None]
    def mesa_siguiente(prop):
        if usos_mesa.get(prop, 0) >= 11 or ult_mesa[0] == prop: return None                       # cada objeto protagonista, como mucho 7 veces (siempre con otra mesa, luz y camara)
        usos_mesa[prop] = usos_mesa.get(prop, 0) + 1; GEN_N[0] += 1; ult_mesa[0] = prop
        return f"gen:mesa:{ctl_actual[0]}{GEN_N[0]}:{prop}"
    ctl_actual = ["k"]
    def elegir_visual(texto, pref):
        ctl_actual[0] = "A" if re.search(CONTROL, VIS.norm(texto)) else "k"                # "A" = palette de alerta (azul frio + rojo/ambar) cuando la IA se sale de control
        """objeto 3D o plano de sala para el texto que suena: palabras clave -> candidatos; luego la etiqueta del bloque; luego lo menos usado"""
        sc = VIS.puntuar(texto)
        pref = [ALIAS.get(o, o) for o in pref if o not in PROHIBIDOS]
        for c, _ in sorted(sc.items(), key=lambda kv: -kv[1]):
            if c.startswith("M:"):
                if sum(1 for x in rec_fam[-6:] if x == "mesa") >= 3: continue
                s = mesa_siguiente(c[2:])
                if s: rec_fam.append("mesa"); return s
                continue
            if c.startswith("R:"):
                if c == "R:lab" and sum(usos.values()) - LAB3_USADO[0] * 0 > 6 and GEN_N[0] // 32 > LAB3_USADO[0]:
                    LAB3_USADO[0] += 1; GEN_N[0] += 1; return f"gen:lab:R{GEN_N[0]}"      # laboratorio donde la camara entra en el monitor rojo (transicion 3D -> 2D)
                if sum(1 for x in rec_fam[-10:] if x == c[2:]) >= 3: continue          # variedad: no mas de 3 ambientes de la misma familia entre los ultimos 10
                s = sala_siguiente(c[2:])
                if s: rec_fam.append(c[2:]); return s
                continue
            if c in PROHIBIDOS: continue
            if usos.get(fam(c), 0) < MAX_USOS and fam(c) != fam(prev[0] or "") and c in TODOS_3D: rec_fam.append("obj"); return c
        for o in pref:
            if (o in TODOS_3D) and usos.get(fam(o), 0) < MAX_USOS and fam(o) != fam(prev[0] or ""): return o
        libres = [o for o in TODOS_3D if usos.get(fam(o), 0) == 0 and fam(o) != fam(prev[0] or "")]
        if libres: rec_fam.append("obj"); return libres[(sum(usos.values()) * 3) % len(libres)]
        for f_ in ("lab", "srv", "fab", "ofi", "mapa", "hogar", "calle", "tienda"):
            s = sala_siguiente(f_)
            if s: return s
        print("AVISO: no quedan clips 3D sin usar; se repite uno")
        return min(TODOS_3D, key=lambda o: usos.get(fam(o), 0))
    nins = [0]; hist = []; K3 = [0]
    def texto_en(t0, t1):
        """texto de la narracion que suena entre t0 y t1 (para frases y cifras en pantalla)"""
        out = []
        for i, l in enumerate(lineas):
            a_, b_ = ini_lin[i], (ini_lin[i + 1] if i + 1 < len(lineas) else dur)
            if a_ < t1 and b_ > t0: out.append(l)
        return " ".join(out[:2])
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
    usos_bl = {}; ult_bl = [None]; ult_set = set()
    # etiquetas de cada objeto de Blender (modelos reales de Poly Haven + los armados a mano): palabras del narrador -> objetos
    BL_TAGS = {
        "robot": r"inteligencia artificial|\bia\b|asistente|agente|modelo|robot|piensa|decide|entiende|aprend|parametros|maquina",
        "router": r"router|wifi|modem|internet|conexion|conectad|red\b",
        "cajas": r"\bcaja|cajita|cajas|streaming|android|decodificador|televisor",
        "telefono": r"telefono|movil|celular|mensaje|correo|email",
        "llave": r"llave|cerradura|puerta|contrasena|agujero|entrar|acceso|abrir",
        "alarm_clock_01": r"hora|tiempo|reloj|minuto|segundo|dias|noche|despert|madrugada", "mantel_clock_01": r"tiempo|reloj|ano|historia|1988|2003|2016|antiguo|vieja|decada",
        "wall_clock": r"hora|tiempo|reloj|diez minutos|velocidad|rapid|lent", "vintage_telephone_wall_clock": r"llamada|telefono|tiempo|hora",
        "classic_laptop": r"laptop|computador|ordenador|portatil|maquina|codigo|programa|virus|software|dato|gusano", "retro_multimeter": r"medir|midieron|numero|cifra|porcentaje|prueba|calculo|sube",
        "binder_notebook": r"informe|documento|registro|estudio|apunte|publico|publicaron|empresa|ley", "vintage_stapler": r"oficina|papeles|documento|empresa|trabajo",
        "security_camera_01": r"camara|vigil|seguridad|grabador|observa", "security_camera_02": r"camara|vigil|seguridad|mira|rastro|detect", "Camera_01": r"foto|imagen|ver|miro|mirar|captur",
        "vintage_video_camera": r"video|grab|imagen|pelicula|filmar", "binoculars": r"buscar|busca|encontr|explor|vigil|lejos|detect|descubr", "magnifying_glass_01": r"investig|descubr|detalle|analiz|encontr|averigu|lupa|buscar",
        "Television_01": r"televisor|\btele\b|serie\b|pelicula|pantalla|sala\b|salas", "television_02": r"televisor|pantalla|tele\b|imagen|salas", "filmstrip_projector_8mm": r"pelicula|escena|imagen|proyect|historia",
        "vintage_radio_transceiver": r"senal|radio|antena|onda|transmit|frecuencia|hablan|comunica", "boombox": r"voz|audio|escuch|sonido|ruido|radio", "cassette_player": r"voz|grab|audio|escuch|mensaje",
        "portable_cassette_player": r"voz|grab|audio|escuch|mensaje|decir", "Megaphone_01": r"anuncio|titular|portada|publicaron|gritar|avis|alerta",
        "desk_lamp_arm_01": r"\bluz\b|lampara|noche|oscur|trabajo|escritorio", "Lantern_01": r"\bluz\b|oscur|noche|sombra|miedo|alerta", "vintage_flashlight": r"\bluz\b|buscar|oscur|linterna|encontr",
        "signal_flashlight": r"senal|alerta|parpade|luz|aviso", "pull_chain_light_socket": r"\bluz\b|encend|apag|bombilla|parpade",
        "utility_box_01": r"caja|cuadro|electric|conexion|instalar|fabrica", "power_box_01": r"electric|energia|apagon|corriente|enchuf", "metal_toolbox": r"tecnico|arreglar|instal|reparar|herramienta|fabrica",
        "vintage_suitcase": r"viaj|llevar|mundo|enviar|paquete|llega", "wooden_crate_01": r"paquete|almacen|envio|fabrica|caja", "cardboard_box_01": r"paquete|envio|caja|comprar|compro|tienda",
        "screwdriver": r"tecnico|arreglar|abrir|instal|reparar|plastico", "adjustable_wrench": r"tecnico|arreglar|ajust|reparar|mecanismo", "seadogs_compass": r"camino|rumbo|dirigi|destino|direccion|guiar|mundo",
        "modular_electric_cables": r"cable|conecta|enchuf|hdmi|red\b|conexion", "book_encyclopedia_set_01": r"libro|historia|estudio|investig|ley|universidad|siglo",
        "korean_public_payphone_01": r"llamada|telefono|numero|llamar|marcar",
    }
    PROPS_BL = list(BL_TAGS)
    ESP_TAGS = {"ojo_ia": r"inteligencia artificial|\bia\b|modelo|piensa|decide|entiende|agente|asistente|que lee|mira a su alrededor|robot|obedece",
                "red_neuronal": r"neuron|parametros|modelo|cortaron|pedazos|aprend|miles de|millones|conectad|red\b|inteligencia",
                "servidores": r"servidor|centro de datos|dns|avalancha|peticion|ataque|decenas de miles|nodos|rack|cluster|millones|todo internet",
                "codigo": r"codigo|programa|virus|gusano|escrito|instruccion|software|comando|malware|copia|copiarse|replic"}
    CONTROL = r"fuera de control|se copia|copiarse|gusano|infect|sin un humano|por si mismo|sola\b|peligro|miedo|ochenta|dos millones|ataque|contagi|obedece|roba"
    usos_esp = {}
    def paleta_de(texto, sem):
        if re.search(CONTROL, VIS.norm(texto)): return "alerta"
        return "frio" if sem % 3 == 0 else None
    def elegir_blender(texto, n=3):
        tn = VIS.norm(texto)
        pe = {k: len(re.findall(rx, tn)) for k, rx in ESP_TAGS.items()}
        mejor = max(pe, key=lambda k: pe[k] - usos_esp.get(k, 0) * 0.8)
        if pe[mejor] >= 1 and usos_esp.get(mejor, 0) < 4 and (GEN_N[0] % 3 != 1) and ult_bl[0] not in ESP_TAGS:
            usos_esp[mejor] = usos_esp.get(mejor, 0) + 1; ult_bl[0] = mejor; ult_set.clear(); GEN_N[0] += 1
            return [mejor], GEN_N[0], ("alerta" if re.search(CONTROL, tn) else "frio")
        pun = {}
        for pr, rx in BL_TAGS.items():
            k = len(re.findall(rx, tn)); pun[pr] = k * 2.0 + R_BL.random() * 0.6 - usos_bl.get(pr, 0) * 1.4
        elegidos = []
        for pr in sorted(pun, key=lambda k: -pun[k]):
            if usos_bl.get(pr, 0) >= 3 or pr in ult_set or pr in elegidos: continue
            elegidos.append(pr)
            if len(elegidos) == n: break
        for pr in elegidos: usos_bl[pr] = usos_bl.get(pr, 0) + 1
        ult_set.clear(); ult_set.update(elegidos); ult_bl[0] = elegidos[-1]; GEN_N[0] += 1
        return elegidos, GEN_N[0], paleta_de(texto, GEN_N[0])
    def texto_ini(t0, t1):
        """lineas que EMPIEZAN entre t0 y t1 (lo que se dice mientras dura el clip)"""
        out = [l for i, l in enumerate(lineas) if t0 - 0.3 <= ini_lin[i] < t1]
        return " ".join(out) or texto_en(t0, t0 + 1)
    def corte(x, objetivo, minimo, tb):
        """fin del clip: el limite de linea mas cercano a x+objetivo (la imagen cambia cuando cambia la frase), sin migajas al final"""
        cand = [ini_lin[i] for i in range(len(lineas)) if x + minimo <= ini_lin[i] <= x + objetivo + 2.5]
        fin = min(cand, key=lambda c: abs(c - (x + objetivo))) if cand else x + objetivo
        if tb - fin < 3.2: fin = tb
        return min(fin, tb)
    def trozos(ta, tb, pref, luz):
        x = ta
        if tb - x < 4.2 and escenas and escenas[-1]["tipo"] == "3d":     # resto corto: se alarga el ultimo 3D (los 3D no deben ser cortos)
            escenas[-1]["dur"] = round(escenas[-1]["dur"] + (tb - x), 3); return
        while tb - x > 0.35:
            rest = tb - x
            if K3[0] >= 3 and rest > 9:                                       # cada dos clips 3D, un inserto corto (pantalla roja, radar, globo, terminal, foto...)
                fin = corte(x, DUR_FOTO, 2.2, tb); d = fin - x
                tx = texto_ini(x, fin); ult = prev[0]
                dato = re.search(r"(\$\s?\d[\d.,]*|\d[\d.,]*\s?%|\b(?:19|20)\d\d\b)", tx)
                pref_k = VIS.inserto_para(tx)
                if (ult or "").startswith("gen:lab:R"): kind = "roja"                               # la camara entra en el monitor rojo y la pantalla roja llena el cuadro (3D -> 2D)
                elif fx.get(bloque[0]): kind = "foto"
                elif dato and "numero" not in hist[-2:] and "dato" not in hist[-2:]: kind = "numero" if nins[0] % 3 else "dato"
                else:
                    ok = [k for k in pref_k if k not in hist[-3:]]
                    if ok: kind = ok[0]
                    else:
                        rot = [k for k in ["casa", "mapapuntos", "radar", "terminal", "foto", "grilla", "anillos", "puerta", "ondas", "roja"] if k not in hist[-3:]]
                        kind = "foto" if (nins[0] % 4 == 3 and "foto" not in hist[-2:]) else rot[nins[0] % len(rot)]
                nins[0] += 1; hist.append(kind); v = nins[0]
                if kind == "numero":
                    fr = re.split(r"(?<=[.!?])\s+", tx.strip()); fr = next((s for s in fr if dato.group(1) in s), fr[0])
                    e = {"tipo": "numero", "valor": dato.group(1).replace(" ", ""), "etiqueta": (lambda s_: s_[:s_[:44].rfind(" ")] if len(s_) > 44 else s_)(re.sub(r"\s+", " ", fr)).rstrip(" ,;:").upper(), "dur": round(d, 3)}
                elif kind == "mapapuntos":
                    dm = "dos millones" in VIS.norm(tx) or "2 millones" in VIS.norm(tx)
                    e = {"tipo": "mapapuntos", "dur": round(d, 3), **({"valor": "2,000,000+", "etiqueta": "DISPOSITIVOS INFECTADOS"} if dm else {})}
                elif kind in ("casa", "puerta"): e = {"tipo": kind, "dur": round(d, 3)}
                elif kind == "grilla":
                    q = "quince" in VIS.norm(tx); e = {"tipo": "grilla", "n": 15 if q else 12, "dur": round(d, 3), **({"etiqueta": "QUINCE CAJAS"} if q else {})}
                elif kind == "dato":
                    fr = re.split(r"(?<=[.!?])\s+", tx.strip()); fr = next((s for s in fr if dato.group(1) in s), fr[0])
                    e = {"tipo": "dato", "valor": dato.group(1).replace(" ", ""), "etiqueta": (lambda s_: s_[:s_[:52].rfind(" ")] if len(s_) > 52 else s_)(re.sub(r"\s+", " ", fr)).rstrip(" ,;:").upper(), "dur": round(d, 3), "fondo": foto_tema(tx, ult)}
                elif kind == "roja": e = {"tipo": "roja", "variante": "ventana" if (ult or "").startswith("gen:lab:R") else "cadena", "etiqueta": None if (ult or "").startswith("gen:lab:R") else "TU CASA > INTERNET", "v": v, "dur": round(d, 3)}
                elif kind == "terminal":
                    fr_ = re.split(r"(?<=[.!?])\s+", tx.strip())[0]; fr_ = fr_ if len(fr_) < 130 else fr_[:130].rsplit(" ", 1)[0] + "…"
                    e = {"tipo": "escribe", "texto": fr_, "est": 2, "dur": round(d, 3)}
                elif kind in ("radar", "barras", "globo2d", "ondas", "anillos"): e = {"tipo": kind, "v": v, "dur": round(d, 3)}
                else:
                    f = fx[bloque[0]].pop(0) if fx.get(bloque[0]) else foto_tema(tx, ult); nfoto[0] += 1
                    e = {"tipo": "foto", "archivo": f, "luz": luz, "v": nfoto[0], "pos": POS[nfoto[0] % len(POS)], "dur": round(d, 3)}
                escenas.append(e); inicios.append(x); x += d; K3[0] = 0; continue
            tx = texto_ini(x, x + 9)
            if x < BL_HASTA:                                               # primeros 5 minutos: clip de Blender (fotorrealista)
                cand_l = [ini_lin[i] for i in range(len(lineas)) if abs(ini_lin[i] - (x + DUR_BL)) <= 1.1]
                fin = min(cand_l, key=lambda c: abs(c - (x + DUR_BL))) if cand_l else x + DUR_BL
                if tb - fin < 3.0: fin = tb
                fin = min(fin, tb); d = fin - x; prs, sem, pal_ = elegir_blender(tx, 3 if d >= 4.0 else 2)
                escenas.append({"tipo": "blender", "props": prs, "seed": sem, "dur": round(d, 3), "luz": luz, **({"paleta": pal_} if pal_ else {})}); K3[0] += 1; prev[0] = "bl:" + prs[0]; inicios.append(x); x += d; continue
            o = elegir_visual(tx, pref); sala = o.startswith("gen:") and not o.startswith("gen:mesa")
            obj = DUR_SALA if sala else DUR_3D
            fin = corte(x, obj, obj - 2.0, tb); d = fin - x
            e = {"tipo": "3d", "objeto": o, "luz": luz, "dur": round(d, 3)}
            if usos.get(fam(o), 0) >= MAX_USOS: print("AVISO: se repite el clip", o)
            usos[fam(o)] = usos.get(fam(o), 0) + 1; prev[0] = o; K3[0] += 1
            escenas.append(e); inicios.append(x); x += d
    def foto_tema(tx, ult):
        """foto real para titulares/cifras/insertos segun lo que se dice: el objeto/sala mas puntuado del texto"""
        sc = VIS.puntuar(tx)
        for c, _ in sorted(sc.items(), key=lambda kv: -kv[1]):
            if c.startswith("R:"): return elegir_foto_cats(VIS.FOTO_SALA.get(c[2:], ["sala"]))
            if c in FOTO_PREF or c in OBJ_CATS: return elegir_foto(c)
        return elegir_foto(ult or "sala")
    def elegir_foto_cats(cats):
        for grupo in (cats, None):
            cand = [f for f, c in pool.items() if (grupo is None or c in grupo) and usos_f.get(f, 0) == 0]
            if cand:
                f = cand[(nfoto[0] * 7) % len(cand)]; usos_f[f] = 1; nfoto[0] += 1; return f
        f = min(pool, key=lambda k: usos_f.get(k, 0)); usos_f[f] = usos_f.get(f, 0) + 1; return f
    for bi, (tag, ls) in enumerate(bloques):
        t_ini = ini_lin[k]; t_fin = ini_lin[k + len(ls)] if k + len(ls) < len(lineas) else dur; k += len(ls)
        if tag == "gancho":                                            # gancho de ~20 s: frase mas perturbadora escrita letra a letra + servidores + ojo de la IA, en frio y rojo
            i0 = k - len(ls); lim = [ini_lin[i0 + j] for j in range(len(ls))] + [t_fin]
            escenas.append({"tipo": "escribe", "texto": "Las cosas que «solo pasan en el laboratorio» tienen un hábito: **dejan de ser solo de laboratorio.**", "est": 1, "dur": round(lim[1] - lim[0], 3), "luz": "noche"}); inicios.append(lim[0])
            escenas.append({"tipo": "blender", "props": ["servidores"], "paleta": "frio", "seed": 9001, "dur": round(lim[2] - lim[1], 3), "luz": "noche"}); inicios.append(lim[1])
            escenas.append({"tipo": "blender", "props": ["ojo_ia"], "paleta": "alerta", "seed": 9002, "dur": round(t_fin - lim[2], 3), "luz": "noche"}); inicios.append(lim[2]); prev[0] = None; golpes.append(lim[0] + 0.1)
            continue
        base = escena_de(tag); tipo = base["tipo"]; bloque[0] = bi + 1
        if tipo == "3d":
            trozos(t_ini, t_fin, base["objetos"], base["luz"])
        else:
            tope = 4.0 if tipo == "titular" else (4.4 if tipo == "comparar" else 8.0)
            t_med = min(t_fin, t_ini + tope) if (t_fin - t_ini) > tope + 4.2 else t_fin     # un resto de menos de ~4 s se absorbe en el titular (nada de clips 3D cortos)
            e = {x: v for x, v in base.items() if not x.startswith("_")}; e["dur"] = round(t_med - t_ini, 3)
            if tipo == "titular": e["fondo"] = foto_tema(" ".join(ls) + " " + " ".join(base.get("_relleno", [])), None)
            escenas.append(e); inicios.append(t_ini); prev[0] = None
            if base.get("_golpe") or tipo == "comparar": golpes.append(t_ini + 0.1)
            if t_fin - t_med > 0.05:                               # el titular/diagrama no se queda quieto toda la frase: sigue un clip 3D variado
                trozos(t_med, t_fin, base.get("_relleno", []), "media")
    escenas[0]["dur"] = round(escenas[0]["dur"] + inicios[0], 3); inicios[0] = 0.0       # cubre el silencio inicial
    ciclo = ["corte", "fundido", "fundido", "corte", "fundido", "pixel", "corte", "fundido", "rgb", "fundido", "corte", "zoom"]     # referencia 3: casi siempre corte o fundido por negro
    EST = [2, 0, 2, 2, 0, 2, 5, 2, 0, 3, 2, 1]                          # teal/cian y ambar dominan; rojo/verde/magenta solo de vez en cuando
    TEMAS_C = ["rojo", "azul", "verde", "morado", "amarillo", "oscuro"]
    ncomp = 0
    for k_, e_ in enumerate(escenas):
        e_["trans"] = "rgb" if e_["tipo"] == "titular" else ciclo[k_ % len(ciclo)] if e_["tipo"] != "blender" else ciclo[e_.get("seed", 0) % len(ciclo)]
        e_["est"] = EST[(k_ * 5 + 3) % len(EST)] if k_ else 0
        if e_["tipo"] == "titular": e_["lay"] = (k_ // 2) % 5
        if e_["tipo"] == "dato": e_["lay"] = (k_ // 2) % 3
        if e_["tipo"] == "foto": e_["marco"] = (k_ // 3) % 4
        if e_["tipo"] == "roja": e_["est"] = [1, 2, 3, 4, 5, 0][k_ % 6]
        if e_["tipo"] == "comparar":
            if ncomp >= 2: e_["tema"] = TEMAS_C[ncomp % len(TEMAS_C)]
            e_["lay"] = [0, 2, 1, 2, 0, 1][ncomp % 6]                        # el segundo ya NO repite el primero: diseños distintos (lado a lado / mitades en diagonal / filas)
            ncomp += 1
        if e_["tipo"] == "3d":
            e_["calidad"] = "alta" if inicios[k_] < 300 else "normal"
            if inicios[k_] >= 300: e_["rf"] = 2                                   # despues de los 5 min: se renderiza a 15 fps y se interpola a 30 (render ~2x mas rapido)
    mp3 = os.path.join(pub, "mezcla.mp3")
    segs = [(inicios[i], (inicios[i + 1] if i + 1 < len(inicios) else dur), escenas[i].get("luz", "media")) for i in range(len(escenas))]
    D = mezclar(audio, inicios, golpes, mp3, segs, escenas=escenas)
    props = {"escenas": escenas, "voz": f"{a.proyecto}/mezcla.mp3"}
    ruta = os.path.join(a.salida, f"props_{a.proyecto}.json"); json.dump(props, open(ruta, "w"), ensure_ascii=False, indent=1)
    print(f"LISTO: {len(escenas)} escenas, audio {D / 60:.1f} min -> {ruta}")
    print("Siguiente: cd ../video && npx remotion render src/index.ts Historia out/prueba4.mp4 --props=props_prueba4.json --scale=0.5 --concurrency=4")


if __name__ == "__main__":
    main()
