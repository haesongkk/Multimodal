"""Optional evidence never changes Count, the three-core-clue exit requirement."""
from pathlib import Path
import json
import unreal as u
OUT=Path(__file__).parent
q=lambda v:json.dumps(v,ensure_ascii=False)
get=lambda n:'(Variables|Default|Get'+n+')'
put=lambda n,v:'(Variables|Default|Set'+n+' '+v+')'
CLUES=[(5,'SnackActor','SnackSeen','Home_Snack','먹다 남은 간식',
        '그릇에 간식이 조금 남아 있고 부스러기가 흩어져 있다. 코코가 주방에 들른 듯하다.',
        '남은 간식은 코코가 주방에 들렀다는 흔적이다. 창가의 핵심 단서와 이어 보면, 주방을 거쳐 창문으로 향한 것으로 보인다.'),
       (6,'PawprintsActor','PawprintsSeen','Home_Pawprints','작은 발자국',
        '작은 발자국이 복도를 지나 거실 쪽으로 이어진다. 코코가 집 안에서 이동한 방향을 짐작할 수 있다.',
        '발자국은 복도에서 거실 쪽으로 이어진다. 창가의 핵심 단서와 맞춰 보면, 코코가 거실을 지나 창문으로 향한 경로가 더 분명해진다.')]

def prepare(hud,B):
    known=set(B.list_variables(hud))
    for n,t in [('SnackSeen','bool'),('PawprintsSeen','bool'),('ExtraCount','int')]:
        if n not in known:B.add_variable(hud,n,t)
    for n in ['SnackActor','PawprintsActor']:
        if n not in known:B.add_object_variable(hud,n,u.Actor.static_class())
    B.compile_blueprint(hud)
    code=(OUT/'BP_CH_Interact.dsl').read_text(encoding='utf-8')
    branches=[]
    for idx,actor,seen,tag,title,msg,late in CLUES:
        branches.append(f'(if (== {get("Nearby")} {idx}) (if (not {get(seen)}) {put(seen,"true")} {put("ExtraCount","(+ "+get("ExtraCount")+" 1)")}) {put("Title",q(title+" · 보조 단서"))} {put("Message","(select "+get("Deduced")+" "+q(late)+" "+q(msg)+")")} {put("Popup","true")} (CallFunction|RefreshPopup))')
    code=code.replace('(if (== (Variables|Default|GetNearby) 4)', '\n'.join(branches)+'\n(if (== (Variables|Default|GetNearby) 4)',1)
    B.write_graph_dsl(B.get_graph(hud,'Interact'),code)
    (OUT/'BP_CH_Minimal_Interact.dsl').write_text(code,encoding='utf-8')
    confirm=(OUT/'BP_CH_Confirm.dsl').read_text(encoding='utf-8')
    original='코코는 창문으로 나간 것 같다. 현관문을 열고 밖으로 나가자.'
    both='간식과 발자국을 이어 보면 코코는 주방에서 복도를 지나 거실로 왔다. 털과 넘어진 화분, 열린 창문이 탈출 경로를 가리킨다. 현관으로 나가자.'
    snack='주방의 남은 간식은 코코가 들렀던 흔적이다. 거실의 핵심 단서 세 가지를 보면 마지막에는 창문으로 나간 것 같다. 현관으로 나가자.'
    paw='복도의 발자국은 거실 쪽으로 이어진다. 털과 넘어진 화분, 열린 창문을 함께 보면 코코는 창문으로 나간 것 같다. 현관으로 나가자.'
    message=f'(select {get("SnackSeen")} (select {get("PawprintsSeen")} {q(both)} {q(snack)}) (select {get("PawprintsSeen")} {q(paw)} {q(original)}))'
    confirm=confirm.replace(q(original),message)
    B.write_graph_dsl(B.get_graph(hud,'Confirm'),confirm)
    (OUT/'BP_CH_Minimal_Confirm.dsl').write_text(confirm,encoding='utf-8')

def augment_event(code):
    if 'foundSnackActor' in code:return code
    begin=[];near=[]
    for idx,actor,seen,tag,title,msg,late in CLUES:
        begin.append(f'(bind found{actor} (Actor|GetAllActorswithTag :Tag {q(tag)}))\n(for item found{actor} {put(actor,"item")})')
        distance=f'(Transformation|GetHorizontalDistanceTo :self pawn :OtherActor {get(actor)})'
        prompt=f'(select {get(seen)} {q("[E] "+title+" 다시 확인")} {q("[E] "+title+" 조사 · 보조 단서")})'
        near.append(f'(if (< {distance} {get("NearestDistance")}) {put("NearestDistance",distance)} {put("Nearby",str(idx))} {put("Prompt",prompt)})')
    code=code.replace('(CallFunction|InitPopup)','(CallFunction|InitPopup)\n'+'\n'.join(begin),1)
    code=code.replace('(if (Variables|Default|GetPopup)','\n'.join(near)+'\n(if (Variables|Default|GetPopup)',1)
    return code
