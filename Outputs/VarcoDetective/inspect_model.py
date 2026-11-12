import bpy, bmesh, json
from pathlib import Path
root=Path(__file__).parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(root/'Detective_Source.glb'))
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    bm=bmesh.new(); bm.from_mesh(o.data)
    print(json.dumps({'name':o.name,'verts':len(bm.verts),'faces':len(bm.faces),'tris':sum(len(f.verts)==3 for f in bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'boundary':sum(e.is_boundary for e in bm.edges),'wire':sum(e.is_wire for e in bm.edges),'size':list(o.dimensions),'uv':len(o.data.uv_layers),'materials':[m.name for m in o.data.materials]},ensure_ascii=False))
    for m in o.data.materials:
        if m and m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image: print('IMAGE',n.image.name, list(n.image.size))
    bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Detective_Imported.blend'))
