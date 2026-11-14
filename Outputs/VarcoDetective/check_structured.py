import bpy,bmesh
from pathlib import Path
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Structured_Working.blend'))
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('00_'):continue
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
    print(o.name)
    for e in bm.edges:
        if e.calc_length()<1e-7:print('ZEROEDGE',[(v.index,[round(n,5) for n in v.co]) for v in e.verts])
    for f in bm.faces:
        if f.calc_area()<1e-12:print('ZEROFACE',[(v.index,list(v.co)) for v in f.verts])
    bm.free()
