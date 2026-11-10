"""Owned-folder-only UE 5.8 gameplay builder. Execute in editor Python.

Creates cooked Blueprint logic, not an editor-only Python gameplay loop.
Shared project settings/assets are never saved or modified.
"""
import json
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.actor import ActorTools as A

ROOT = '/Game/ClientHome_Haeso'
MAP = ROOT + '/Maps/Lvl_ClientHome_Blockout'
OUT = Path('D:/Multimodal/Development/ClientHome')
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
levels = u.get_editor_subsystem(u.LevelEditorSubsystem)

def bp(name, parent):
    path = ROOT + '/Blueprints/' + name
    return u.load_asset(path) or B.create(ROOT + '/Blueprints', name, parent.static_class())

def component(blueprint, cls, name):
    cdo = u.get_default_object(blueprint.generated_class())
    found = A.get_components(cdo, cls.static_class())
    chosen = next((c for c in found if c.get_name() == name + '_GEN_VARIABLE'), None)
    if chosen is None and found: chosen = found[0]
    for c in found:
        if c != chosen: A.remove_component(c)
    return chosen or A.add_component(blueprint, cls.static_class(), name)

def build():
    world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    assert world.get_path_name().startswith(MAP + '.'), 'Open only owned map first'
    dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    assert all(p.get_name().startswith(ROOT + '/') for p in dirty), 'Foreign unsaved package: stop'
    player = bp('BP_CH_Player', u.Character)
    hud = bp('BP_CH_HUD', u.HUD)
    mode = bp('BP_CH_GameMode', u.GameModeBase)
    doorbp = bp('BP_CH_Door', u.Actor)
    # Independent character. Basic shapes are deliberately temporary art.
    pcdo = u.get_default_object(player.generated_class())
    pcdo.set_editor_property('use_controller_rotation_yaw', False)
    pcdo.get_component_by_class(u.CharacterMovementComponent).set_editor_property('max_walk_speed', 270.0)
    camera = component(player, u.CameraComponent, 'ViewCamera')
    camera.set_editor_property('relative_location', u.Vector(0, -850, 1400))
    camera.set_editor_property('relative_rotation', u.Rotator(pitch=-58, yaw=90, roll=0))
    camera.set_editor_property('absolute_location', True)
    camera.set_editor_property('absolute_rotation', True)
    camera.set_editor_property('field_of_view', 65.0)
    # Existing component templates are addressed through the blueprint API.
    body = component(player, u.StaticMeshComponent, 'Body')
    body.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cylinder'))
    body.set_editor_property('relative_scale3d', u.Vector(.5, .5, 1.2))
    body.set_material(0, u.load_asset(ROOT + '/Materials/M_CH_Exit'))
    body.set_collision_profile_name('NoCollision')
    B.compile_blueprint(player)
    # A hinged door with its visual offset from the pivot, rather than rotating its centre.
    dcdo = u.get_default_object(doorbp.generated_class())
    leaf = component(doorbp, u.StaticMeshComponent, 'DoorLeaf')
    leaf.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
    leaf.set_editor_property('relative_location', u.Vector(70, 0, 115))
    leaf.set_editor_property('relative_scale3d', u.Vector(1.4, .12, 2.3))
    leaf.set_editor_property('mobility', u.ComponentMobility.MOVABLE)
    leaf.set_material(0, u.load_asset(ROOT + '/Materials/M_CH_Exit'))
    leaf.set_collision_profile_name('BlockAllDynamic')
    B.compile_blueprint(doorbp)
    known = set(B.list_variables(hud))
    for name, typ in [('PotSeen','bool'),('FurSeen','bool'),('WindowSeen','bool'),('Popup','bool'),('Deduced','bool'),('DoorOpen','bool'),('Complete','bool'),('Count','int'),('Nearby','int'),('DoorAngle','float'),('Title','string'),('Message','string'),('Prompt','string')]:
        if name not in known: B.add_variable(hud,name,typ)
    for name in ['PotActor','FurActor','WindowActor','DoorActor']:
        if name not in known: B.add_object_variable(hud,name,u.Actor.static_class())
    graph = B.get_graph(hud, 'EventGraph')
    interact_graph = B.add_function_graph(hud, 'Interact')
    confirm_graph = B.add_function_graph(hud, 'Confirm')
    B.compile_blueprint(hud)
    cache = {}
    def node(name, prefix=None):
        key = (name,prefix)
        if key not in cache:
            ids = sorted(set(v for v in B.find_node_types(graph,name) if v.split('|')[-1] == name and (prefix is None or v.startswith(prefix))))
            if prefix and prefix + name in ids: ids = [prefix + name]
            assert len(ids)==1, (name,ids)
            cache[key]=ids[0]
            B.get_node_type_pins(graph,ids[0])
        return cache[key]
    def call(name, args='', prefix=None): return '(' + node(name,prefix) + (' '+args if args else '') + ')'
    def get(n): return call('Get'+n,prefix='Variables|')
    def put(n,v): return call('Set'+n,v,prefix='Variables|')
    def q(s): return json.dumps(s,ensure_ascii=False)
    def popup(title,message): return '\n'.join([put('Title',q(title)),put('Message',q(message)),put('Popup','true')])
    def key(k,pressed=False): return call('WasInputKeyJustPressed' if pressed else 'IsInputKeyDown', ':self controller :Key '+q(k))
    def text(s,x,y,scale=1.2,color='(R=0.92,G=0.93,B=0.9,A=1)'):
        return call('DrawText',f':Text {s} :ScreenX {x} :ScreenY {y} :Scale {scale} :TextColor {q(color)}', 'HUD|')
    def rect(x,y,w,h,col): return call('DrawRect',f':ScreenX {x} :ScreenY {y} :ScreenW {w} :ScreenH {h} :RectColor {q(col)}','HUD|')
    begin=[]
    for var,tag in [('PotActor','Home_Pot'),('FurActor','Home_Fur'),('WindowActor','Home_Window'),('DoorActor','Home_Door')]:
        begin.append(f'(bind found{var} '+call('GetAllActorswithTag',':Tag '+q(tag))+f')\n(for item found{var} '+put(var,'item')+')')
    begin += [popup('의뢰인 집', '코코가 남긴 흔적을 찾아보자. 화분, 털, 창문을 조사하자.')]
    tick=['(bind controller '+call('GetOwningPlayerController',prefix='HUD|')+')','(bind pawn '+call('GetOwningPawn',prefix='HUD|')+')']
    # Pure validity checks prevent early initialization or teardown access errors.
    valid_node = node('IsValid','Utilities|')
    active=[]
    active.append(put('Nearby','0'))
    active.append(put('Prompt',q('주변에서 코코의 흔적을 찾아보자.')))
    for idx,var,label in [(1,'PotActor','넘어진 화분'),(2,'FurActor','고양이 털'),(3,'WindowActor','열린 창문'),(4,'DoorActor','현관문')]:
        distance=call('GetHorizontalDistanceTo',':self pawn :OtherActor '+get(var))
        active.append(f'(if (< {distance} 165.0) {put("Nearby",str(idx))} {put("Prompt",q("[E] "+label+" 조사 / 확인"))})')
    moves=[]
    for k,v in [('W','0,1,0'),('S','0,-1,0'),('A','1,0,0'),('D','-1,0,0')]:
        moves.append(call('AddMovementInput',':self pawn :WorldDirection '+q(v)+f' :ScaleValue (select {key(k)} 1.0 0.0)'))
    investigations=[]
    for idx,flag,title,msg in [(1,'PotSeen','넘어진 화분','화분이 떨어져 있다. 코코가 지나가다 떨어뜨린 것으로 추정된다.'),(2,'FurSeen','고양이 털','코코의 털 같다. 창가 쪽으로 이동한 흔적이 남아 있다.'),(3,'WindowSeen','열린 창문','창문이 열려 있다. 코코가 이곳으로 빠져나갔을 가능성이 높다.')]:
        investigations.append(f'(if (== {get("Nearby")} {idx}) (if (not {get(flag)}) {put(flag,"true")} {put("Count","(+ "+get("Count")+" 1)")}) {popup(title,msg)})')
    investigations.append(f'(if (== {get("Nearby")} 4) (if {get("Deduced")} {put("DoorOpen","true")} (else {popup("아직 남은 흔적", "집 안의 단서 세 가지를 먼저 확인하자.")})))')
    confirm_code=f'(fn Confirm () (if (and {get("Popup")} (not {get("Complete")})) {put("Popup","false")} (if (and (== {get("Count")} 3) (not {get("Deduced")})) {put("Deduced","true")} {popup("추리 완료", "코코는 창문으로 나간 것 같다. 현관문을 열고 밖으로 나가자.")})))'
    interact_code=f'(fn Interact () (if (and (not {get("Popup")}) (not {get("Complete")})) '+'\n'.join(investigations)+'))'
    B.write_graph_dsl(confirm_graph,confirm_code)
    B.write_graph_dsl(interact_graph,interact_code)
    (OUT/'BP_CH_Confirm.dsl').write_text(confirm_code,encoding='utf-8')
    (OUT/'BP_CH_Interact.dsl').write_text(interact_code,encoding='utf-8')
    close=f'(if {key("Enter",True)} {call("Confirm")})'
    active.append(f'(if {get("Popup")} {close} (else '+ '\n'.join(moves)+f'\n(if {key("E",True)} {call("Interact")})))' )
    # The angle advances with delta seconds and clamps to exactly 90 degrees.
    angle=f'(select (> (+ {get("DoorAngle")} (* DeltaSeconds 100.0)) 90.0) 90.0 (+ {get("DoorAngle")} (* DeltaSeconds 100.0)))'
    rotation=call('MakeRotator',':Yaw (- '+get('DoorAngle')+')')
    active.append(f'(if {get("DoorOpen")} {put("DoorAngle",angle)} '+call('SetActorRotation',':self '+get('DoorActor')+' :NewRotation '+rotation)+')')
    loc=call('GetActorLocation',':self pawn')
    active.append(f'(bind position {loc})\n(if (and {get("DoorOpen")} (< (.y position) -570.0)) {put("Complete","true")} {popup("집 조사 완료", "단서 3개를 확인하고 현관을 나왔다. 다음 목적지는 골목이다.")})')
    tick.append(f'({valid_node} :InputObject pawn (:"Is Valid" (if (not {get("Complete")}) '+'\n'.join(active)+')) (:"Is Not Valid"))')
    draw=[rect('20.0','20.0','540.0','132.0','(R=0.025,G=0.04,B=0.05,A=0.94)'),text(q('묘한 흔적을 찾아서  /  의뢰인 집'),'38.0','34.0',1.5),text(q('WASD 이동   ·   E 조사   ·   Enter 확인'),'38.0','68.0'),text('(select (== '+get('Count')+' 0) '+q('조사한 단서: 0 / 3')+' (select (== '+get('Count')+' 1) '+q('조사한 단서: 1 / 3')+' (select (== '+get('Count')+' 2) '+q('조사한 단서: 2 / 3')+' '+q('조사한 단서: 3 / 3')+')))','38.0','96.0'),text(get('Prompt'),'38.0','124.0',1.05)]
    draw.append(f'(if {get("Deduced")} '+text(q('추리: 창문으로 탈출  →  현관으로 나가기'),'38.0','166.0',1.2)+')')
    panel=[rect('(* SizeX 0.10)','(* SizeY 0.62)','(* SizeX 0.80)','210.0','(R=0.02,G=0.035,B=0.045,A=0.98)'),text(get('Title'),'(+ (* SizeX 0.10) 28.0)','(+ (* SizeY 0.62) 22.0)',1.7,'(R=1,G=0.72,B=0.32,A=1)'),text(get('Message'),'(+ (* SizeX 0.10) 28.0)','(+ (* SizeY 0.62) 72.0)',1.15),text(q('[Enter] 확인'),'(+ (* SizeX 0.10) 28.0)','(+ (* SizeY 0.62) 144.0)',1.2)]
    draw.append(f'(if {get("Popup")} '+'\n'.join(panel)+')')
    code='(event EventBeginPlay\n'+'\n'.join(begin)+')\n(event EventTick (DeltaSeconds)\n'+'\n'.join(tick)+')\n(event EventReceiveDrawHUD (SizeX SizeY)\n'+'\n'.join(draw)+')'
    (OUT/'BP_CH_HUD.dsl').write_text(code,encoding='utf-8')
    B.write_graph_dsl(graph,code)
    mcdo=u.get_default_object(mode.generated_class())
    mcdo.set_editor_property('default_pawn_class',player.generated_class())
    mcdo.set_editor_property('hud_class',hud.generated_class())
    B.compile_blueprint(mode)
    world.get_world_settings().set_editor_property('default_game_mode',mode.generated_class())
    by_label={a.get_actor_label():a for a in actors.get_all_level_actors()}
    for name,xyz,rot,scale in [('CH_PlayerStart',(-400,-340,100),(0,0,0),(1,1,1)),('CH_Clue_Pot',(80,160,22),(75,15,0),(.42,.42,.55)),('CH_Sun',(0,0,650),(-55,-35,0),(1,1,1))]:
        a=by_label[name]
        a.set_actor_location(u.Vector(*xyz),False,False)
        a.set_actor_rotation(u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False)
        a.set_actor_scale3d(u.Vector(*scale))
    old=by_label.get('CH_Door_Open_Placeholder')
    if old: actors.destroy_actor(old)
    door=by_label.get('CH_Door')
    if not door: door=actors.spawn_actor_from_class(doorbp.generated_class(),u.Vector(-470,-500,0))
    door.set_actor_label('CH_Door')
    door.set_editor_property('tags',[u.Name('Home_Door')])
    door.set_folder_path('ClientHome/Gameplay')
    for b in [player,hud,mode,doorbp]:
        B.compile_blueprint(b,True)
        assert assets.save_loaded_asset(b)
    assert levels.save_current_level()
    u.log('CLIENT_HOME_GAMEPLAY_BUILD_OK')

previous_language=u.InternationalizationLibrary.get_current_language()
try:
    u.InternationalizationLibrary.set_current_language('en',False)
    import toolset_registry
    with toolset_registry.tool_raising_exceptions():
        build()
except Exception:
    import traceback
    u.log_error(traceback.format_exc())
    raise
finally:
    u.InternationalizationLibrary.set_current_language(previous_language,False)
