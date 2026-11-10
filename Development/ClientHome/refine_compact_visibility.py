import unreal as u,json
from pathlib import Path
b=Path('D:/Multimodal/Saved/ClientHome')
base=json.loads((b/'precompact-actors.json').read_text())
entry={r['label'] for r in base if 180<r['location'][0]<300 and -800<r['location'][1]<-650 and r['mesh']}
(b/'compact-extra-hidden.json').write_text(json.dumps(sorted(entry)))
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
for a in actors.get_all_level_actors():
 if a.get_actor_label() in entry or a.get_actor_label() in ['Plane','SM_Carpet_02','Assets_Proxy_kitchen_Shelf_A_Proxy2']:
  a.set_actor_hidden_in_game(True)
  a.set_is_temporarily_hidden_in_editor(True)
  if a.get_actor_label() in entry or a.get_actor_label() in ['Plane','SM_Carpet_02']:a.set_actor_enable_collision(False)
  c=a.get_component_by_class(u.StaticMeshComponent)
  if c:c.set_editor_property('cast_hidden_shadow',a.get_actor_label()!='SM_Carpet_02')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('COMPACT_VISIBILITY_SAVED')
