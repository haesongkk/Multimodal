"""Shift the six wall pictures camera-left, preserving their original arrangement."""
import json
from pathlib import Path
import unreal as u
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
labels={'SM_Frames_06','SM_Frames_7','SM_Frames_8','SM_Frames_10','SM_Frames_11','SM_Frames_13'}
rows=json.loads(Path('D:/Multimodal/Saved/ClientHome/spread-clues-before.json').read_text())
by={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
count=0
for row in rows:
 if row['label'] in labels:
  x,y,z=row['pos']
  by[row['label']].set_actor_location(u.Vector(x+45,y,z),False,False)
  count+=1
assert count==6
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('WALL_PICTURES_SHIFTED_LEFT_6')
