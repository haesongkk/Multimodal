import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Imported.blend'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH');m=o.data
t=BVHTree.FromPolygons([v.co for v in m.vertices],[list(p.vertices) for p in m.polygons],all_triangles=True)
for z in [.1,.05,0,-.05,-.1,-.15,-.25,-.28,-.30,-.32,-.35,-.37,-.395,-.42]:
    print(z,[(x,tuple(round(v,4) for v in q[0]) if q[0] else None) for x in [0,.04,.075,.11,.15,.18] for q in [t.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))]] )
