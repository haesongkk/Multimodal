"""Final adjustments applied only to LV_ClientHome_Linear in Unreal Editor."""
import unreal as u
import json
from pathlib import Path
root=Path('D:/Multimodal/Outputs/ClientHomeLinear')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Linear.')
visibility={r['name']:r for r in json.loads((root/'visibility_before.json').read_text())}
for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    previous=visibility.get(actor.get_name())
    if previous and previous['hidden'] and actor.get_component_by_class(u.StaticMeshComponent):
        actor.set_actor_enable_collision(False)
    if 'Home_Exit' in [str(t) for t in actor.tags]:
        actor.set_actor_location(u.Vector(-1790,140,110),False,True)
    if actor.get_actor_label()=='SpotLight2':
        actor.set_actor_hidden_in_game(True)
    if actor.get_editor_property('hidden'):
        actor.set_is_temporarily_hidden_in_editor(True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
