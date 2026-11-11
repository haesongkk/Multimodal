"""Five equally weighted clues and the cozy journal bridge. No scene edits."""
import unreal as u,runpy,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
ROOT='/Game/ClientHome_Haeso';OUT=Path(__file__).parent
q=lambda s:json.dumps(s,ensure_ascii=False)
get=lambda n:'(Variables|Default|Get'+n+')'
put=lambda n,v:'(Variables|Default|Set'+n+' '+v+')'
CLUES=[(1,'PotSeen','넘어진 화분','앗, 화분이 넘어졌네. 흙 위의 작은 자국이 창가 쪽으로 이어져 있어.'),
(2,'FurSeen','보송보송한 털','의자 옆에 보드라운 털이 한 움큼! 코코가 이곳을 스쳐 지나갔나 봐.'),
(3,'WindowSeen','살짝 열린 창문','커튼 사이로 바람이 솔솔. 코코가 이 틈으로 나간 걸까? 다른 흔적과 이어 보자.'),
(5,'SnackSeen','먹다 남은 간식','간식 그릇이 비어 가고 바닥에는 부스러기가 남았어. 코코가 주방에서 냠냠했나 봐.'),
(6,'PawprintsSeen','콩콩, 작은 발자국','복도에서 거실로 이어지는 작은 발자국. 코코가 어디로 갔는지 수첩에 적어 두자.')]
def build():
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    hud=u.load_asset(ROOT+'/Blueprints/BP_CH_HUD_Minimal');popup=u.load_asset(ROOT+'/UI/WBP_CH_Popup')
    _BlueprintCache.invalidate(hud)
    # Preserve the existing variable for old serialized assets, but it is no longer read or written.
    lines=['(fn Interact ()',f'(if (and (not {get("Popup")}) (not {get("Complete")}))']
    for i,seen,title,msg in CLUES:
        lines += [f'(if (== {get("Nearby")} {i})',f'(if (not {get(seen)}) {put(seen,"true")} {put("Count","(+ "+get("Count")+" 1)")})',put('Title',q(title)),put('Message',q(msg)),put('Popup','true'),'(CallFunction|RefreshPopup))']
    lines += [f'(if (== {get("Nearby")} 4) (if {get("Deduced")} {put("DoorOpen","true")} (else {put("Title",q("조금만 더 찾아볼까?"))} {put("Message",q("집 안에 남은 단서 다섯 개를 모두 찾아보자. 코코가 지나간 길이 보일 거야."))} {put("Popup","true")} (CallFunction|RefreshPopup))))))']
    code='\n'.join(lines);B.write_graph_dsl(B.get_graph(hud,'Interact'),code);(OUT/'BP_CH_Minimal_Interact.dsl').write_text(code,encoding='utf-8')
    code=f'''(fn Confirm () (if (and {get('Popup')} (not {get('Complete')}))
{put('Popup','false')} (CallFunction|RefreshPopup)
(if (and (== {get('Count')} 5) (not {get('Deduced')}))
{put('Deduced','true')} {put('Title',q('코코의 길을 찾았어!'))}
{put('Message',q('간식을 먹고, 복도를 콩콩 지나 거실로! 털과 넘어진 화분, 열린 창문까지 이어 보니 코코는 창밖으로 나간 게 틀림없어. 이제 현관으로 나가 찾아보자.'))}
{put('Popup','true')} (CallFunction|RefreshPopup))))'''
    B.write_graph_dsl(B.get_graph(hud,'Confirm'),code);(OUT/'BP_CH_Minimal_Confirm.dsl').write_text(code,encoding='utf-8')
    # Small explicit bridge avoids expensive UMG bindings and keeps gameplay in the HUD.
    g=B.add_function_graph(hud,'SyncJournal');B.write_graph_dsl(g,'(fn SyncJournal ())')
    e=u.BlueprintGraphEditor.get_graph_editor(g);entry=next(n for n in e.list_all_nodes() if isinstance(n,u.K2Node_FunctionEntry))
    def pin(n,name,out=False):
        info=B.get_node_infos([n])[0];return next(p.pin_id for p in (info.output_pins if out else info.input_pins) if p.name==name)
    def link(a,ap,b,bp):B.connect_pins(pin(a,ap,True),pin(b,bp))
    call=e.add_call_function_node(popup.generated_class().get_path_name()+':UpdateJournal');link(entry,'then',call,'execute')
    for name,target in [('PopupUI','self'),('Count','Found'),('Prompt','Hint'),('Deduced','Solved')]:
        ids=sorted(set(i for i in B.find_node_types(g,'Get'+name) if i.startswith('Variables|') and i.split('|')[-1]=='Get'+name));assert len(ids)==1
        B.get_node_type_pins(g,ids[0]);n=B.create_node(g,ids[0],u.IntPoint(0,0));link(n,name,call,target)
    B.compile_blueprint(hud,True)
    g=B.get_graph(hud,'EventGraph')
    code=(OUT/'BP_CH_Minimal_HUD.dsl').read_text(encoding='utf-8');code=code[:code.index('(event EventReceiveDrawHUD')]
    code=code.replace('(event EventTick (DeltaSeconds)','(event EventTick (DeltaSeconds)\n(CallFunction|SyncJournal)',1) if '(CallFunction|SyncJournal)' not in code else code
    code=code.replace(' · 보조 단서','').replace('단서 3개를 확인하고 현관문을 열었다. 다음 목적지는 골목이다.','다섯 가지 흔적을 모두 수첩에 담았어. 코코를 찾아 골목으로 가 보자!')
    code=code.replace('창가의 화분, 의자 주변의 털, 열린 창문을 조사하자.','코코가 어디로 갔을까? 집 안에 남은 다섯 가지 흔적을 찾아보자.')
    code=code.replace('주변에서 코코의 흔적을 찾아보자.','코코가 남긴 흔적을 찾아보자.').replace('(Variables|Default|SetTitle "의뢰인 집")','(Variables|Default|SetTitle "코코는 어디로 갔을까?")')
    code+=runpy.run_path(str(OUT/'minimal_hud_layout.py'))['make_hud'](g,B)
    B.write_graph_dsl(g,code);B.compile_blueprint(hud,True)
    assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(hud)
    (OUT/'BP_CH_Minimal_HUD.dsl').write_text(code,encoding='utf-8')
    u.log('COZY_FIVE_CLUES_OK')
if __name__=='__main__':
    import toolset_registry
    lang=u.InternationalizationLibrary.get_current_language()
    try:
        u.InternationalizationLibrary.set_current_language('en',False)
        with toolset_registry.tool_raising_exceptions():build()
    finally:u.InternationalizationLibrary.set_current_language(lang,False)
