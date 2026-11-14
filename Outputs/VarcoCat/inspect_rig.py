import bpy, sys, json
src=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=src)
for o in bpy.context.scene.objects:
    print('OBJECT',o.name,o.type,'matrix',list(map(list,o.matrix_world)))
    if o.type=='ARMATURE': print('BONES',[(b.name,list(b.head_local),list(b.tail_local)) for b in o.data.bones])
    if o.type=='MESH':
        print('GROUPS',[g.name for g in o.vertex_groups]);print('MODS',[(m.name,m.type) for m in o.modifiers]);print('MATERIALS',[(m.name,[(n.type,n.image.size[:] if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes]) for m in o.data.materials])
print('ACTIONS',[(a.name,list(a.frame_range)) for a in bpy.data.actions]);print('FRAMES',bpy.context.scene.frame_start,bpy.context.scene.frame_end)
