import bpy, bmesh, sys, json
from pathlib import Path
from mathutils import Vector, kdtree

src, dst = sys.argv[sys.argv.index('--')+1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in bpy.context.scene.objects: o.select_set(False)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.object.join()
ob=bpy.context.object
ob.name='Cat_Game_Symmetric'
ob.parent=None
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bm=bmesh.new(); bm.from_mesh(ob.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bm.to_mesh(ob.data); bm.free()
raw_tris=sum(len(p.vertices)-2 for p in ob.data.polygons)
if raw_tris>5400:
    mod=ob.modifiers.new('Game_budget','DECIMATE')
    mod.ratio=5400/raw_tris
    bpy.ops.object.modifier_apply(modifier=mod.name)
xs=[v.co.x for v in ob.data.vertices]
center=(min(xs)+max(xs))/2
for v in ob.data.vertices: v.co.x-=center
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.symmetrize(direction='NEGATIVE_X',threshold=0.0001)
bpy.ops.object.mode_set(mode='OBJECT')
bm=bmesh.new(); bm.from_mesh(ob.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(ob.data); bm.free()
zmin=min(v.co.z for v in ob.data.vertices)
for v in ob.data.vertices: v.co.z-=zmin
for p in ob.data.polygons: p.use_smooth=False
ob.data.update()
kd=kdtree.KDTree(len(ob.data.vertices))
for i,v in enumerate(ob.data.vertices): kd.insert(v.co,i)
kd.balance()
errors=[kd.find(Vector((-v.co.x,v.co.y,v.co.z)))[2] for v in ob.data.vertices]
bm=bmesh.new();bm.from_mesh(ob.data)
report={'source_triangles':raw_tris,'triangles':len(ob.data.polygons),'vertices':len(ob.data.vertices),'symmetry_max_error':max(errors),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'materials':len(ob.data.materials),'symmetry_plane':'Blender X=0','forward':'Blender -Y','up':'Blender +Z'}
bm.free()
Path(dst).parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst,export_format='GLB',use_selection=True,export_animations=False)
bpy.ops.wm.save_as_mainfile(filepath=str(Path(dst).with_suffix('.blend')))
Path(dst).with_suffix('.validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('SYMMETRY_REPORT '+json.dumps(report))
