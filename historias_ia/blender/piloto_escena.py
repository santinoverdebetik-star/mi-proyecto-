import bpy, math, time, sys, os
A=os.path.abspath('assets')
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMPLES','28')); sc.cycles.use_denoising=True
sc.render.resolution_x=960; sc.render.resolution_y=540; sc.cycles.max_bounces=5
sc.view_settings.view_transform='Filmic' if 'Filmic' in [v.identifier for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'AgX'
# mundo: HDRI muy tenue (reflejos y bokeh de fondo)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; nt=w.node_tree; nt.nodes.clear()
env=nt.nodes.new('ShaderNodeTexEnvironment'); env.image=bpy.data.images.load(A+'/abandoned_games_room_02.hdr'); bg=nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value=0.10
out=nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(env.outputs[0],bg.inputs[0]); nt.links.new(bg.outputs[0],out.inputs[0])
# mesa de madera (textura real PBR)
bpy.ops.mesh.primitive_plane_add(size=4); mesa=bpy.context.object
m=bpy.data.materials.new('madera'); m.use_nodes=True; n=m.node_tree.nodes; l=m.node_tree.links; b=n['Principled BSDF']
mp=n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(3,3,3); tc=n.new('ShaderNodeTexCoord'); l.new(tc.outputs['UV'],mp.inputs[0])
def tex(nombre,cs):
    t=n.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(f'{A}/brown_planks_03/{nombre}.jpg'); t.image.colorspace_settings.name=cs; l.new(mp.outputs[0],t.inputs[0]); return t
d=tex('Diffuse','sRGB'); r=tex('Rough','Non-Color'); nm=tex('nor_gl','Non-Color'); nmn=n.new('ShaderNodeNormalMap')
l.new(d.outputs[0],b.inputs['Base Color']); l.new(r.outputs[0],b.inputs['Roughness']); l.new(nm.outputs[0],nmn.inputs['Color']); l.new(nmn.outputs[0],b.inputs['Normal']); mesa.data.materials.append(m)
# modelos reales (Poly Haven, CC0)
def importa(nombre,pos,rot=0,esc=1.0):
    bpy.ops.import_scene.gltf(filepath=f'{A}/{nombre}/{nombre}_1k.gltf'); ob=[o for o in bpy.context.selected_objects]
    raices=[o for o in ob if o.parent is None]
    root=bpy.data.objects.new(nombre+'_grp',None); bpy.context.collection.objects.link(root)
    for o in raices: o.parent=root
    root.location=pos; root.rotation_euler[2]=math.radians(rot); root.scale=(esc,esc,esc); return root
from mathutils import Vector
def bbox(root):
    pts=[]
    for o in [root]+list(root.children_recursive):
        if o.type=='MESH': pts+= [o.matrix_world@Vector(c) for c in o.bound_box]
    return Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts))),Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
def pon(root,x,y,rot):
    root.rotation_euler[2]=math.radians(rot); bpy.context.view_layer.update(); lo,hi=bbox(root); c=(lo+hi)/2
    root.location.x+=x-c.x; root.location.y+=y-c.y; root.location.z-=lo.z; bpy.context.view_layer.update(); lo,hi=bbox(root); print('DIM',root.name,tuple(round(v,3) for v in (hi-lo)),flush=True)
reloj=importa('alarm_clock_01',(0,0,0),0,1.0); pon(reloj,0,0,-20)
laptop=importa('classic_laptop',(0,0,0),0,1.0); pon(laptop,0.55,0.2,-32)
lampara=importa('desk_lamp_arm_01',(0,0,0),0,1.0); pon(lampara,-0.55,0.25,25)
# luces: lampara calida y acento cian
bpy.ops.object.light_add(type='SPOT',location=(-0.45,0.05,0.38)); sp=bpy.context.object; sp.data.energy=60; sp.data.color=(1.0,0.62,0.30); sp.data.spot_size=math.radians(95); sp.data.spot_blend=0.8; sp.data.shadow_soft_size=0.05
sp.rotation_euler=(math.radians(150),0,math.radians(-70))
bpy.ops.object.light_add(type='AREA',location=(0.6,-0.5,0.25)); ac=bpy.context.object; ac.data.energy=6; ac.data.color=(0.3,0.85,1.0); ac.data.size=0.4; ac.rotation_euler=(math.radians(70),0,math.radians(35))
# camara macro con profundidad de campo
bpy.ops.object.camera_add(); cam=bpy.context.object; sc.camera=cam; cam.data.lens=40; cam.data.dof.use_dof=True; cam.data.dof.aperture_fstop=1.6
tgt=bpy.data.objects.new('t',None); bpy.context.collection.objects.link(tgt); tgt.location=(0,0,0.06); cam.data.dof.focus_object=tgt
tr=cam.constraints.new('TRACK_TO'); tr.target=tgt; tr.track_axis='TRACK_NEGATIVE_Z'; tr.up_axis='UP_Y'
sc.frame_start=1; sc.frame_end=int(os.environ.get('NF','36'))
cam.location=(0.34,-0.46,0.13); cam.keyframe_insert('location',frame=1); cam.location=(0.17,-0.27,0.085); cam.keyframe_insert('location',frame=sc.frame_end)
salida=os.environ.get('OUT','/tmp/bl_pilot/f_')
os.makedirs(os.path.dirname(salida),exist_ok=True)
frames=[int(x) for x in os.environ.get('FRAMES','1').split(',')]
for fr in frames:
    sc.frame_set(fr); sc.render.filepath=f'{salida}{fr:03d}.png'; t=time.time(); bpy.ops.render.render(write_still=True); print('FRAME',fr,round(time.time()-t,1),'s',flush=True)
