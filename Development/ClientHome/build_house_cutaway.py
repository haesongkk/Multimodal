"""Render-only cutaway copies; original walls keep their collision and shadows."""
import unreal as u,json
from pathlib import Path
s=u.get_editor_subsystem(u.EditorAssetSubsystem);levels=u.get_editor_subsystem(u.LevelEditorSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
MAP='/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal'
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
assert levels.save_current_level()
def snapshot():
 result={}
 for a in actors.get_all_level_actors():
  c=a.get_component_by_class(u.StaticMeshComponent)
  if c:result[a.get_actor_label()]=[m.get_path_name() if m else None for m in c.get_materials()]
 return result
assert levels.load_level('/Game/StylizedKitchen/Levels/Stylized_Interior');original=snapshot();assert levels.load_level(MAP)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
labels=['House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM','Bathroom_Walls_Trim_SM']
report=[]
for name in labels:
 a=by[name];c=a.get_component_by_class(u.StaticMeshComponent)
 for i,path in enumerate(original[name]):
  if path:c.set_material(i,u.load_asset(path))
 a.set_actor_hidden_in_game(True);c.set_editor_property('cast_hidden_shadow',True)
 dst='/Game/ClientHome_Haeso/Meshes/SM_CH_Cutaway_'+name
 mesh=u.load_asset(dst)
 if not mesh:
  mesh=s.duplicate_asset(c.static_mesh.get_path_name(),dst)
  desc=mesh.get_static_mesh_description(0);removed=[]
  for i in range(desc.get_polygon_count()):
   pid=u.PolygonID();pid.set_editor_property('id_value',i)
   if not desc.is_polygon_valid(pid):continue
   pts=[u.MathLibrary.transform_location(a.get_actor_transform(),desc.get_vertex_position(v)) for v in desc.get_polygon_vertices(pid)]
   if len(pts)<3:continue
   center=sum(v.x for v in pts)/len(pts)
   ab=pts[1]-pts[0];ac=pts[2]-pts[0];normal=ab.cross(ac)
   length=normal.length()
   # West-facing front walls block a camera that looks east. Keep side/back walls.
   front=length>0 and abs(normal.x)/length>.8
   if center < -500 and (front or 'Walls' not in name):removed.append(pid)
  for pid in removed:desc.delete_polygon(pid)
  mesh.build_from_static_mesh_descriptions([desc],False,False)
  assert s.save_loaded_asset(mesh)
  report.append([name,len(removed)])
 visual=by.get('CH_Minimal_Cutaway_'+name)
 if not visual:
  visual=actors.spawn_actor_from_class(u.StaticMeshActor,a.get_actor_location());visual.set_actor_label('CH_Minimal_Cutaway_'+name)
 visual.set_actor_transform(a.get_actor_transform(),False,False)
 vc=visual.get_component_by_class(u.StaticMeshComponent);vc.set_static_mesh(mesh)
 for i,path in enumerate(original[name]):
  if path:vc.set_material(i,u.load_asset(path))
 visual.set_actor_enable_collision(False);visual.set_folder_path('ClientHome/CameraCutaway')
# Lighting blockers and foreground kitchen dressing must not cover the player.
for name,a in by.items():
 c=a.get_component_by_class(u.StaticMeshComponent)
 if not c:continue
 if name in ['Kitchen_Window','Kitchen_Curtain_Low','Kitchen_Curtain_Low2','Curtain_Rod']:
  for i,path in enumerate(original[name]):
   if path:c.set_material(i,u.load_asset(path))
  a.set_actor_hidden_in_game(True);c.set_editor_property('cast_hidden_shadow',True)
 if name.startswith('Cube') and name!='Cube17':a.set_actor_hidden_in_game(True);c.set_editor_property('cast_hidden_shadow',True)
assert levels.save_current_level()
Path('D:/Multimodal/Saved/ClientHome/cutaway-mesh-report.json').write_text(json.dumps(report),encoding='utf-8')
u.log('WHOLE_HOUSE_CUTAWAY_SAVED')
