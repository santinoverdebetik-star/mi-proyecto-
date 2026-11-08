#!/usr/bin/env python3
"""Baja de Poly Haven (CC0, https://polyhaven.com) los modelos, texturas y HDRIs que usa gen_clip.py -> blender/assets/ (no se sube a git)."""
import json, os, urllib.request
AQUI = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(AQUI, "assets")
def get(u, dest=None):
    d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "IA-Descontrolada/1.0"}), timeout=120).read()
    if dest: os.makedirs(os.path.dirname(dest), exist_ok=True); open(dest, "wb").write(d)
    return d
for m in ["alarm_clock_01", "classic_laptop", "desk_lamp_arm_01", "security_camera_01", "Television_01", "vintage_radio_transceiver", "modular_electric_cables", "book_encyclopedia_set_01", "mantel_clock_01", "wall_clock", "korean_public_payphone_01", "portable_cassette_player"]+["Camera_01", "boombox", "cassette_player", "binoculars", "magnifying_glass_01", "retro_multimeter", "security_camera_02", "television_02", "vintage_video_camera", "filmstrip_projector_8mm", "signal_flashlight", "vintage_flashlight", "metal_toolbox", "screwdriver", "power_box_01", "utility_box_01", "seadogs_compass", "vintage_suitcase", "vintage_stapler", "binder_notebook", "Megaphone_01", "Lantern_01", "wooden_crate_01", "cardboard_box_01", "adjustable_wrench", "vintage_telephone_wall_clock", "pull_chain_light_socket"]:
    fl = json.loads(get(f"https://api.polyhaven.com/files/{m}")); g = fl["gltf"]["1k"]["gltf"]; base = f"{A}/{m}/"
    get(g["url"], base + os.path.basename(g["url"]))
    for rel, info in g.get("include", {}).items(): get(info["url"], base + rel)
for t in ["brown_planks_03", "brown_planks_04", "brown_planks_05", "black_painted_planks", "brown_planks_07"]:
    fl = json.loads(get(f"https://api.polyhaven.com/files/{t}"))
    for k in ("Diffuse", "Rough", "nor_gl"): get(fl[k]["1k"]["jpg"]["url"], f"{A}/{t}/{k}.jpg")
for h in ["abandoned_workshop", "abandoned_garage", "boiler_room", "bank_vault", "carpentry_shop_01", "art_studio", "cabin", "abandoned_tiled_room", "autoshop_01", "burnt_warehouse", "abandoned_bakery", "blinds", "abandoned_games_room_02"]:
    fl = json.loads(get(f"https://api.polyhaven.com/files/{h}")); get(fl["hdri"]["1k"]["hdr"]["url"], f"{A}/{h}.hdr")
print("listo")
