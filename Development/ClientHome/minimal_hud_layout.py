"""Canvas HUD for the fixed top-down home. No world art changes."""
import json

def make_hud(graph, blueprint_tools):
    for node in ['HUD|Project']:
        blueprint_tools.get_node_type_pins(graph, node)
    q = lambda s: json.dumps(s, ensure_ascii=False)
    get = lambda n: '(Variables|Default|Get'+n+')'
    dark = '"(R=0.018,G=0.03,B=0.035,A=0.88)"'
    white = '"(R=0.94,G=0.95,B=0.9,A=1)"'
    gold = '"(R=1,G=0.73,B=0.32,A=1)"'
    mint = '"(R=0.4,G=0.9,B=0.7,A=1)"'
    def rect(x,y,w,h,color=dark):
        return f'(HUD|DrawRect :ScreenX {x} :ScreenY {y} :ScreenW {w} :ScreenH {h} :RectColor {color})'
    def text(t,x,y,scale='1.1',color=white):
        return f'(HUD|DrawText :Text {t} :ScreenX {x} :ScreenY {y} :Scale {scale} :TextColor {color})'
    out=['(event EventReceiveDrawHUD (SizeX SizeY)',rect('18','16','250','64'),
         text(q('의뢰인 집  /  흔적 찾기'),'32','25','1.25'),
         text(q('WASD 이동 · E 조사 · Enter 확인'),'32','54','0.95'),
         rect('(- SizeX 224)','16','206','90')]
    count=f'(select (== {get("Count")} 0) "핵심 단서 0 / 3" (select (== {get("Count")} 1) "핵심 단서 1 / 3" (select (== {get("Count")} 2) "핵심 단서 2 / 3" "핵심 단서 3 / 3")))'
    out += [text(count,'(- SizeX 208)','25','1.25',gold),
            text(f'(select (== {get("ExtraCount")} 0) "보조 단서 0 / 2 · 선택" (select (== {get("ExtraCount")} 1) "보조 단서 1 / 2 · 선택" "보조 단서 2 / 2 · 선택"))','(- SizeX 208)','53','1.0',mint),
            text(f'(select {get("Deduced")} "현관으로 이동하세요" "주변의 흔적을 살펴보세요")','(- SizeX 208)','80','0.95')]
    out += [f'(if (not {get("Popup")})',rect('18','(- SizeY 58)','(- SizeX 36)','40'),
            text(get('Prompt'),'32','(- SizeY 47)','1.2')]
    # Local hints are revealed on approach, and the active target alone gets an E label.
    for index,actor,seen,label in [(1,'PotActor','PotSeen','화분'),(2,'FurActor','FurSeen','털'),(3,'WindowActor','WindowSeen','창문'),(4,'ExitActor','Deduced','현관'),(5,'SnackActor','SnackSeen','간식'),(6,'PawprintsActor','PawprintsSeen','발자국')]:
        target=get(actor); point='mark'+str(index)
        condition=f'(< (Transformation|GetHorizontalDistanceTo :self (HUD|GetOwningPawn) :OtherActor {target}) 350.0)'
        if index==4: condition=f'(and {get("Deduced")} {condition})'
        out += [f'(if {condition}',f'(bind {point} (HUD|Project :Location (Transformation|GetActorLocation :self {target})))']
        x=f'(.x {point})'; y=f'(.y {point})'
        out += [rect(f'(- {x} 6)',f'(- {y} 6)','12','12'),
                f'(if {get(seen)}',
                rect(f'(- {x} 4)',f'(- {y} 1)','8','2',mint),
                rect(f'(- {x} 1)',f'(- {y} 4)','2','8',mint),
                '(else',
                rect(f'(- {x} 4)',f'(- {y} 1)','8','2',gold),
                rect(f'(- {x} 1)',f'(- {y} 4)','2','8',gold),'))',
                f'(if (== {get("Nearby")} {index})',
                rect(f'(+ {x} 12)',f'(- {y} 32)','126','28'),
                text(q('[E] '+label),f'(+ {x} 20)',f'(- {y} 27)','1.1',gold),'))']
    out += ['))']
    return '\n'.join(out)+'\n'
