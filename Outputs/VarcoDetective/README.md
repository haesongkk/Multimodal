# Papercraft Detective — Blender cleanup

Detective_Quad_Optimized.blend is the editable master. Textures are packed.

- Detective_Quad_Edit: 3,180 quad faces; no triangles/ngons; closed manifold.
- Detective_LowPoly_Clean (hidden): welded and cleaned low-poly mesh, 596 geometric vertices, 996 mixed faces; retains 1,188 triangulated faces before export.
- Detective_Source_ARCHIVE (hidden): untouched imported source geometry and UV reference.

The all-quad version is for editing. Its GPU triangle count increases to 6,360. This is not a runtime polygon reduction. GLB always triangulates faces; use the .blend for actual editable quads.

Cleanup welds coincident positions, removes degenerates, recalculates normals, joins near-coplanar triangles while respecting UV/material seams, then uses SIMPLE subdivision to create a conforming all-quad mesh. No smoothing, voxel remesh or new generation. Original 2K textures and UVs are retained. This is topology cleanup, not animation-specific hand retopology.

Scripts: inspect_model.py, build_quad.py, validate_quad.py. Source: Detective_Source.glb. Validation: topology_report.json. Preview PNGs show front, back, quarter and quad wires.
