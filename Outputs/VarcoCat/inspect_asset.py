import bpy, sys, json
from mathutils import Vector
args = sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
result=[]
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH': continue
    vs=[ob.matrix_world @ v.co for v in ob.data.vertices]
    bounds=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
    zlo,zhi=bounds[2]
    high=[v for v in vs if v.z>zlo+(zhi-zlo)*0.72]
    head=sum(high,Vector())/len(high)
    result.append({'name':ob.name,'bounds':bounds,'high_centroid':list(head),'verts':len(vs),'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),'materials':len(ob.data.materials)})
print('ASSET_INFO '+json.dumps(result))
