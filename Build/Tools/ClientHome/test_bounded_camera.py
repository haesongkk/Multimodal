"""Verify bounded perspective follow without changing the established composition."""
import unreal as u,math,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
p=u.GameplayStatics.get_player_pawn(w,0);camera=p.get_component_by_class(u.CameraComponent)
points=[(-730,-238),(870,350),(740,-400),(400,-460),(-760,570),(0,500),(0,0)]
index=0;elapsed=0;records=[]
p.set_actor_location(u.Vector(*points[0],114),False,False)
def tick(dt):
 global index,elapsed
 try:
  elapsed+=dt
  if elapsed<1.5:return
  c=camera.get_world_location();r=camera.get_world_rotation()
  assert camera.get_editor_property('projection_mode')==u.CameraProjectionMode.PERSPECTIVE
  assert abs(r.pitch+35)<0.01 and abs(camera.get_editor_property('field_of_view')-60)<0.01
  assert -350.01<=c.x<=430.01 and -1075.01<=c.y<=-919.99,c
  records.append({'player':points[index],'camera':[c.x,c.y,c.z],'pitch':r.pitch})
  index+=1;elapsed=0
  if index==len(points):
   u.unregister_slate_post_tick_callback(handle)
   p.set_actor_location(u.Vector(-730,-238,114),False,False)
   Path('D:/Multimodal/Outputs/ClientHome/bounded-camera-test.json').write_text(json.dumps({'passed':True,'cases':records},indent=2))
   u.log('BOUNDED_CAMERA_ALL_7_PASS');return
  p.set_actor_location(u.Vector(*points[index],114),False,False)
 except Exception as ex:
  u.unregister_slate_post_tick_callback(handle);u.log_error('BOUNDED_CAMERA_FAILED '+str(ex))
handle=u.register_slate_post_tick_callback(tick)
