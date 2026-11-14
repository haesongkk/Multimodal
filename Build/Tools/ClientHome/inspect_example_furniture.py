import unreal as u,json
from pathlib import Path
levels=u.get_editor_subsystem(u.LevelEditorSubsystem);editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world();assert editor.get_editor_world().get_path_name().startswith('/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal.')
assert levels.save_current_level()
try:
 assert levels.load_level('/Game/ExternalAssets/StylizedKitchen/Levels/Stylized_Interior')
 rows=[]
 def v(p):return [p.x,p.y,p.z]
 for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
  c=a.get_component_by_class(u.StaticMeshComponent)
  if not c or not c.static_mesh:continue
  r=a.get_actor_rotation();o,e=a.get_actor_bounds(False)
  rows.append(dict(label=a.get_actor_label(),pos=v(a.get_actor_location()),rot=[r.pitch,r.yaw,r.roll],scale=v(a.get_actor_scale3d()),center=v(o),extent=v(e),mesh=c.static_mesh.get_path_name(),materials=[m.get_path_name() if m else None for m in c.get_materials()]))
 Path('D:/Multimodal/SourceAssets/Data/ClientHome/example-furnishings.json').write_text(json.dumps(rows,indent=2))
finally:
 assert levels.load_level('/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal')
u.log('EXAMPLE_FURNITURE_INSPECTED')
