"""PIE camera bounds, tracking, fixed rotation and clue-route framing checks."""
import unreal as u,json,math
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert w and 'Lvl_ClientHome_Minimal' in w.get_name()
p=u.GameplayStatics.get_player_pawn(w,0)
c=p.get_component_by_class(u.CameraComponent)
h=u.GameplayStatics.get_player_controller(w,0).get_hud()
if h.get_editor_property('Popup'):h.call_method('Confirm')
points=[('start',378,350),('pot',740,380),('fur',50,-145),('window',870,350),('door',-760,-238),('kitchen',-450,350),('snack',-230,-100),('study',100,500),('left floor',-650,-350),('library rug footprints',150,230)]
index=0;elapsed=0.;moving=False;records=[];samples=[]
def finish(error=None):
 u.unregister_slate_post_tick_callback(handle)
 Path('D:/Multimodal/Saved/ClientHome/side-camera-test.json').write_text(json.dumps({'passed':error is None,'error':error,'positions':records,'samples':len(samples),'scope':'fixed rotation, camera bounds every tick, settled follow at investigation points'},indent=2),encoding='utf-8')
 u.log('SIDE_CAMERA_RESULT: '+str(error or 'PASS'))
def tick(dt):
 global index,elapsed,moving
 try:
  name,x,y=points[index]
  if not moving:p.set_actor_location(u.Vector(x,y,114),False,False);moving=True;elapsed=0.
  elapsed+=dt;loc=c.get_world_location();rot=c.get_world_rotation()
  assert -650.1<=loc.x<=750.1 and -1350.1<=loc.y<=-569.9 and 719.9<=loc.z<=720.1,('bounds',str(loc))
  assert abs(rot.pitch+35)<.1 and abs(rot.yaw-90)<.1 and abs(rot.roll)<.1,('rotation',str(rot))
  samples.append((loc.x,loc.y))
  if elapsed<2.5:return
  pos=p.get_actor_location()
  target=(max(-650,min(750,pos.x)),max(-350,min(430,pos.y))-1000,720)
  assert abs(loc.z-target[2])<3,(name,'height',str(loc),target)
  dx=pos.x-loc.x;dy=pos.y-loc.y;dz=pos.z-loc.z
  forward=dy;side=-dx
  angle=math.radians(35);depth=forward*math.cos(angle)-dz*math.sin(angle)
  right=side/(depth*math.tan(math.radians(30)));up=(forward*math.sin(angle)+dz*math.cos(angle))/(depth*math.tan(math.radians(30))*9/16)
  assert depth>0 and abs(right)<.95 and abs(up)<.95,(name,'player outside frame',right,up)
  assert math.hypot(loc.x-target[0],loc.y-target[1])<3,(name,'tracking',str(loc),target)
  records.append({'name':name,'camera':[loc.x,loc.y,loc.z],'target':target})
  index+=1;moving=False
  if index==len(points):finish()
 except Exception as e:finish(str(e))
handle=u.register_slate_post_tick_callback(tick)
