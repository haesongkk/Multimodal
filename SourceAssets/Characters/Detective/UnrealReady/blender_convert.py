# Blender: re-export VARCO FBX files with Unreal-friendly settings.
# Usage: blender -b --python blender_convert.py -- <in_dir> <out_dir> <name> [<name> ...]
import os, sys, bpy

args = sys.argv[sys.argv.index("--") + 1:]
in_dir, out_dir, names = args[0], args[1], args[2:]
os.makedirs(out_dir, exist_ok=True)

for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(in_dir, name + ".fbx"))
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    mesh = next(o for o in bpy.data.objects if o.type == "MESH")
    dims = mesh.dimensions
    action = arm.animation_data.action if arm.animation_data else None
    if action:
        action.name = name
        bpy.context.scene.frame_start = int(action.frame_range[0])
        bpy.context.scene.frame_end = int(action.frame_range[1])
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(out_dir, name + ".fbx"),
        use_selection=False,
        object_types={"ARMATURE", "MESH"},
        apply_unit_scale=False,
        global_scale=100.0,
        apply_scale_options="FBX_SCALE_ALL",
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True,
        path_mode="COPY",
        embed_textures=True,
    )
    print("CONVERTED", name, "dims=%.3f,%.3f,%.3f" % tuple(dims), "frames=", action.frame_range[:] if action else None)
