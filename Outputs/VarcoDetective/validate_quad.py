import bpy,bmesh,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector,Quaternion
root=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(root/'Detective_Quad_Optimized.blend'))
src=bpy.data.objects['Detective_Source_ARCHIVE'];main=bpy.data.objects['Detective_Quad_Edit'];low=bpy.data.objects['Detective_QuadDominant_LowPoly']
low.name='Detective_LowPoly_Clean'
bvh=BVHTree.FromPolygons([v.co for v in src.data.vertices],[list(p.vertices) for p in src.data.polygons],all_triangles=True)
dist=[bvh.find_nearest(v.co)[3] for v in main.data.vertices]
report=json.loads((root/'topology_report.json').read_text())
report['validation']={'max_vertex_distance_from_source_m':max(dist),'mean_vertex_distance_from_source_m':sum(dist)/len(dist),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'all_quad':all(len(p.vertices)==4 for p in main.data.polygons)}
assert report['validation']['all_quad']
assert len(main.data.uv_layers)==1
bm=bmesh.new();bm.from_mesh(main.data);assert all(e.is_manifold for e in bm.edges);bm.free()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            r=area.spaces.active.region_3d
            r.view_rotation=Quaternion((1,0,0),1.5707963267948966)
            r.view_location=Vector((0,0,0));r.view_distance=1.6
main['quad_count']=len(main.data.polygons)
main['max_vertex_surface_deviation_m']=max(dist)
main['workflow_script']='build_quad.py (stored beside blend); source retained in archive collection'
text=bpy.data.texts.get('README_Workflow');text.write('\nValidation:\n'+json.dumps(report['validation'],indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Detective_Quad_Optimized.blend'))
(root/'topology_report.json').write_text(json.dumps(report,indent=2))
(root/'README.md').write_text('''# Papercraft Detective — Blender cleanup

Detective_Quad_Optimized.blend is the editable master. Textures are packed.

- Detective_Quad_Edit: 3,180 quad faces; no triangles/ngons; closed manifold.
- Detective_LowPoly_Clean (hidden): welded and cleaned low-poly mesh, 596 geometric vertices, 996 mixed faces; retains 1,188 triangulated faces before export.
- Detective_Source_ARCHIVE (hidden): untouched imported source geometry and UV reference.

The all-quad version is for editing. Its GPU triangle count increases to 6,360. This is not a runtime polygon reduction. GLB always triangulates faces; use the .blend for actual editable quads.

Cleanup welds coincident positions, removes degenerates, recalculates normals, joins near-coplanar triangles while respecting UV/material seams, then uses SIMPLE subdivision to create a conforming all-quad mesh. No smoothing, voxel remesh or new generation. Original 2K textures and UVs are retained. This is topology cleanup, not animation-specific hand retopology.

Scripts: inspect_model.py, build_quad.py, validate_quad.py. Source: Detective_Source.glb. Validation: topology_report.json. Preview PNGs show front, back, quarter and quad wires.
''',encoding='utf-8')
print(json.dumps(report['validation'],indent=2))
