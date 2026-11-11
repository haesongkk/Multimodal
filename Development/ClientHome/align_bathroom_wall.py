"""Align bathroom with the existing exterior wall and remove the front sill."""
import unreal as u,json
from pathlib import Path
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
rows={r['label']:r for r in json.loads(Path('D:/Multimodal/Saved/ClientHome/example-furnishings.json').read_text())}
def move(name,x):
 a=by['CH_SmallBath_'+name];p=a.get_actor_location();p.x=x;a.set_actor_location(p,False,False)
def resize(name,x,width):
 move(name,x);a=by['CH_SmallBath_'+name];s=a.get_actor_scale3d();s.x=width/100;a.set_actor_scale3d(s)
resize('TileFloor',717.5675,395.135)
for suffix in ['Tile','Upper','Trim']:
 resize('Back'+suffix,717.5675,407.135+(2 if suffix=='Trim' else 0))
 resize('Left'+suffix,915.135,3.21+(2 if suffix=='Trim' else 0))
for name in ['Bathroom_Sink','Bathroom_Mirror','Bathroom_Water_Glass','SM_Soap_01','Bathroom_Shower_Head','Bathroom_Towel_Rack2','Bathroom_Towels2']:
 move(name,520-.8*rows[name]['pos'][0]-44.865)
move('Bathroom_Bathtub',520-.8*rows['Bathroom_Bathtub']['pos'][0]-25)
front=by.get('CH_SmallBath_FrontCutaway')
if front:actors.destroy_actor(front)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('BATH_WALL_ALIGNED_FRONT_SILL_REMOVED')
