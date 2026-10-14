#!/usr/bin/env python3
"""Busca en Wikimedia Commons fotos de lugares/objetos (sin caras) con licencia libre y las descarga.
Uso: python3 buscar_imagenes.py CARPETA_SALIDA
Genera CARPETA_SALIDA/*.jpg y CARPETA_SALIDA/creditos.csv (titulo, autor, licencia, pagina, consulta)."""
import csv, html, io, json, os, re, sys, time, urllib.parse, urllib.request
import cv2, numpy as np

UA = {"User-Agent": "LaCosaNuestraDraft/1.0 (video draft; images from Wikimedia Commons)"}
API = "https://commons.wikimedia.org/w/api.php"
OK_LIC = re.compile(r"^(CC0|Public domain|PD|CC BY|Copyrighted free use)", re.I)  # incluye BY-SA (se marca en creditos)
BAD_TITLE = re.compile(r"portrait|people|person|man |men |woman|women|girl|boy|child|crowd|police|soldier|"
                       r"band|concert|wedding|bride|selfie|team|player|mayor|president|senator|actor|actress|"
                       r"flag|logo|map of|diagram|coat of arms|stamp|poster|painting|drawing|illustration|"
                       r"\bsvg\b|screenshot|album|film still|movie", re.I)
# (consulta, etiqueta de bloque)
QUERIES = [
 ("New Jersey suburban street dusk", "G01"), ("residential street New Jersey night", "G01"),
 ("rain on window night", "G02"), ("car window rain night city", "G02"),
 ("empty rural road night", "G03"), ("two lane road at night taillights", "G03"),
 ("social club exterior night", "G04"), ("Italian restaurant exterior night", "G04"),
 ("empty restaurant interior booth", "G05"), ("diner interior empty", "G05"),
 ("strip mall parking lot night", "G06"), ("parking lot fog night", "G06"),
 ("New Jersey industrial waterfront", "G07"), ("Newark port cranes dawn", "G07"),
 ("chain link fence barbed wire sky", "G08"), ("barbed wire fence dusk", "G08"),
 ("butcher shop storefront", "G09"), ("pork store storefront night", "G09"),
 ("hospital corridor empty", "G10"), ("empty hallway fluorescent lights", "G10"),
 ("backyard barbecue grill sunset", "G11"), ("suburban backyard patio evening", "G11"),
 ("rotary telephone desk", "G12"), ("vintage telephone close up", "G12"),
 ("cigar ashtray smoke", "G13"), ("whiskey glass table dark", "G32"),
 ("stack of cash banknotes desk", "G14"), ("ledger accounting book desk lamp", "G14"),
 ("courtroom interior empty", "G15"), ("courthouse interior benches", "G15"),
 ("cork board pins string", "G16"), ("manila folders desk office", "G17"),
 ("typewriter desk vintage", "G17"), ("Brooklyn brownstone street morning", "G18"),
 ("highway overpass night light trails", "G19"), ("foggy forest road dawn car", "G20"),
 ("church interior candles", "G21"), ("cemetery angel statue dusk", "G22"),
 ("wooden pier dawn fog", "G23"), ("lake cabin autumn porch", "G24"),
 ("kitchen at night lamp", "G25"), ("marble steps government building", "G26"),
 ("leather briefcase table", "G27"), ("Sicily old town alley dawn", "G28"),
 ("Sicilian countryside farmhouse sunset", "G29"), ("neon lights reflected wet street night", "G30"),
 ("warehouse interior crates light rays", "G31"), ("keys on wooden table", "G32"),
 ("forest dusk fog trees", "G33"), ("airport runway dusk rain", "G34"),
 ("steakhouse exterior night New York", "G35"), ("Manhattan steakhouse exterior", "G35"),
 ("jewelry shop window night", "G36"), ("snow street night suburban", "G37"),
 ("barbershop interior", "G38"), ("railroad tracks fog", "G39"),
 ("Manhattan skyline from New Jersey dusk", "G40"), ("Hudson River skyline New Jersey waterfront", "G40"),
 ("Sicily farmhouse hillside morning", "H01"), ("Arizona desert ranch house sunset", "R5"),
 ("adobe house desert Arizona", "R5"), ("Florida retirement community street palm trees", "R8"),
 ("golf cart pond sunset", "R8"), ("swimming pool dusk empty", "R6"),
 ("lake mist dawn cabin", "R11"), ("pine forest road autumn", "R11"),
 ("butcher shop back room hooks", "R12"), ("loading dock night", "R12"),
 ("motel night sign", "R4"), ("roadside motel at night", "R4"),
 ("telephone booth night street", "R13"), ("basement room bare bulb", "R9"),
 ("stone stairway cellar", "R9"), ("candles votive church", "R9"),
 ("surveillance equipment tape recorder", "P3"), ("reel to reel tape recorder", "P3"),
 ("Senate hearing room empty", "P3"), ("New York street 1930s night wet", "P3"),
 ("boardroom table empty chairs", "R10"), ("prison watchtower dawn", "R17"),
 ("federal courthouse steps", "R16"), ("prison corridor gate", "R16"),
 ("gavel courtroom bench", "R16"), ("car crash night road ditch", "R14"),
 ("emergency flares road night", "R14"), ("apartment building door night", "R15"),
 ("clapperboard film set table", "R15"), ("city lights window night curtain", "R15"),
 ("balance scale brass coins", "C01"), ("sunrise highway empty New Jersey Turnpike", "C03"),
 ("road into fog", "C05"), ("empty chair head of table", "C06"),
 ("candle burning closed book", "C07"), ("hotel room bed night", "R19"),
 ("binoculars car dashboard", "R19"), ("wedding ring bedside", "R19"),
 ("Italian farmhouse dawn Sicily police", "H01"), ("nightclub exterior neon night", "H03"),
]
TEMAS = {
 "G01": ["suburban street dusk", "residential street night", "new jersey street"],
 "G02": ["rain window night", "rainy night street", "wet road night"],
 "G03": ["road night", "country road dusk", "highway night"],
 "G04": ["restaurant exterior night", "italian restaurant", "old club building night"],
 "G05": ["diner interior", "restaurant interior empty", "booth restaurant"],
 "G06": ["parking lot night", "strip mall night", "gas station night"],
 "G07": ["port cranes dawn", "industrial waterfront", "refinery dusk"],
 "G08": ["barbed wire fence", "chain link fence sunset"],
 "G09": ["butcher shop", "meat market storefront", "sausages hanging"],
 "G10": ["hospital corridor", "empty hallway", "fluorescent corridor"],
 "G11": ["backyard barbecue", "patio evening", "suburban house dusk"],
 "G12": ["rotary telephone", "vintage telephone", "old telephone desk"],
 "G13": ["cigar smoke", "ashtray", "whiskey glass"],
 "G14": ["cash money desk", "banknotes stack", "ledger book"],
 "G15": ["courtroom", "courthouse interior", "empty courtroom"],
 "G16": ["cork board pins", "bulletin board string"],
 "G17": ["typewriter", "manila folders", "old office desk"],
 "G18": ["brownstone street", "brooklyn street morning", "new york street fog"],
 "G19": ["overpass night", "highway light trails", "bridge night traffic"],
 "G20": ["forest road fog", "dirt road dawn fog", "car forest dawn"],
 "G21": ["church interior candles", "cathedral interior dark", "votive candles"],
 "G22": ["cemetery dusk", "graveyard statue", "cemetery fog"],
 "G23": ["pier fog", "dock dawn mist", "lake mist dawn"],
 "G24": ["cabin lake autumn", "log cabin porch", "lake house dusk"],
 "G25": ["kitchen night", "kitchen table lamp", "coffee cup table"],
 "G26": ["courthouse steps", "government building columns", "marble stairs"],
 "G27": ["briefcase", "leather bag table", "suitcase old"],
 "G28": ["sicily street", "palermo alley", "italian village narrow street"],
 "G29": ["sicily countryside", "tuscany farmhouse sunset", "italian farmhouse"],
 "G30": ["neon reflection wet street", "neon night street", "city night rain bokeh"],
 "G31": ["warehouse interior", "crates warehouse light", "loading dock"],
 "G32": ["keys table", "whiskey glass wood", "old keys"],
 "G33": ["forest dusk", "shovel tree", "dark woods fog"],
 "G34": ["runway dusk", "airport rain window", "airport night"],
 "G35": ["steakhouse", "restaurant night street", "diner night"],
 "G36": ["jewelry store window", "shop window night", "pawn shop"],
 "G37": ["snow street night", "snowy suburban night"],
 "G38": ["barbershop", "barber chair", "salon interior vintage"],
 "G39": ["railroad tracks fog", "train tracks dawn", "railway night"],
 "G40": ["manhattan skyline dusk", "new york skyline from new jersey", "hudson river skyline"],
 "R5": ["arizona desert", "adobe house desert", "desert ranch sunset"],
 "R8": ["florida palm street", "retirement community florida", "golf course sunset"],
 "R6": ["swimming pool dusk", "empty pool night"],
 "R11": ["lake dawn mist", "pine forest autumn road"],
 "R4": ["motel night", "roadside motel", "motel sign night"],
 "R13": ["phone booth", "payphone night", "telephone booth street"],
 "R9": ["basement bare bulb", "stone stairs cellar", "candle dark room"],
 "P3": ["tape recorder vintage", "reel to reel", "senate hearing room", "old new york street"],
 "R10": ["boardroom table", "conference table empty", "empty office night"],
 "R17": ["prison tower", "prison fence", "prison corridor"],
 "R14": ["car wreck night", "road flares night", "highway accident night"],
 "R15": ["apartment door", "city window night", "film clapperboard"],
 "C01": ["brass scale", "balance scale", "coins scale"],
 "C03": ["highway sunrise", "empty highway dawn", "turnpike"],
 "C05": ["road fog", "foggy road", "fog trees road"],
 "C06": ["empty chair table", "empty dining room", "head of table chair"],
 "C07": ["candle book", "candle burning dark", "candlelight"],
 "R19": ["hotel room night", "binoculars", "wedding ring", "nightclub neon"],
 "H01": ["sicily farmhouse", "hillside farmhouse dawn", "rural italy dawn"],
}
EXTRA = [(q, t) for t, qs in TEMAS.items() for q in qs]
face1 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
face2 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

def get(url, binary=False, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                d = r.read(); return d if binary else json.loads(d)
        except Exception as e:
            time.sleep(2 * (i + 1)); err = e
    raise err

def tiene_cara(img_bytes):
    a = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    if a is None: return True
    h, w = a.shape; k = 900 / max(h, w); a = cv2.resize(a, (int(w * k), int(h * k)))
    a = cv2.equalizeHist(a)
    if len(face1.detectMultiScale(a, 1.1, 4, minSize=(28, 28))): return True
    if len(face2.detectMultiScale(a, 1.1, 5, minSize=(40, 40))): return True
    if len(face2.detectMultiScale(cv2.flip(a, 1), 1.1, 5, minSize=(40, 40))): return True
    return False

def buscar(q):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q + " filetype:bitmap",
         "gsrnamespace": "6", "gsrlimit": "30", "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
         "iiurlwidth": "1920"}
    d = get(API + "?" + urllib.parse.urlencode(p))
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99)):
        ii = (pg.get("imageinfo") or [{}])[0]
        yield pg["title"], ii

def main(out, por_consulta=3):
    os.makedirs(out, exist_ok=True)
    vistos = set(); filas = []
    if os.path.exists(os.path.join(out, 'creditos.csv')):
        for f in csv.reader(open(os.path.join(out, 'creditos.csv'), encoding='utf-8')):
            vistos.add(f[1])
    for q, tag in QUERIES + EXTRA:
        n = 0
        try: cand = list(buscar(q))
        except Exception as e: print("ERR consulta", q, e); continue
        for titulo, ii in cand:
            if n >= por_consulta: break
            if titulo in vistos or not ii or ii.get("mime") != "image/jpeg": continue
            w, h = ii.get("width", 0), ii.get("height", 0)
            if w < 1600 or h < 900 or not (1.3 <= w / h <= 2.3): continue
            em = ii.get("extmetadata", {}); lic = em.get("LicenseShortName", {}).get("value", "")
            if not OK_LIC.match(lic) or BAD_TITLE.search(titulo + " " + em.get("ImageDescription", {}).get("value", "")[:200]): continue
            try: data = get(ii["thumburl"], binary=True)
            except Exception as e: print("ERR descarga", titulo, e); continue
            if tiene_cara(data): vistos.add(titulo); continue
            vistos.add(titulo)
            k = 1
            while os.path.exists(os.path.join(out, f"{tag}_{k:02d}.jpg")): k += 1
            nombre = f"{tag}_{k:02d}.jpg"
            open(os.path.join(out, nombre), "wb").write(data)
            autor = re.sub(r"<[^>]+>", "", html.unescape(em.get("Artist", {}).get("value", "?")))[:120]
            fila = [nombre, titulo, autor, lic, ii.get("descriptionurl", ""), q]; filas.append(fila); n += 1
            nuevo = not os.path.exists(os.path.join(out, "creditos.csv"))
            with open(os.path.join(out, "creditos.csv"), "a", newline="", encoding="utf-8") as fh:
                w_ = csv.writer(fh)
                if nuevo: w_.writerow(["archivo", "titulo", "autor", "licencia", "pagina", "consulta"])
                w_.writerow(fila)
            time.sleep(1.2)
        print(f"{q!r}: {n} imagenes (total {len(filas)})", flush=True); time.sleep(1.5)
    print("TOTAL", len(filas))

if __name__ == "__main__":
    main(sys.argv[1])
