"""Smoke-test the original town game after moving its packages."""
import unreal as u
import json
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world
pawn=u.GameplayStatics.get_player_pawn(world,0)
controller=u.GameplayStatics.get_player_controller(world,0)
mode=u.GameplayStatics.get_game_mode(world)
report={'classes':{k:v.get_class().get_path_name() for k,v in {'pawn':pawn,'controller':controller,'mode':mode}.items()},'checks':{}}
report['checks']['new_game_classes']=all(p.startswith(('/Game/Multimodal/02_Blueprints/','/Script/Engine.')) for p in report['classes'].values())
report['checks']['controller_possession']=pawn.get_controller()==controller
report['checks']['movement_component']=bool(pawn.get_component_by_class(u.CharacterMovementComponent))
report['checks']['mesh_loaded']=any(c.get_editor_property('static_mesh') for c in pawn.get_components_by_class(u.StaticMeshComponent)) or any(c.get_editor_property('skeletal_mesh_asset') for c in pawn.get_components_by_class(u.SkeletalMeshComponent))
start=pawn.get_actor_location()
elapsed=0
def tick(dt):
    global elapsed
    elapsed+=dt
    pawn.add_movement_input(u.Vector(-1,0,0),1.0,True)
    if elapsed<1.5:return
    u.unregister_slate_post_tick_callback(handle)
    end=pawn.get_actor_location()
    report['distance']=((end.x-start.x)**2+(end.y-start.y)**2)**.5
    report['checks']['movement_changes_position']=report['distance']>10
    report['success']=all(report['checks'].values())
    Path('D:/Multimodal/Outputs/Organization20261113/TownPlay.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
handle=u.register_slate_post_tick_callback(tick)
