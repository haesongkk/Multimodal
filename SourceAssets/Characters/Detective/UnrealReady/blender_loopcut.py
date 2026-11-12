# Blender: find the most seamless loop inside each VARCO clip and export only that range for Unreal.
# Usage: blender -b --python blender_loopcut.py -- <in_dir> <out_dir> <name> [<name> ...]
import os, sys, math, bpy

args = sys.argv[sys.argv.index("--") + 1:]
in_dir, out_dir, names = args[0], args[1], args[2:]
os.makedirs(out_dir, exist_ok=True)
MIN_FRACTION = float(os.environ.get("LOOP_MIN_FRACTION", "0.45"))  # a loop must keep at least this share of the clip


def pose_vec(arm, f):
    bpy.context.scene.frame_set(f)
    v = []
    for b in arm.pose.bones:
        m = b.matrix
        # Rotation part only for every bone; translation only matters for the hips bob.
        v.extend(m[r][c] for r in range(3) for c in range(3))
        if b.name == "Hips":
            v.extend((m[0][3] * 0.01, m[1][3] * 0.01, m[2][3] * 0.01))
    return v


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


for name in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=os.path.join(in_dir, name + ".fbx"))
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    # Some VARCO clips face sideways compared with idle/walk; LOOP_ROTATE_Z (degrees) turns the whole
    # rig around the vertical axis and bakes it into the rest so the root track carries the turn.
    turn = float(os.environ.get("LOOP_ROTATE_Z", "0"))
    if turn:
        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        arm.rotation_euler[2] += math.radians(turn)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    act = arm.animation_data.action
    s, e = int(act.frame_range[0]), int(round(act.frame_range[1]))
    poses = {f: pose_vec(arm, f) for f in range(s, e + 1)}
    length = e - s
    best = (1e9, s, e)
    for i in range(s, s + length // 2 + 1):
        for j in range(i + max(8, int(length * MIN_FRACTION)), e + 1):
            d = dist(poses[i], poses[j])
            if d < best[0]:
                best = (d, i, j)
    d, i, j = best
    # Frame j matches frame i, so the loop plays i .. j-1 and wraps back to i.
    act.name = name
    bpy.context.scene.frame_start = i
    bpy.context.scene.frame_end = j - 1
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(out_dir, name + ".fbx"), use_selection=False, object_types={"ARMATURE", "MESH"},
        apply_unit_scale=False, global_scale=100.0, apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE",
        add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True, path_mode="COPY", embed_textures=True)
    step = sum(dist(poses[f], poses[f + 1]) for f in range(s, e)) / max(1, e - s)
    print("LOOPCUT %s clip=%d-%d loop=%d-%d seam=%.4f full_seam=%.4f avg_step=%.4f" % (name, s, e, i, j - 1, d, dist(poses[s], poses[e]), step))
