import bpy,bmesh,json
from pathlib import Path
root=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(root/'Detective_Imported.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
vs=list(bm.verts);rem=set(vs);comps=[]
while rem:
    todo=[rem.pop()];comp=[]
    while todo:
        v=todo.pop();comp.append(v)
        for e in v.link_edges:
            n=e.other_vert(v)
            if n in rem: rem.remove(n);todo.append(n)
    comps.append(comp)
print('COMPONENTS',[(len(c),[tuple(round(f(v.co[i] for v in c),4) for i in range(3)) for f in (min,max)]) for c in comps])
print('TRANSFORM',list(o.location),list(o.rotation_euler),list(o.scale))
print('RANGE',[(round(z,3),[(round(min(v.co[i] for v in vs if abs(v.co.z-z)<.026),4),round(max(v.co[i] for v in vs if abs(v.co.z-z)<.026),4)) for i in (0,1)]) for z in [x/100 for x in range(-45,51,5)] if any(abs(v.co.z-z)<.026 for v in vs)])
data={'vertices':[list(v.co) for v in bm.verts], 'faces':[[v.index for v in f.verts] for f in bm.faces]}
(root/'surface_geometry.json').write_text(json.dumps(data))
