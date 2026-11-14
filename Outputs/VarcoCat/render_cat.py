import bpy, sys, math
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
src,outdir=args[:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
scene=bpy.context.scene
meshes=[o for o in scene.objects if o.type=='MESH' and len(o.data.materials)]
verts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in verts) for i in range(3)))
hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
center=(lo+hi)/2
size=max(hi-lo)
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(0.22,0.24,0.28,1);bg.inputs[1].default_value=0.7
for loc,power,scale in [((2,-3,4),300,4),((-3,-1,2),200,3),((0,3,3),250,3)]:
    data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.shape='DISK';data.size=scale
    ob=bpy.data.objects.new('Softbox',data);scene.collection.objects.link(ob);ob.location=center+Vector(loc)*size
    ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO';data.ortho_scale=size*1.22
scene.view_settings.view_transform='Standard'
Path(outdir).mkdir(parents=True,exist_ok=True)
for name,loc in [('front',(0,-3,0.1)),('side',(3,0,0.1)),('beauty',(2,-3,1.1))]:
    cam.location=center+Vector(loc)*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(Path(outdir)/(name+'.png'));bpy.ops.render.render(write_still=True)
if len(args)>2 and args[2]=='walk':
    for frame in (6,16,26,36):
        scene.frame_set(frame)
        cam.location=center+Vector((2,-3,1))*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(Path(outdir)/('walk_%02d.png'%frame));bpy.ops.render.render(write_still=True)
