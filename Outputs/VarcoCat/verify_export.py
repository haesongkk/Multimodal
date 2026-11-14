import bpy,bmesh,sys,json,math,struct
from pathlib import Path
from mathutils import Vector,kdtree
src=Path(sys.argv[sys.argv.index('--')+1])
b=src.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];arm=next((o for o in bpy.context.scene.objects if o.type=='ARMATURE'),None)
r={'file':src.name,'bytes':len(b),'mesh_objects':len(meshes),'materials':len(g.get('materials',[])),'textures':len(g.get('textures',[])),'skins':len(g.get('skins',[])),'animations':len(g.get('animations',[])),'bones':len(arm.data.bones) if arm else 0}
r['gltf_meshes']=len(g.get('meshes',[]));r['gltf_primitives']=sum(len(m['primitives']) for m in g.get('meshes',[]))
o=max(meshes,key=lambda o:len(o.data.vertices));kd=kdtree.KDTree(len(o.data.vertices))
for i,v in enumerate(o.data.vertices):kd.insert(v.co,i)
kd.balance();r['symmetry_max_error']=max(kd.find(Vector((-v.co.x,v.co.y,v.co.z)))[2] for v in o.data.vertices)
r['triangles']=sum(len(p.vertices)-2 for p in o.data.polygons)
if arm:
    r['max_influences']=max(len(v.groups) for v in o.data.vertices)
    r['max_weight_sum_error']=max(abs(sum(gr.weight for gr in v.groups)-1) for v in o.data.vertices)
    samples=[]
    for f in (1,6,16,26,36,44):
        bpy.context.scene.frame_set(f);ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());vs=[ev.matrix_world@v.co for v in ev.data.vertices]
        samples.append({'frame':f,'finite':all(math.isfinite(c) for v in vs for c in v),'bounds':[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]})
    r['pose_samples']=samples
src.with_suffix('.export_check.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print('EXPORT_CHECK '+json.dumps(r))
