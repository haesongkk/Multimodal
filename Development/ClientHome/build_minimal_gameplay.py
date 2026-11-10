"""Original fixed overhead controls and existing investigation UI for the minimal-layout home.
All gameplay Blueprints are copies; the blockout gameplay remains unchanged.
"""
import unreal as u
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B, _BlueprintCache
from editor_toolset.toolsets.actor import ActorTools as A
import toolset_registry
ROOT='/Game/ClientHome_Haeso'
MAP=ROOT+'/Maps/Lvl_ClientHome_Minimal'
OUT=Path(__file__).resolve().parent
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(MAP+'.')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
def clone(name):
    dst=ROOT+'/Blueprints/'+name+'_Minimal'
    return u.load_asset(dst) if assets.does_asset_exist(dst) else assets.duplicate_asset(ROOT+'/Blueprints/'+name,dst)
def build():
    player,hud,mode=[clone(n) for n in ['BP_CH_Player','BP_CH_HUD','BP_CH_GameMode']]
    for bp in [player,hud,mode]: _BlueprintCache.invalidate(bp)
    pcdo=u.get_default_object(player.generated_class())
    pcdo.set_editor_property('use_controller_rotation_yaw',False)
    pcdo.get_component_by_class(u.CharacterMovementComponent).set_editor_property('max_walk_speed',270)
    import runpy
    runpy.run_path(str(OUT/'minimal_follow_camera.py'))['configure'](player,B,A)
    pcdo=u.get_default_object(player.generated_class())
    runpy.run_path(str(OUT/'configure_manny.py'))['configure'](player,B,A)
    if 'ExitActor' not in B.list_variables(hud): B.add_object_variable(hud,'ExitActor',u.Actor.static_class())
    optional=runpy.run_path(str(OUT/'optional_clue_graphs.py'))
    optional['prepare'](hud,B)
    B.compile_blueprint(hud)
    graph=B.get_graph(hud,'EventGraph')
    def call(name,args=''):
        ids=sorted(set(v for v in B.find_node_types(graph,name) if v.split('|')[-1]==name))
        assert len(ids)==1,(name,ids)
        B.get_node_type_pins(graph,ids[0])
        return '('+ids[0]+' '+args+')'
    code=(OUT/'BP_CH_HUD.dsl').read_text(encoding='utf-8')
    extra='(bind foundExitActor (Actor|GetAllActorswithTag :Tag "Home_Exit"))\n(for item foundExitActor (Variables|Default|SetExitActor item))\n'
    code=code.replace('(CallFunction|InitPopup)','(CallFunction|InitPopup)\n'+extra,1)
    # The doorway threshold follows a scene marker, not blockout world coordinates.
    code=code.replace('(< (.y position) -570.0)','(< (Transformation|GetHorizontalDistanceTo :self pawn :OtherActor (Variables|Default|GetExitActor)) 65.0)')
    code=code.replace('(and (Variables|Default|GetDoorOpen) (< (Transformation|GetHorizontalDistanceTo',
                      '(and (>= (Variables|Default|GetDoorAngle) 90.0) (< (Transformation|GetHorizontalDistanceTo')
    code=code.replace('단서 3개를 확인하고 현관을 나왔다. 다음 목적지는 골목이다.','단서 3개를 확인하고 현관문을 열었다. 다음 목적지는 골목이다.')
    code=code.replace('165.0','175.0')
    # Screen-relative movement for the camera looking toward the window wall (+X).
    import re
    directions={'0,1,0':'1,0,0','0,-1,0':'-1,0,0','1,0,0':'0,-1,0','-1,0,0':'0,1,0'}
    code=re.sub(r':WorldDirection "([0-9,\-]+)"',lambda m: ':WorldDirection "'+directions[m[1]]+'"',code)
    code=code.replace('코코가 집 밖으로 나간 경로를 찾아보자.','창가의 화분, 의자 주변의 털, 열린 창문을 조사하자.')
    import runpy
    make_hud=runpy.run_path(str(OUT/'minimal_hud_layout.py'))['make_hud']
    code=code[:code.index('(event EventReceiveDrawHUD')]+make_hud(graph,B)
    code=optional['augment_event'](code)
    B.write_graph_dsl(graph,code)
    (OUT/'BP_CH_Minimal_HUD.dsl').write_text(code,encoding='utf-8')
    B.compile_blueprint(hud,True)
    mcdo=u.get_default_object(mode.generated_class())
    mcdo.set_editor_property('default_pawn_class',player.generated_class())
    mcdo.set_editor_property('hud_class',hud.generated_class())
    B.compile_blueprint(mode,True)
    # Preserve the ceiling asset and placement, hide it only during gameplay.
    for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
        if actor.get_actor_label() in {'House_Ceiling_SM', 'Cube3'}: actor.set_actor_hidden_in_game(True)
    world.get_world_settings().set_editor_property('default_game_mode',mode.generated_class())
    for bp in [player,hud,mode]: assert assets.save_loaded_asset(bp)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
    u.log('CLIENT_HOME_MINIMAL_GAMEPLAY_OK')
language=u.InternationalizationLibrary.get_current_language()
try:
    u.InternationalizationLibrary.set_current_language('en',False)
    with toolset_registry.tool_raising_exceptions(): build()
finally:
    u.InternationalizationLibrary.set_current_language(language,False)
