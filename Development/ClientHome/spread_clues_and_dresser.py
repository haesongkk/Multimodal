"""Spread clue sites and move the window dresser to the same wall immediately to the right of the window."""
import unreal as u,json
from pathlib import Path
base=Path('D:/Multimodal/Saved/ClientHome');editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
assert (base/'Lvl_ClientHome_Minimal.before-spread-clues.umap').exists()
rows=json.loads((base/'spread-clues-before.json').read_text())
source={row['label']:row for row in rows}
plant_pots=[row for row in rows if not row['hidden'] and row['label'].startswith('SM_FlowerPot') and row['pos'][0]>735 and row['pos'][1]>475]
# Translate the original authored cluster intact, preserving its irregular spacing.
plant_targets={row['label']:(row['pos'][0]-260,row['pos'][1]-20) for row in plant_pots}
# Tuck the two foremost pots into the open sides of the cluster.
plant_targets.update({'SM_FlowerPot_20':(665,575),'SM_FlowerPot_21':(430,580)})
actors=u.get_editor_subsystem(u.EditorActorSubsystem);by={a.get_actor_label():a for a in actors.get_all_level_actors()};report={}
for row in rows:
 n=row['label'];a=by.get(n)
 if not a:continue
 x,y,z=row['pos'];p,yaw,r=row['rot'];new=None;turn=0
 if n.startswith('CH_Minimal_Fur'):
  new=(x-665,y-280,z)
 elif n.startswith('CH_Minimal_Pawprint'):
  pad=source[n.split('_Toe')[0]+'_Pad'] if '_Toe' in n else row
  px,py,_=pad['pos']
  new=(155-(2*py-y+520),285+(2*px-x-301),z+2.5);turn=270
 elif n in ['Assets_Proxy_LR_Desk_Proxy2','SM_Radio','SM_Bottles_7','SM_FlowerPot_22','SM_FlowersPlant_25']:
  new=(x,y+230,z)
 elif not row['hidden'] and n.startswith(('SM_FlowerPot','SM_FlowersPlant')) and x>735 and y>475:
  pot=min(plant_pots,key=lambda row:(row['pos'][0]-x)**2+(row['pos'][1]-y)**2)
  tx,ty=plant_targets[pot['label']];px,py,_=pot['pos']
  new=(tx+x-px,ty+y-py,z)
  a.set_actor_hidden_in_game(False);a.set_is_temporarily_hidden_in_editor(False)
 elif n in ['SM_FlowerPot_02','SM_FlowersPlant_02'] or n.startswith('CH_Minimal_Soil'):
  new=(x,y+230,z)
 if new:
  a.set_actor_location(u.Vector(*new),False,False)
  a.set_actor_rotation(u.Rotator(pitch=p,yaw=yaw+turn,roll=r),False)
  report[n]=list(new)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(base/'spread-clues-report.json').write_text(json.dumps(report,indent=2))
u.log('SPREAD_CLUES_SAVED '+str(len(report)))
