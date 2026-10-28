#!/usr/bin/env python3
"""Genera la lista de PROMPTS de ImageFX (Google Labs) para el video completo: una imagen por cada hueco de 'foto' que el planificador va a intercalar.
Salida: ../IMAGENES_IMAGEFX_PROMPTS.md. Archivos esperados: video/public/fotos_fx/b<bloque>_<k>.jpg (el planificador los usa primero si existen).
Uso: python3 prompts_imagefx.py"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prueba_4min as P

VEL = 2.47                                           # palabras/segundo de Martin (medido en la prueba de 4 min)
ESTILO = "photorealistic photograph, natural bright lighting, sharp focus, high detail, shallow depth of field, 16:9, no people, no text, no logos"
V = {  # objeto 3D -> variantes de foto real (distintas para que no se repitan)
 "sala": ["cozy living room at dusk, sofa facing a large TV, lamp on, warm light", "modern apartment living room with TV on a stand and a router on the shelf", "empty family living room with a flat screen TV and a coffee table"],
 "caja_tv": ["black android TV box with remote next to a television, close up", "cheap streaming box plugged into the back of a TV, HDMI cable, macro", "unbranded TV box on a wooden shelf with small blinking LED"],
 "caja_led": ["streaming box with a tiny glowing LED in a dim living room, macro", "TV box with blinking green light, shallow depth of field", "set-top box standby LED close up on a media console"],
 "reloj": ["analog wall clock in a quiet kitchen at night, close up", "digital alarm clock showing 3:00 in a dark bedroom, red numbers", "vintage desk clock on a wooden table in morning light"],
 "ojo": ["security dome camera lens close up, reflection of a hallway", "extreme close up of a camera lens with blue reflections", "doorbell camera glowing at night on a front door"],
 "intrusion": ["laptop open on a desk showing code on screen in a dark room", "hand-free close up of a keyboard with reflection of code on a monitor", "home office desk at night with two monitors showing terminal windows"],
 "contagio": ["row of laptops on a long table in a computer lab", "several smartphones and laptops connected by cables on a desk", "office with rows of desktop computers, all screens lit"],
 "dominos": ["long line of dominoes starting to fall, macro, soft light", "dominoes in a chain on a wooden floor, one tipping", "colorful dominoes lined up on a table, shallow depth of field"],
 "nucleo": ["microchip processor close up on a motherboard, macro", "CPU socket with golden contacts, macro photography", "glowing circuit traces on a green circuit board, macro"],
 "engranajes": ["interlocking metal gears of a mechanical watch, macro", "large rusty gears in an old machine, side light", "brass gears and cogs on a workbench"],
 "placa": ["green circuit board with chips and capacitors, macro", "motherboard with heat sinks on a clean white table", "open computer case showing components, soft light"],
 "manometro": ["analog pressure gauge with needle in red zone, industrial", "old dial gauge on a pipe in a factory, close up", "speedometer needle close up, car dashboard"],
 "lupa": ["magnifying glass over a printed document on a desk", "antique magnifying glass on a wooden desk, morning light", "detective's magnifier over a map and notes"],
 "escudo": ["heavy steel vault door, closed, cold light", "padlock on a metal gate, close up", "security shield sticker on a laptop, macro"],
 "globo": ["vintage world globe on a desk, warm light", "earth globe in a classroom by a window", "illuminated globe in a dark study, softly lit"],
 "casas_red": ["suburban houses at night with lit windows, aerial view", "rows of apartment windows lit up at dusk", "city neighborhood at night from a hill, glowing windows"],
 "antena": ["cell tower against a blue sky, low angle", "satellite dish on a rooftop at sunset", "radio mast and antennas on a hill at dawn"],
 "estanteria": ["electronics store shelf full of boxes of TV streaming devices", "supermarket aisle with cheap gadgets on shelves", "online store parcels stacked on a shelf"],
 "hdmi": ["HDMI cable plugged into a TV back panel, macro", "HDMI connector close up on white surface", "tangle of HDMI and power cables behind a television"],
 "tv_play": ["television screen showing a movie menu with colorful thumbnails (no readable text)", "remote control in front of a TV with a movie paused", "TV glowing in a dark living room"],
 "nube": ["server cloud storage data center aisle, blue light", "dramatic storm cloud over a city skyline", "fiber optic cables glowing blue, macro"],
 "fabrica": ["factory conveyor belt with cardboard boxes, wide angle", "automated assembly line in a warehouse, bright light", "packages moving on a conveyor belt in a logistics center"],
 "paquetes": ["stack of cardboard parcels in a warehouse", "boxes on a conveyor belt close up", "delivery packages on a doorstep"],
 "dinero": ["stack of US dollar bills on a table, close up", "banknotes fanned out on a dark surface", "coins and bills in a jar, soft light"],
 "password": ["sticky note with a password on a monitor edge (blurred text)", "keyboard close up with a lock icon sticker", "login screen glowing on a laptop in a dark room, no readable text"],
 "candado": ["padlock on a chain, close up, bright light", "open padlock on a wooden table", "rusty padlock on an old door"],
 "candado_agujero": ["keyhole close up in a metal door, light coming through", "old key in a lock, macro", "door lock with a gap showing light"],
 "puerta": ["open door in a dark hallway with light spilling in", "front door slightly ajar at night", "long corridor with a door at the end"],
 "avalancha": ["huge crowd of cars on a highway at night, long exposure", "server racks with thousands of blinking lights, wide angle", "waterfall of data cables in a data center"],
 "apagon": ["city skyline during a blackout, dusk", "dark room with a single glowing screen", "power outage street at night, lights off in apartments"],
 "latido": ["heart rate monitor line on a screen, hospital, blurred background", "traffic light blinking amber at night, long exposure", "old oscilloscope showing a green wave"],
 "llave": ["old brass key on a wooden table, macro", "bunch of keys hanging in a lock", "modern key card and a door reader, close up"],
 "cable": ["ethernet cables plugged into a network switch, macro", "tangled network cables behind a desk", "patch panel with blue network cables"],
 "router": ["white wifi router with blinking lights on a shelf, close up", "router with antennas in a living room corner", "black wireless router on a desk, shallow depth of field"],
 "camara": ["security camera mounted on a wall, close up", "CCTV camera on a building corner against the sky", "indoor security camera on a shelf"],
 "rack": ["server rack with network cables and blinking LEDs", "data center aisle between server cabinets, blue light", "network switch ports with cables, macro"],
 "codigo": ["lines of code on a monitor in a dark room, blurred", "close up of a keyboard and code reflected in glasses (no person)", "terminal window with green text on a black screen"],
 "pc_antiguo": ["1980s beige personal computer with green phosphor monitor", "old CRT computer on a desk in a university lab", "vintage floppy disks next to an old keyboard"],
 "duplicacion": ["identical rubber ducks in a row, macro", "mirror reflections repeating in a long hall", "rows of identical servers, perspective view"],
 "pantalla_rota": ["cracked smartphone screen, macro", "broken monitor with colorful glitch lines", "shattered glass screen with light leaking"],
 "red": ["network switch with fiber cables glowing, macro", "globe of connected lights over a night city, long exposure", "tangle of fiber optic cables with light"],
 "radar": ["radar dish on a hill at sunset", "airport control tower at dusk", "green radar screen in a dark room, no readable text"],
 "cajas15": ["wall of identical cardboard boxes in a warehouse", "fifteen small boxes lined up on a shelf", "chain of cargo containers in a port"],
 "movil": ["smartphone lying on a wooden table, close up, screen off", "phone charging on a nightstand", "phone with notification light glowing in the dark"],
 "calendario": ["wall calendar with a date circled in red", "desk calendar page close up, soft light", "paper calendar on a kitchen wall"],
 "mando": ["TV remote control on a sofa, close up", "remote control and a TV box on a table", "universal remote with backlit buttons in the dark"],
 "usb": ["usb flash drives scattered on a desk, macro", "usb stick plugged into a laptop port, close up", "memory card and usb on a white table"],
}
DEF = ["server room with blinking lights, wide angle", "laptop on a desk in a dark room, glowing screen", "city at night with lit windows"]
TIT = {  # titulares que sugieren una foto de 'epoca' o ambiente
 "1988": "1988-style computer lab with beige computers and CRT monitors", "2016": "2016 home office with a laptop, router and a smart camera",
 "2003": "2003 era computer lab with CRT monitors and cables", "ENERO": "winter morning view from an office window with a laptop on the desk",
}


def main():
    bloques = P.leer_bloques(10 ** 6)
    usos = {}; salida = []; n_tot = 0
    for bi, (tag, ls) in enumerate(bloques):
        base = P.escena_de(tag); tipo = base["tipo"]; palabras = sum(len(l.split()) for l in ls); dur = palabras / VEL
        if tipo == "3d": ta, objs = 0.0, base["objetos"]
        elif tipo == "titular": ta, objs = 4.5, base.get("_relleno", [])
        else: ta, objs = 8.0, []
        total = dur - ta
        if total < 1.0: continue
        n_f = 0; x = 0.0; i = 0                                      # misma logica de alternancia 3D(3 s)/foto(2,2 s) que el planificador
        while x < total - 0.01:
            d = P.DUR_3D if i % 2 == 0 else P.DUR_FOTO
            if total - x - d < 1.3: d = total - x
            if i % 2 == 1 and d >= 1.0: n_f += 1
            x += d; i += 1
        slots = []
        for k in range(n_f):
            o = objs[k % len(objs)] if objs else "x"
            o = P.FAMILIA.get(o, o); lst = V.get(o, DEF); u = usos.get(o, 0); usos[o] = u + 1
            slots.append((o, lst[u % len(lst)] + ("" if u < len(lst) else ", different angle")))
        if not slots: continue
        salida.append((bi, tag, ls, slots)); n_tot += len(slots)
    md = ["# Prompts de ImageFX — IA DESCONTROLADA: 'Los virus informáticos de IA ya casi están aquí'", "",
          f"**{n_tot} imágenes** (una por cada hueco de foto del video). Pega cada prompt en ImageFX, elige la imagen más realista, descárgala y guárdala con el nombre indicado en `video/public/fotos_fx/`.",
          f"Todas terminan con: *{ESTILO}*. Sin personas ni texto (así no hay caras raras ni letras deformadas). Formato 16:9.", "",
          "> Si una imagen sale mal, repite el prompt; el nombre del archivo es lo único que importa. Si no genera alguna, el planificador usa una foto real del banco de fotos.", ""]
    for bi, tag, ls, slots in salida:
        md.append(f"## Bloque {bi + 1} — {re.sub(r'<.*', '', tag)[:80]}"); md.append(f"> {ls[0][:150]}{'…' if len(ls[0]) > 150 else ''}"); md.append("")
        for k, (o, p) in enumerate(slots, 1): md.append(f"- `b{bi + 1:02d}_{k}.jpg` — {p}, {ESTILO}")
        md.append("")
    ruta = os.path.join(P.RAIZ, "IMAGENES_IMAGEFX_PROMPTS.md"); open(ruta, "w", encoding="utf-8").write("\n".join(md))
    print(f"{n_tot} prompts en {len(salida)} bloques -> {ruta}")


if __name__ == "__main__":
    main()
