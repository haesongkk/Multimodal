"""Sample actual animation pose and camera while the movement test drives Manny."""
import unreal as u,json,math
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();p=u.GameplayStatics.get_player_pawn(w,0)
m=p.get_component_by_class(u.SkeletalMeshComponent);a=m.get_anim_instance();c=p.get_component_by_class(u.CameraComponent);cap=p.get_component_by_class(u.CapsuleComponent)
assert m.get_editor_property('skeletal_mesh_asset').get_name()=='SKM_Manny_Simple'
assert a and a.get_class().get_name()=='ABP_Unarmed_C'
assert cap.get_unscaled_capsule_radius()==34 and cap.get_unscaled_capsule_half_height()==88
assert all(not body.is_visible() for body in p.get_components_by_class(u.StaticMeshComponent))
samples=[];elapsed=0

def tick(dt):
 global elapsed
 elapsed+=dt
 v=p.get_velocity();speed=math.hypot(v.x,v.y)
 if speed>30:
  pos=m.get_socket_transform('foot_l',u.RelativeTransformSpace.RTS_COMPONENT).translation
  forward=p.get_actor_forward_vector();r=c.get_world_rotation()
  samples.append({'speed':speed,'foot':[pos.x,pos.y,pos.z],'facing':(forward.x*v.x+forward.y*v.y)/speed,'camera_yaw':r.yaw,'camera_pitch':r.pitch})
 if elapsed<8:return
 u.unregister_slate_post_tick_callback(handle)
 checks={'moving_samples':len(samples)>8,'walking_pose_changes':bool(samples) and max(max(s['foot'][axis] for s in samples)-min(s['foot'][axis] for s in samples) for axis in range(3))>2,'faces_travel':bool(samples) and sum(s['facing']>.8 for s in samples)>len(samples)*.65,'camera_angle_fixed':all(abs(s['camera_yaw'])<.1 and abs(s['camera_pitch']+30)<.1 for s in samples)}
 Path('D:/Multimodal/Outputs/ClientHome/manny-animation-test.json').write_text(json.dumps({'passed':all(checks.values()),'checks':checks,'samples':samples},indent=2))
 u.log('MANNY_ANIMATION_RESULT: '+str(checks))
handle=u.register_slate_post_tick_callback(tick)
