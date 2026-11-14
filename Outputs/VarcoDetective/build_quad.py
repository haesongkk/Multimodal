import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(root/'Detective_Imported.blend'))
source=next(o for o in bpy.context.scene.objects if o.type=='MESH')
source.name='Detective_Source_ARCHIVE'
archive=bpy.data.collections.new('00_Source_Archive'); bpy.context.scene.collection.children.link(archive)
for c in list(source.users_collection): c.objects.unlink(source)
archive.objects.link(source)
def copy_obj(name):
    o=source.copy(); o.data=source.data.copy(); o.name=name; bpy.context.scene.collection.objects.link(o); return o
low=copy_obj('Detective_QuadDominant_LowPoly')
bm=bmesh.new(); bm.from_mesh(low.data)
before=len(bm.verts)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0000001)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bmesh.ops.join_triangles(bm,faces=list(bm.faces),angle_face_threshold=math.radians(5),angle_shape_threshold=math.radians(70),cmp_seam=True,cmp_sharp=True,cmp_uvs=True,cmp_vcols=True,cmp_materials=True)
bm.to_mesh(low.data); bm.free(); low.data.update()
main=low.copy(); main.data=low.data.copy(); main.name='Detective_Quad_Edit'; bpy.context.scene.collection.objects.link(main)
bpy.context.view_layer.objects.active=main
mod=main.modifiers.new('Conforming_AllQuad_Surface','SUBSURF'); mod.subdivision_type='SIMPLE'; mod.levels=1; mod.render_levels=1
bpy.ops.object.modifier_apply(modifier=mod.name)
for o in (source,low,main):
    for p in o.data.polygons: p.use_smooth=False
def stats(o):
    bm=bmesh.new(); bm.from_mesh(o.data)
    s={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'triangles':sum(len(f.verts)==3 for f in bm.faces),'ngons':sum(len(f.verts)>4 for f in bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_edges for v in bm.verts),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'uv_layers':len(o.data.uv_layers)}
    bm.free();return s
report={o.name:stats(o) for o in (source,low,main)}
print(json.dumps(report,indent=2)); (root/'topology_report.json').write_text(json.dumps(report,indent=2))
source.hide_render=True; low.hide_render=True; source.hide_set(True); low.hide_set(True)
main['workflow']='Weld coincident vertices 1e-6 m; remove degenerates; recalculate normals; join triangles within 5 degrees respecting UV/material seams; conforming SIMPLE subdivision to all quads. No smoothing or voxel remesh.'
main['source_url']='https://3d.varco.ai/studio/2cd4f90a-dfa0-442d-bb6b-fa506ebfcda7'
main['note']='All-quad editing mesh; more triangles when exported than source. LowPoly variant retains lower runtime cost. Original UV and textures retained.'
doc=bpy.data.texts.new('README_Workflow')
doc.write(main['workflow']+'\n'+main['note']+'\n'+json.dumps(report,indent=2))
bpy.ops.object.select_all(action='DESELECT'); main.select_set(True)
bpy.ops.file.pack_all()
# Set a useful material viewport and frame imported character.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.region_3d.view_distance=1.7
            area.spaces.active.region_3d.view_location=Vector((0,0,0))
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Detective_Quad_Optimized.blend'))
bpy.ops.export_scene.gltf(filepath=str(root/'Detective_Quad_Optimized.glb'),use_selection=True)
main.hide_set(True); main.hide_render=True; low.hide_set(False); low.hide_render=False
bpy.ops.object.select_all(action='DESELECT'); low.select_set(True); bpy.context.view_layer.objects.active=low
bpy.ops.export_scene.gltf(filepath=str(root/'Detective_QuadDominant_LowPoly.glb'),use_selection=True)
# Render inspection views with original texture shown unlit to compare geometry and UVs.
main.hide_set(False); main.hide_render=False; low.hide_render=True; low.hide_set(True)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=16
scene.render.resolution_x=700; scene.render.resolution_y=800; scene.render.resolution_percentage=100
if scene.world is None: scene.world=bpy.data.worlds.new('InspectionWorld')
scene.world.color=(0.16,0.16,0.16)
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='Standard'
for mat in main.data.materials:
    if not mat or not mat.use_nodes: continue
    nt=mat.node_tree
    bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
    out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
    em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value=1
    color=bs.inputs['Base Color']
    if color.is_linked: nt.links.new(color.links[0].from_socket,em.inputs['Color'])
    else: em.inputs['Color'].default_value=color.default_value
    nt.links.new(em.outputs[0],out.inputs['Surface'])
points=[main.matrix_world@Vector(v) for v in main.bound_box]
center=sum(points,Vector())/8; print('CENTER',list(center))
camdata=bpy.data.cameras.new('InspectionCamera');cam=bpy.data.objects.new('InspectionCamera',camdata);scene.collection.objects.link(cam);scene.camera=cam
camdata.type='ORTHO';camdata.ortho_scale=1.22
for label,direction in [('front',(0,-3,0.0)),('quarter',(2,-3,1.0)),('back',(0,3,0.0))]:
    cam.location=center+Vector(direction); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(root/('preview_'+label+'.png'));bpy.ops.render.render(write_still=True)
# Wire overlay on neutral material, for visible quad topology.
neutral=bpy.data.materials.new('Inspection_Grey');neutral.diffuse_color=(0.55,0.65,0.75,1);neutral.use_nodes=True
bs=next(n for n in neutral.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(0.4,0.6,0.7,1)
main.data.materials.clear();main.data.materials.append(neutral)
wire=main.copy();wire.data=main.data.copy();scene.collection.objects.link(wire)
black=bpy.data.materials.new('WireBlack');black.diffuse_color=(0.005,0.005,0.005,1)
wire.data.materials.clear();wire.data.materials.append(black)
wm=wire.modifiers.new('QuadEdges','WIREFRAME');wm.thickness=0.00065;wm.use_replace=True
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
cam.location=center+Vector((1.6,-3,0.8));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(root/'preview_quad_wire.png');bpy.ops.render.render(write_still=True)
