import bpy, bmesh, sys, json, math
from pathlib import Path
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

src,outdir=sys.argv[sys.argv.index('--')+1:][:2]
out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=src)
scene=bpy.context.scene
arm=next(o for o in scene.objects if o.type=='ARMATURE')
ob=max((o for o in scene.objects if o.type=='MESH' and len(o.vertex_groups)),key=lambda o:len(o.data.vertices))
ob.name='Cat_LOD0';arm.name='Cat_Rig'
assert max(abs(ob.matrix_world[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-4, 'Unexpected mesh transform'
ob.data.calc_loop_triangles()
sv=[v.co.copy() for v in ob.data.vertices];st=[tuple(t.vertices) for t in ob.data.loop_triangles]
names=[g.name for g in ob.vertex_groups]
sw=[{names[g.group]:g.weight for g in v.groups if g.weight>1e-6} for v in ob.data.vertices]
tree=BVHTree.FromPolygons(sv,st,all_triangles=True)
def flip(n):
    return n[:-2]+'.R' if n.endswith('.L') else n[:-2]+'.L' if n.endswith('.R') else n
def weights(p):
    # Keep the small stylized paws rigid instead of collapsing across toe joints.
    if p.z<0.065 and abs(p.x)>0.025:
        side='.L' if p.x>0 else '.R'
        return [('hand'+side if p.y<0 else 'foot'+side,1.0)]
    positive=p.x>1e-6
    q=Vector((-p.x,p.y,p.z)) if positive else p
    loc,no,idx,dist=tree.find_nearest(q)
    a,b,c=(sv[i] for i in st[idx]);v0=b-a;v1=c-a;v2=loc-a
    d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-18: factors=(1,0,0)
    else:
        v=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;w=(d00*v2.dot(v1)-d01*v2.dot(v0))/den;factors=(1-v-w,v,w)
    result={}
    for vid,f in zip(st[idx],factors):
        for name,val in sw[vid].items():
            n=flip(name) if positive else name;result[n]=result.get(n,0)+max(0,f)*val
    if abs(p.x)<1e-6:
        result={n:(result.get(n,0)+result.get(flip(n),0))/2 for n in set(result)|{flip(n) for n in result}}
    result=sorted(((n,w) for n,w in result.items() if w>0.005),key=lambda x:x[1],reverse=True)[:4]
    total=sum(w for n,w in result)
    return [(n,w/total) for n,w in result] if total else [('Root',1)]

# One opaque base-color material; no extra normal/ORM textures or transparency.
mat=ob.data.materials[0]
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
base=bs.inputs['Base Color']
img=next((l.from_node.image for l in base.links if l.from_node.type=='TEX_IMAGE'),None)
if img is None: img=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.colorspace_settings.name=='sRGB')
if tuple(img.size)!=(1024,1024):img.scale(1024,1024)
img.filepath_raw=str(out/'Cat_BaseColor_1K.png');img.file_format='PNG';img.save();img.pack()
clean=bpy.data.materials.new('Cat_BaseColor_1K');clean.use_nodes=True
pbs=next(n for n in clean.node_tree.nodes if n.type=='BSDF_PRINCIPLED');pbs.inputs['Metallic'].default_value=0;pbs.inputs['Roughness'].default_value=0.85
tex=clean.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;clean.node_tree.links.new(tex.outputs['Color'],pbs.inputs['Base Color'])
ob.data.materials.clear();ob.data.materials.append(clean)

def active(o):
    for x in scene.objects:x.select_set(False)
    o.select_set(True);bpy.context.view_layer.objects.active=o
def symmetric(o,target):
    active(o)
    # Weld UV-split import vertices before collapse so UV seams cannot open holes.
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.to_mesh(o.data);bm.free()
    count=sum(len(p.vertices)-2 for p in o.data.polygons)
    if count>target:
        m=o.modifiers.new('Budget','DECIMATE');m.ratio=target/count
        bpy.ops.object.modifier_move_up(modifier=m.name)
        bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.to_mesh(o.data);bm.free()
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.symmetrize(direction='NEGATIVE_X',threshold=0.0001);bpy.ops.object.mode_set(mode='OBJECT')
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for group in o.vertex_groups:group.remove(list(range(len(o.data.vertices))))
    for v in o.data.vertices:
        for name,w in weights(v.co):o.vertex_groups[name].add([v.index],w,'REPLACE')
    for p in o.data.polygons:p.use_smooth=False;p.material_index=0
    o.data.update()
    kd=kdtree.KDTree(len(o.data.vertices))
    for i,v in enumerate(o.data.vertices):kd.insert(v.co,i)
    kd.balance();err=max(kd.find(Vector((-v.co.x,v.co.y,v.co.z)))[2] for v in o.data.vertices)
    bm=bmesh.new();bm.from_mesh(o.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
    return {'triangles':len(o.data.polygons),'vertices':len(o.data.vertices),'symmetry_max_error':err,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'max_bone_influences':max(len(v.groups) for v in o.data.vertices),'unweighted_vertices':sum(not len(v.groups) for v in o.data.vertices)}

arm.data.pose_position='REST'
r0=symmetric(ob,5400)
lod=ob.copy();lod.data=ob.data.copy();scene.collection.objects.link(lod);lod.name='Cat_LOD1';r1=symmetric(lod,1800)
actions=list(bpy.data.actions)
if actions:
    arm.animation_data_create();arm.animation_data.action=actions[0]
    for tr in list(arm.animation_data.nla_tracks):arm.animation_data.nla_tracks.remove(tr)
    scene.frame_start=math.floor(actions[0].frame_range[0]);scene.frame_end=math.ceil(actions[0].frame_range[1])
scene.frame_set(scene.frame_start)
arm.data.pose_position='POSE'
# Keep the lowest paw on the ground throughout the in-place walk.
root=arm.pose.bones.get('Root')
ground_corrections=[]
if root and actions:
    source_root=[]
    for frame in range(scene.frame_start,scene.frame_end+1):
        scene.frame_set(frame)
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        low=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
        matrix=root.matrix.copy();matrix.translation.z-=low
        source_root.append((frame,matrix,low))
    for frame,matrix,low in source_root:
        scene.frame_set(frame);root.matrix=matrix;root.keyframe_insert(data_path='location',frame=frame)
        ground_corrections.append(low)
scene.frame_set(scene.frame_start)
def export_glb(path,mesh,animated):
    active(mesh)
    if animated:arm.select_set(True)
    props={p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}
    kwargs={'filepath':str(path),'export_format':'GLB','use_selection':True,'export_animations':animated,'export_skins':animated,'export_force_sampling':True,'export_frame_range':True,'export_nla_strips':False}
    bpy.ops.export_scene.gltf(**{k:v for k,v in kwargs.items() if k in props})
export_glb(out/'Cat_Game_LOD0_Walk.glb',ob,True)
export_glb(out/'Cat_Game_LOD1_Walk.glb',lod,True)
arm.data.pose_position='REST';export_glb(out/'Cat_Game_LOD0_Standing.glb',ob,False);arm.data.pose_position='POSE'
active(ob);arm.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'Cat_Game_LOD0_Walk.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,path_mode='COPY',embed_textures=True)
lod.hide_render=True;lod.hide_set(True)
for helper in list(scene.objects):
    if helper.type=='MESH' and helper not in (ob,lod):bpy.data.objects.remove(helper,do_unlink=True)
active(ob);arm.data.pose_position='REST'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'Cat_Game_Source.blend'))
report={'LOD0':r0,'LOD1':r1,'materials_per_mesh':1,'basecolor_resolution':[1024,1024],'texture_maps':1,'opaque':True,'bones':len(arm.data.bones),'animations':len(actions),'animation_frame_range':[scene.frame_start,scene.frame_end],'fps':scene.render.fps,'max_root_ground_correction':max(map(abs,ground_corrections),default=0),'symmetry_plane':'Blender X=0; glTF X=0','forward':'Blender -Y; glTF +Z','source':src,'notes':['Geometry mirrored from negative X to positive X before export.','Mirrored skin weights swap .L/.R bone groups; at most 4 normalized influences.','No target-device engine profiling performed.','LODs are separate exports using the same skeleton.']}
(out/'VALIDATION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('FINAL_REPORT '+json.dumps(report))
