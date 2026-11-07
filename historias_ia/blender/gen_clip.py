#!/usr/bin/env python3
"""Genera UN clip de Blender (Cycles, fotorrealista) segun un JSON: {"prop","seed","dur","fps","samples","res":[w,h],"salida"}  -> salida/f_0001.png ...
Mesa de madera con texturas PBR reales (Poly Haven, CC0), HDRI de interior muy tenue de fondo (bokeh), luz calida de lampara + acento cian, camara macro con profundidad de campo."""
import bpy, math, os, sys, json, random
from mathutils import Vector
spec = json.load(open(sys.argv[sys.argv.index("--") + 1])) if "--" in sys.argv else json.load(open(sys.argv[1]))
A = os.environ.get("ASSETS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))
R = random.Random(spec["seed"]); prop = spec["prop"]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = spec.get("samples", 24); sc.cycles.use_denoising = True; sc.cycles.max_bounces = spec.get("bounces", 4)
sc.render.resolution_x, sc.render.resolution_y = spec.get("res", [960, 540]); sc.render.resolution_percentage = 100
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
sc.view_settings.look = "None"; sc.cycles.preview_samples = 8
sc.cycles.adaptive_threshold = spec.get("adapt", 0.01); sc.cycles.sample_clamp_indirect = spec.get("clamp", 10); sc.cycles.use_adaptive_sampling = True
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.render.use_persistent_data = True
try: sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.denoising_prefilter = "ACCURATE"
except Exception: pass
HDRIS = ["abandoned_workshop", "abandoned_garage", "boiler_room", "bank_vault", "carpentry_shop_01", "art_studio", "cabin", "abandoned_tiled_room", "autoshop_01", "burnt_warehouse", "abandoned_bakery", "blinds", "abandoned_games_room_02"]
MAD = ["brown_planks_03", "brown_planks_04", "brown_planks_05", "black_painted_planks", "brown_planks_07"]

def mat(nombre, color, rough=0.5, metal=0.0, emis=None, fuerza=0.0):
    m = bpy.data.materials.new(nombre); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emis is not None: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = fuerza
    return m
def caja(nombre, size, loc, m, bisel=0.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = nombre; o.scale = size; bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("b", "BEVEL"); bv.width = bisel; bv.segments = 3; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def cil(nombre, r, h, loc, m, rot=(0, 0, 0), seg=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=seg); o = bpy.context.object; o.name = nombre; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def esfera(nombre, r, loc, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16); o = bpy.context.object; o.name = nombre; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

# ---------- mundo ----------
hd = R.choice(HDRIS); w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value[2] = R.uniform(0, 6.28)
env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(f"{A}/{hd}.hdr"); bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = R.uniform(0.06, 0.16)
out = nt.nodes.new("ShaderNodeOutputWorld"); nt.links.new(tc.outputs["Generated"], mp.inputs[0]); nt.links.new(mp.outputs[0], env.inputs[0]); nt.links.new(env.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
# ---------- mesa ----------
bpy.ops.mesh.primitive_plane_add(size=6); mesa = bpy.context.object
tx = R.choice(MAD); m = bpy.data.materials.new("madera"); m.use_nodes = True; n = m.node_tree.nodes; l = m.node_tree.links; b = n["Principled BSDF"]
mpp = n.new("ShaderNodeMapping"); mpp.inputs["Scale"].default_value = (3, 3, 3); tcc = n.new("ShaderNodeTexCoord"); l.new(tcc.outputs["UV"], mpp.inputs[0])
def tex(nombre, cs):
    t = n.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(f"{A}/{tx}/{nombre}.jpg"); t.image.colorspace_settings.name = cs; l.new(mpp.outputs[0], t.inputs[0]); return t
d = tex("Diffuse", "sRGB"); r = tex("Rough", "Non-Color"); nm = tex("nor_gl", "Non-Color"); nmn = n.new("ShaderNodeNormalMap")
l.new(d.outputs[0], b.inputs["Base Color"]); l.new(r.outputs[0], b.inputs["Roughness"]); l.new(nm.outputs[0], nmn.inputs["Color"]); l.new(nmn.outputs[0], b.inputs["Normal"]); mesa.data.materials.append(m)

def gltf(nombre, x, y, rot=0, esc=1.0):
    bpy.ops.import_scene.gltf(filepath=f"{A}/{nombre}/{nombre}_1k.gltf"); ob = list(bpy.context.selected_objects)
    root = bpy.data.objects.new(nombre + "_g", None); bpy.context.collection.objects.link(root)
    for o in [o for o in ob if o.parent is None]: o.parent = root
    root.scale = (esc, esc, esc); root.rotation_euler[2] = math.radians(rot); bpy.context.view_layer.update()
    def bb():
        pts = []
        for o in [root] + list(root.children_recursive):
            if o.type == "MESH": pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
        return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    lo, hi = bb(); c = (lo + hi) / 2; root.location.x += x - c.x; root.location.y += y - c.y; root.location.z -= lo.z; bpy.context.view_layer.update()
    lo, hi = bb(); return root, (hi - lo)

CIAN = (0.2, 0.85, 1.0); AMB = (1.0, 0.62, 0.3)
tam = 0.3; foco = Vector((0, 0, 0.06)); decor = []
def router():
    global tam, foco
    cu = mat("cuerpo", (0.02, 0.022, 0.026), 0.25, 0.4); caja("router", (0.32, 0.19, 0.035), (0, 0, 0.0175), cu, 0.006)
    for i, x in enumerate((-0.11, 0, 0.11)): cil(f"ant{i}", 0.006, 0.26, (x, -0.07, 0.15), mat("ant", (0.01, 0.01, 0.012), 0.4), (math.radians(8 * (i - 1)), 0, math.radians(6 * (i - 1))))
    for i in range(5): caja(f"led{i}", (0.008, 0.004, 0.004), (-0.1 + i * 0.05, 0.096, 0.02), mat("led", (0, 0, 0), 0.3, emis=(CIAN if i % 3 == 0 else (0.2, 1.0, 0.5)), fuerza=60))
    for i, c in enumerate(((0.1, 0.3, 1.0), (0.9, 0.8, 0.1), (0.1, 0.3, 1.0))): cil(f"cab{i}", 0.004, 0.5, (-0.08 + i * 0.08, 0.34, 0.012), mat("cab", c, 0.5), (math.radians(90), 0, 0), 12)
    tam = 0.34; foco = Vector((0, 0.0, 0.03))
def cajas():
    global tam, foco
    n = R.randint(8, 14); cu = mat("caja", (0.015, 0.016, 0.018), 0.3, 0.3)
    for i in range(n):
        x = (i - (n - 1) / 2) * 0.19; caja(f"b{i}", (0.14, 0.095, 0.028), (x, 0, 0.014), cu, 0.004)
        caja(f"l{i}", (0.008, 0.004, 0.004), (x - 0.04, 0.049, 0.02), mat("led", (0, 0, 0), 0.3, emis=CIAN if R.random() > 0.2 else (0.1, 0.4, 0.4), fuerza=70))
        for k, c in enumerate(((0.1, 0.3, 1.0), (0.9, 0.8, 0.1))): cil(f"c{i}{k}", 0.003, 0.5, (x + (k - 0.5) * 0.02, 0.28, 0.006), mat("cab", c, 0.5), (math.radians(90), 0, 0), 10)
    tam = 0.5; foco = Vector((0, 0, 0.03))
def robot():
    global tam, foco
    cu = mat("rob", (0.62, 0.64, 0.68), 0.28, 0.6); osc = mat("osc", (0.02, 0.02, 0.025), 0.2, 0.4); ojo = mat("ojo", (0, 0, 0), 0.3, emis=CIAN, fuerza=140)
    caja("torso", (0.17, 0.10, 0.19), (0, 0, 0.19), cu, 0.012); caja("pecho", (0.09, 0.004, 0.06), (0, 0.052, 0.21), mat("pan", (0.01, 0.02, 0.03), 0.2, emis=CIAN, fuerza=6), 0.002)
    cil("cuello", 0.02, 0.05, (0, 0, 0.31), osc)
    head = bpy.data.objects.new("cab_g", None); bpy.context.collection.objects.link(head); head.location = (0, 0, 0.355); bpy.context.view_layer.update()
    h = caja("cabeza", (0.15, 0.12, 0.11), (0, 0, 0.355), cu, 0.012); v = caja("visor", (0.12, 0.004, 0.05), (0, 0.062, 0.36), osc, 0.003)
    e1 = esfera("ojo1", 0.011, (-0.03, 0.065, 0.36), ojo); e2 = esfera("ojo2", 0.011, (0.03, 0.065, 0.36), ojo); an = cil("antena", 0.003, 0.07, (0, 0, 0.44), osc); pu = esfera("punta", 0.008, (0, 0, 0.48), ojo)
    for o in (h, v, e1, e2, an, pu): o.parent = head; o.matrix_parent_inverse = head.matrix_world.inverted()
    nf = spec["frames"]; head.rotation_euler = (0, 0, math.radians(-18)); head.keyframe_insert("rotation_euler", frame=1); head.rotation_euler = (0, 0, math.radians(18)); head.keyframe_insert("rotation_euler", frame=nf)
    for s in (-1, 1):
        cil(f"brazo{s}", 0.018, 0.17, (s * 0.115, 0, 0.19), cu, (0, math.radians(s * 10), 0)); esfera(f"hom{s}", 0.026, (s * 0.105, 0, 0.275), osc)
        cil(f"pierna{s}", 0.025, 0.12, (s * 0.045, 0, 0.06), osc); caja(f"pie{s}", (0.06, 0.09, 0.025), (s * 0.045, 0.015, 0.0125), cu, 0.006)
    tam = 0.62; foco = Vector((0, 0.04, 0.30))
def telefono():
    global tam, foco
    caja("tel", (0.072, 0.152, 0.009), (0, 0, 0.0045), mat("tel", (0.01, 0.01, 0.012), 0.2, 0.5), 0.004, (0, 0, math.radians(R.uniform(-30, 30))))
    caja("pant", (0.066, 0.145, 0.0005), (0, 0, 0.0095), mat("pant", (0.02, 0.1, 0.14), 0.2, emis=CIAN, fuerza=2.2), 0.0005, (0, 0, math.radians(R.uniform(-30, 30)))); tam = 0.17; foco = Vector((0, 0, 0.01))
def llave():
    global tam, foco
    oro = mat("oro", (0.8, 0.55, 0.2), 0.25, 1.0); caja("placa", (0.2, 0.012, 0.2), (0, 0, 0.1), mat("pl", (0.03, 0.025, 0.02), 0.4), 0.006)
    cil("cerr", 0.045, 0.02, (0, -0.012, 0.1), oro, (math.radians(90), 0, 0)); cil("ojo", 0.008, 0.03, (0, -0.02, 0.1), mat("neg", (0, 0, 0), 0.5), (math.radians(90), 0, 0), 16)
    cil("llav", 0.005, 0.1, (0.012, -0.075, 0.095), oro, (math.radians(90), 0, math.radians(8))); bpy.ops.mesh.primitive_torus_add(location=(0.02, -0.14, 0.092), major_radius=0.022, minor_radius=0.006, rotation=(math.radians(90), 0, 0)); bpy.context.object.data.materials.append(oro)
    tam = 0.3; foco = Vector((0, -0.04, 0.1))
def modelos(prin, extra=()):
    global tam, foco
    root, dim = gltf(prin[0], 0, 0, R.uniform(-35, 35), prin[1]); tam = max(dim.x, dim.y, dim.z); foco = Vector((0, 0, dim.z * 0.5))
    for nom, x, y, rot, esc in extra: gltf(nom, x, y, rot, esc)
PRIN = {"reloj": ("alarm_clock_01", 1.0), "laptop": ("classic_laptop", 1.0), "camara": ("security_camera_01", 1.0), "tv": ("Television_01", 1.0), "radio": ("vintage_radio_transceiver", 1.0), "libros": ("book_encyclopedia_set_01", 1.0), "cables": ("modular_electric_cables", 1.0), "lampara": ("desk_lamp_arm_01", 1.0), "telepublico": ("korean_public_payphone_01", 1.0), "cassette": ("portable_cassette_player", 1.0)}
if prop in PRIN:
    extras = []
    if prop in ("reloj", "libros", "radio", "cassette"): extras = [("desk_lamp_arm_01", -0.45, 0.35, R.uniform(0, 60), 1.0)]
    if prop == "laptop": extras = [("alarm_clock_01", 0.55, -0.1, R.uniform(-40, 10), 1.0)]
    modelos(PRIN[prop], extras)
else:
    {"router": router, "cajas": cajas, "robot": robot, "telefono": telefono, "llave": llave}[prop]()
    if R.random() > 0.4: gltf("alarm_clock_01", R.choice((-1, 1)) * (tam * 0.9 + 0.2), 0.12, R.uniform(-60, 60), 1.0)

# ---------- luces ----------
lx = R.choice((-1, 1)); bpy.ops.object.light_add(type="SPOT", location=(lx * (tam + 0.25), 0.05, 0.28 + tam * 0.4)); sp = bpy.context.object
sp.data.energy = R.uniform(70, 130); sp.data.color = R.choice([AMB, (1.0, 0.74, 0.45), (1.0, 0.5, 0.25)]); sp.data.spot_size = math.radians(110); sp.data.spot_blend = 0.9; sp.data.shadow_soft_size = 0.06
tg = bpy.data.objects.new("lt", None); bpy.context.collection.objects.link(tg); tg.location = foco; c = sp.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
bpy.ops.object.light_add(type="AREA", location=(-lx * (tam + 0.35), -0.45, 0.22)); ac = bpy.context.object; ac.data.energy = R.uniform(6, 14); ac.data.color = CIAN if R.random() > 0.3 else (0.6, 0.5, 1.0); ac.data.size = 0.4
c2 = ac.constraints.new("TRACK_TO"); c2.target = tg; c2.track_axis = "TRACK_NEGATIVE_Z"; c2.up_axis = "UP_Y"
# ---------- camara macro ----------
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.lens = R.choice((35, 40, 50)); cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = R.uniform(1.4, 2.2)
ft = bpy.data.objects.new("ft", None); bpy.context.collection.objects.link(ft); ft.location = foco; cam.data.dof.focus_object = ft
tr = cam.constraints.new("TRACK_TO"); tr.target = ft; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
nf = spec["frames"]; sc.frame_start = 1; sc.frame_end = nf; d0 = tam * R.uniform(2.2, 3.0); d1 = d0 * R.uniform(0.5, 0.75); k = R.randint(0, 4)
ang0 = math.radians(R.uniform(-55, 55)); ang1 = ang0 + math.radians(R.uniform(-25, 25)) * (1 if k in (2, 3) else 0.3); h0 = tam * R.uniform(0.18, 0.5); h1 = h0 * R.uniform(0.6, 1.4)
if k == 1: d0, d1 = d1, d0                                                         # retroceso
if k == 4: h0, h1 = tam * 0.9, tam * 0.15                                           # bajada
def pos(d, a, h): return Vector((foco.x + math.sin(a) * d, foco.y - math.cos(a) * d, max(0.03, h + foco.z * 0.3)))
cam.location = pos(d0, ang0, h0); cam.keyframe_insert("location", frame=1); cam.location = pos(d1, ang1, h1); cam.keyframe_insert("location", frame=nf)
os.makedirs(spec["salida"], exist_ok=True)
for fr in range(1, nf + 1):
    sc.frame_set(fr); sc.render.filepath = f"{spec['salida']}/f_{fr:04d}.png"; bpy.ops.render.render(write_still=True)
print("LISTO", prop, nf, "cuadros", flush=True)
