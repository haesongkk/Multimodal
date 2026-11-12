import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Structured_Working.blend'))
src=bpy.data.objects['00_SOURCE_BakeReference']
parts=sorted([o for o in bpy.context.scene.objects if o.type=='MESH' and o!=src],key=lambda o:o.name)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.009,area_weight=1.0,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
image=bpy.data.images.new('Detective_Retopo_BaseColor_2K',width=2048,height=2048,alpha=False)
image.generated_color=(.25,.25,.25,1)
mat=bpy.data.materials.new('Detective_Retopo_Baked');mat.use_nodes=True
nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.78
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;nt.nodes.active=tex;nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for o in parts:o.data.materials.clear();o.data.materials.append(mat)
for m in src.data.materials:
    nodes=m.node_tree.nodes;links=m.node_tree.links
    old=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
    em=nodes.new('ShaderNodeEmission');color=old.inputs['Base Color']
    if color.is_linked:links.new(color.links[0].from_socket,em.inputs['Color'])
    else:em.inputs['Color'].default_value=color.default_value
    links.new(em.outputs[0],out.inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=1
scene.render.bake.use_selected_to_active=True;scene.render.bake.cage_extrusion=.012;scene.render.bake.max_ray_distance=.09
scene.render.bake.margin=12;scene.render.bake.use_clear=False
src.hide_set(False);src.hide_render=False
# Texture pixels are populated by transfer_nearest_texture.py after the UV layout is saved.
image.filepath_raw=str(R/'Detective_Retopo_BaseColor_2K.png');image.file_format='PNG';image.save();image.pack()
# Restore archived source shader.
for m in src.data.materials:
    bs0=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
    m.node_tree.links.new(bs0.outputs[0],out.inputs['Surface'])
src.hide_set(True);src.hide_render=True
archive=bpy.data.collections.new('00_Original_Source_ARCHIVE');scene.collection.children.link(archive)
for c in list(src.users_collection):c.objects.unlink(src)
archive.objects.link(src)
retopo=bpy.data.collections.new('01_Structured_Retopology');scene.collection.children.link(retopo)
for o in parts:
    for c in list(o.users_collection):c.objects.unlink(o)
    retopo.objects.link(o)
    o['editable_part']=True;o['texture']='Detective_Retopo_BaseColor_2K, baked from original atlas'
# Include former all-quad version for direct comparison, hidden by default.
with bpy.data.libraries.load(str(R/'Detective_Quad_Optimized.blend'),link=False) as (a,b):b.objects=['Detective_Quad_Edit']
old=b.objects[0]
if old:
    c=bpy.data.collections.new('02_Previous_Subdivision_ARCHIVE');scene.collection.children.link(c);c.objects.link(old);old.name='Previous_Subdivision_3180Quads';old.hide_render=True;old.hide_set(True)
text=bpy.data.texts.new('README_Retopology_v2')
text.write('''Structured quad retopology v2

This replaces the previous triangle-subdivision topology. Original source and former quad version are archived and hidden.
7 editable parts: eye-loop face/head, connected coat/shoulder/sleeve/hip loops, brim/crown rings, 2 bow patches, and 2 thickened lapel fold patches.
2,316 quads total. Each part is closed manifold; parts overlap at natural clothing/hat joins rather than being welded into one surface.
Eye loops are planned over the painted eyes. There are no separate eyeballs or facial rig. Deformation has not been validated.
The original 2K base color is transferred to a new shared UV atlas by transfer_nearest_texture.py. Lapel colors reuse blue coat texture; bow bases reuse the original bow color to avoid underside contamination. Original source textures remain in the archive.
Paper facets and T pose retained. Projection approximates silhouette; this is not an exact surface duplicate.
Reproduction: rebuild_structured.py -> bake_structured.py -> transfer_nearest_texture.py -> validate_retopo_v2.py. Geometry health: structured_report.json.
GLB exports triangles; edit true quads in this .blend.
''')
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_floor=False
            r=area.spaces.active.region_3d;r.view_rotation=Quaternion((1,0,0),math.pi/2);r.view_location=Vector((0,0,0));r.view_distance=1.6
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Detective_Retopology_v2.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'Detective_Retopology_v2.glb'),use_selection=True)
# Inspection renders use emission to show the same albedo without new lighting bias.
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
scene.render.bake.use_selected_to_active=False;scene.cycles.samples=8
scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
if scene.world is None:scene.world=bpy.data.worlds.new('InspectionWorld')
scene.world.color=(.16,.16,.16)
cd=bpy.data.cameras.new('InspectionCamera');cam=bpy.data.objects.new('InspectionCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=1.18
for label,direction in [('front',(0,-3,0)),('quarter',(1.5,-3,.7)),('back',(0,3,0))]:
    cam.location=Vector(direction);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(R/('retopo_v2_'+label+'.png'));bpy.ops.render.render(write_still=True)
