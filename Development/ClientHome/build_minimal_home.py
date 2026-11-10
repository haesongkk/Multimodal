"""Preserve the Fab example layout; add only the three investigation clues.
Run outside PIE. Initial creation saves a new map, then explicitly opens it.
"""
import unreal as u
import json
from pathlib import Path

ROOT='/Game/ClientHome_Haeso'
SOURCE='/Game/StylizedKitchen/Levels/Stylized_Interior'
MAP=ROOT+'/Maps/Lvl_ClientHome_Minimal'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
dirty=list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
assert all(p.get_name().startswith(ROOT+'/') for p in dirty),'Foreign unsaved changes'
if dirty: assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
if not assets.does_asset_exist(MAP):
    assert levels.load_level(SOURCE)
    assert u.EditorLoadingAndSavingUtils.save_map(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),MAP)
assert levels.load_level(MAP)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
# Retain the original solid wall: this doorway is a level-transition point.
by['House_Walls_SM'].get_component_by_class(u.StaticMeshComponent).set_static_mesh(u.load_asset('/Game/StylizedKitchen/Meshes/SM_House_Walls'))
def tag(a,name): a.set_editor_property('tags',[u.Name(name)])
pot=by['SM_FlowerPot_02']
pot.set_actor_location(u.Vector(740,225,39),False,False)
pot.set_actor_rotation(u.Rotator(pitch=78,yaw=25,roll=0),False)
tag(pot,'Home_Pot')
plant=by['SM_FlowersPlant_02']
plant.set_actor_location(u.Vector(723,214,29),False,False)
plant.set_actor_rotation(u.Rotator(pitch=80,yaw=25,roll=0),False)
for a in [pot,plant]: a.set_actor_enable_collision(False)
# Existing window mesh is opened outward about its far jamb. No replacement art.
window=by['Assets_Proxy_LR_Window_Proxy']
window.set_actor_location(u.Vector(980.4,268.7,209.9),False,False)
window.set_actor_rotation(u.Rotator(pitch=0,yaw=45,roll=0),False)
tag(window,'Home_Window')
door=by['Assets_Proxy_Door_Proxy']
door.get_component_by_class(u.StaticMeshComponent).set_mobility(u.ComponentMobility.MOVABLE)
tag(door,'Home_Door')
def detail(name,xyz,size,material,tag_name=None):
    name='CH_Minimal_'+name
    a=by.get(name)
    if not a:
        a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz)); a.set_actor_label(name); by[name]=a
    c=a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'))
    c.set_material(0,u.load_asset(ROOT+'/Materials/'+material))
    a.set_actor_location(u.Vector(*xyz),False,False)
    a.set_actor_scale3d(u.Vector(*(v/100 for v in size)))
    a.set_actor_enable_collision(False)
    a.set_folder_path('ClientHome/RequiredClues')
    if tag_name: tag(a,tag_name)
    return a
for i,(x,y,s) in enumerate([(739,239,28),(754,246,15),(769,254,8),(789,265,5)]):
    detail('Soil'+str(i),(x,y,23.1),(s,s*.65,.8),'M_CH_Soil')
# The chair-side fur is separated from the pot/window approach, so all clues are reachable.
for i in range(5):
    a=detail('Fur'+str(i),(710+i*1.6,80+(i%2)*2,23.4),(12,1.8,.8),'M_CH_Fur','Home_Fur' if i==0 else None)
    a.set_actor_rotation(u.Rotator(pitch=0,yaw=i*23,roll=0),False)
start=by['PlayerStart']
start.set_actor_location(u.Vector(350,350,120),False,False)
start.set_actor_rotation(u.Rotator(pitch=0,yaw=-10,roll=0),False)
exit_actor=by.get('CH_Minimal_ExitTarget')
if not exit_actor:
    exit_actor=actors.spawn_actor_from_class(u.TargetPoint,u.Vector(390,-330,110))
    exit_actor.set_actor_label('CH_Minimal_ExitTarget')
exit_actor.set_actor_location(u.Vector(390,-330,110),False,False)
exit_actor.set_folder_path('ClientHome/Gameplay')
tag(exit_actor,'Home_Exit')
assert levels.save_current_level()
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(300,-50,175),u.Rotator(pitch=-5,yaw=40,roll=0))
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('CLIENT_HOME_MINIMAL_MAP_OK')
