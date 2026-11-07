"""Reglas para que LO QUE DICE EL NARRADOR aparezca en pantalla en ese momento (regla fija del usuario): palabras clave -> objeto 3D / sala 3D / inserto.
Cada regla: (regex sobre el texto normalizado sin acentos, [candidatos en orden de preferencia]). 'R:fam' = siguiente plano sin usar de esa sala."""
import re, unicodedata

def norm(s):
    return re.sub(r"[^a-z0-9%$ ]", " ", "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn"))

VISUAL = [
    (r"televis|\btele\b|serie\b|pelicula|\bsala\b|salon|sofa|ver una|enciende|noche", ["R:hogar", "caja_tv", "tv_play"]),
    (r"\bcaja|cajita|cajas|streaming|android|decodificador", ["caja_tv", "caja_led", "R:hogar", "hdmi"]),
    (r"\bluz\b|lucecita|parpade|\bled\b|brill", ["caja_led", "R:hogar"]),
    (r"laptop|computador|ordenador|portatil|maquina", ["contagio", "R:lab", "pc_antiguo"]),
    (r"router|modem|wifi", ["router", "R:hogar", "antena"]),
    (r"camara|grabador|vigil|seguridad", ["camara", "R:srv", "radar"]),
    (r"contrasena|clave|password|credencial", ["password", "candado", "llave"]),
    (r"cerradura|\bllave\b|puerta|agujero|entrar|entrada|acceso|abrir", ["llave", "puerta", "candado_agujero", "password"]),
    (r"candado|protege|proteccion|bloquea|segura", ["candado", "escudo"]),
    (r"millones|planeta|mundo|paises|todo el|globo|kimwolf|infectad|repartid|miles de", ["R:map", "globo", "casas_red"]),
    (r"ventanas|hogares|casas|departamentos|oficinas|vecin|domicilio", ["casas_red", "R:map", "R:hogar"]),
    (r"servidor|centro de datos|dns|\bdyn\b|avalancha|peticion|ataque|atacar|saturad|tumb", ["R:srv", "avalancha", "rack"]),
    (r"apagon|se cae|caida|desaparec|nada carga|colaps|no carga|apaga", ["apagon", "pantalla_rota", "R:srv"]),
    (r"internet|conexion|\bred\b|redes|conectad|conectar", ["red", "cable", "R:srv", "router"]),
    (r"cable|hdmi|enchuf|enchufa|conecta el", ["cable", "hdmi"]),
    (r"fabrica|fabricante|cinta|paquete|envio|se instal|de fabrica|montaje|cadena de montaje", ["R:fab", "fabrica", "paquetes"]),
    (r"dinero|dolar|precio|cuesta|barat|pagar|pagan|vend|reven|alquil|negocio|comprar|compro", ["dinero", "R:fab", "paquetes"]),
    (r"calendario|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|otono|20[0-3][0-9]|19[89][0-9]", ["calendario", "reloj", "R:ofi"]),
    (r"reloj|minuto|segundo|\bhoras?\b|dias|velocidad|rapid|lent|tiempo|diez", ["reloj", "latido", "manometro"]),
    (r"gusano|duplica|copia|copiar|copiarse|replic|multipl|reproduc|contagi|infecta|propag|cada ocho", ["duplicacion", "contagio", "dominos", "R:lab"]),
    (r"virus|codigo|programa|escrito|escribir|software|malware|instruccion|comando|truco", ["codigo", "intrusion", "pc_antiguo", "R:lab"]),
    (r"laboratorio|experimento|investigador|prueba|medir|midieron|cornell|anthropic|demostracion|estudiante|universidad", ["R:lab", "lupa", "manometro"]),
    (r"inteligencia artificial|modelo|\bia\b|asistente|agente|piensa|parametros|decide|entiende|aprend", ["placa", "R:srv", "engranajes", "escudo"]),
    (r"correo|mensaje|email|texto|escrito para", ["movil", "contagio", "R:ofi"]),
    (r"telefono|movil|celular", ["movil"]),
    (r"investig|descubr|detect|encontr|buscar|busca|explor|analiz|mira a su|averigu|mide|calculo|cuenta", ["lupa", "radar", "R:ofi"]),
    (r"error|falla|fallo|rota|roto|bloque|se apagan|lentas|quedaron fuera", ["pantalla_rota", "manometro", "apagon"]),
    (r"miedo|peligro|riesgo|alerta|amenaza|cerca|incomod|temer|inquiet", ["escudo", "latido", "manometro"]),
    (r"memoria|gigabyte|quince|pedazos|trozos|cortaron|cadena|fragment", ["cajas15", "placa", "engranajes", "R:fab"]),
    (r"porcentaje|por ciento|%|numero|cifra|sube|crece", ["manometro", "latido"]),
    (r"estanteria|tienda|comprar una|supermercado|almacen|vender", ["estanteria", "R:fab"]),
    (r"engranaje|pieza|mecanismo|funciona|sistema", ["engranajes", "placa"]),
    (r"antena|senal|radio|torre|satelite|onda", ["antena", "radar", "R:map"]),
    (r"archivo|documento|registro|informe|publico|publicaron|empresa|seguridad de|equipo de", ["R:ofi", "calendario", "lupa"]),
    (r"mando|control remoto|elegir", ["mando", "tv_play"]),
]
INSERTO = [
    ("radar", r"buscar|busca|encontr|detect|vigil|explor|mira a su|entiende|averigu|descubr|investig|rastr"),
    ("globo2d", r"mundo|planeta|millones|paises|todo el|repartid|global|miles de"),
    ("roja", r"conexion|internet|casa|router|proxy|alquil|reven|red de invitados|puerta"),
    ("flujo", r"contagi|infecta|copia|propag|replic|duplic|siguiente|vecin|cadena|gusano|red\b"),
    ("terminal", r"codigo|programa|comando|escrito|instruccion|software|escribe|ejecut|terminal"),
    ("barras", r"avalancha|peticion|ataque|saturad|pico|trafico|velocidad|crece|sube|exponencial"),
]
# categorias de fotos de lugar para fondos de titulares/cifras segun la sala o tema
FOTO_SALA = {"hogar": ["sala"], "lab": ["aula", "oficina_casa"], "srv": ["datacenter", "pasillo"], "map": ["ventana_noche", "calle_noche"], "ofi": ["oficina_casa", "biblioteca"], "fab": ["fabrica", "centro_comercial"]}

def puntuar(texto):
    t = norm(texto); sc = {}
    for rx, cands in VISUAL:
        n = len(re.findall(rx, t))
        if n:
            for i, c in enumerate(cands): sc[c] = sc.get(c, 0.0) + n * (1 - 0.12 * i)
    return sc

def inserto_para(texto):
    t = norm(texto); mejor = []
    for k, rx in INSERTO:
        n = len(re.findall(rx, t))
        if n: mejor.append((n, k))
    return [k for _, k in sorted(mejor, reverse=True)]
