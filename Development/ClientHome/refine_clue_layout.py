"""Refine only clue dressing, preserving the example furniture and camera."""
import unreal as u
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name('build_optional_clues.py')))
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
# A tapered spill keeps the large pot readable and leads toward the window.
for i,(x,y,size) in enumerate([(739,239,32),(758,250,18),(778,261,10),(797,275,5)]):
    a=by['CH_Minimal_Soil'+str(i)]
    a.set_actor_location(u.Vector(x,y,23.6),False,False)
    a.set_actor_scale3d(u.Vector(size/100,size*.65/100,.008))
# A loose, pale tuft at the chair edge, away from the pot's dark soil.
for i,(x,y,yaw,length) in enumerate([(700,75,-25,15),(704,78,20,13),(708,73,48,16),(711,79,-8,12),(715,76,70,10)]):
    a=by['CH_Minimal_Fur'+str(i)]
    a.set_actor_location(u.Vector(x,y,23.8),False,False)
    a.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_scale3d(u.Vector(length/100,.024,.009))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('CLUE_LAYOUT_REFINED_OK')
