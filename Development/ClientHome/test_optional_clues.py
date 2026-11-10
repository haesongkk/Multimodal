"""Call run('before') or run('after') in fresh PIE to test optional evidence ordering."""
import unreal as u,json
from pathlib import Path

def run(scenario='before'):
    assert scenario in ['before','after']
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    assert world and 'Lvl_ClientHome_Minimal' in world.get_name()
    pawn=u.GameplayStatics.get_player_pawn(world,0)
    hud=u.GameplayStatics.get_player_controller(world,0).get_hud()
    records=[];steps=[];elapsed=0.;index=0
    def p(n):return hud.get_editor_property(n)
    def check(name,value):
        records.append({'test':name,'passed':bool(value)})
        assert value,name
    def step(t,fn):steps.append((t,fn))
    def move(x,y):pawn.set_actor_location(u.Vector(x,y,114),False,False)
    def confirm():hud.call_method('Confirm')
    def interact():hud.call_method('Interact')
    def message():return str(p('PopupUI').get_editor_property('PopupMessage').get_text())
    def core():
        for idx,label,x,y in [(1,'pot',740,320),(2,'fur',650,20),(3,'window',870,350)]:
            step(.1,lambda x=x,y=y:move(x,y));step(.4,interact)
            step(.1,lambda idx=idx:check('core count '+str(idx),p('Count')==idx))
            step(.1,confirm)
        step(.1,lambda:check('three core clues unlock deduction',p('Deduced') and p('Popup')))
        if scenario=='before':step(.1,lambda:check('both optional clues enrich deduction','주방' in message() and '복도' in message()))
        step(.1,confirm)
    step(.4,lambda:check('fresh optional state',p('ExtraCount')==0 and p('Count')==0 and not p('SnackSeen') and not p('PawprintsSeen')))
    step(.1,confirm)
    if scenario=='after':core()
    for count,idx,label,flag,x,y in [(1,5,'snack','SnackSeen',-230,250),(2,6,'pawprints','PawprintsSeen',301,-450)]:
        step(.1,lambda x=x,y=y:move(x,y))
        step(.5,lambda idx=idx,label=label:check(label+' nearest',p('Nearby')==idx))
        step(.1,interact)
        step(.1,lambda count=count,flag=flag,label=label:check(label+' recorded separately',p(flag) and p('ExtraCount')==count and p('Count')==(3 if scenario=='after' else 0) and p('Popup') and '보조 단서' in p('Title')))
        if scenario=='after':step(.1,lambda:check('late evidence updates explanation','창문' in message() and p('Deduced')))
        step(.1,confirm);step(.1,interact)
        step(.1,lambda count=count:check('repeat optional does not increment',p('ExtraCount')==count))
        step(.1,confirm)
    if scenario=='before':
        step(.1,lambda:check('optional evidence alone never unlocks exit',not p('Deduced') and not p('DoorOpen')))
        step(.1,lambda:move(370,-330));step(.5,interact)
        step(.1,lambda:check('door remains locked with only optional clues',p('Popup') and not p('DoorOpen')))
        step(.1,confirm);core()
    step(.1,lambda:check('final counts remain core three optional two',p('Count')==3 and p('ExtraCount')==2 and p('Deduced')))
    def finish(error=None):
        u.unregister_slate_post_tick_callback(handle)
        Path('D:/Multimodal/Saved/ClientHome/optional-'+scenario+'-test.json').write_text(json.dumps({'passed':error is None,'error':error,'checks':records},ensure_ascii=False,indent=2),encoding='utf-8')
        u.log('OPTIONAL_'+scenario.upper()+'_TEST: '+str(error or 'PASS'))
    def tick(dt):
        nonlocal index,elapsed
        try:
            elapsed+=dt
            if elapsed<steps[index][0]:return
            elapsed=0.;steps[index][1]();index+=1
            if index==len(steps):finish()
        except Exception as e:finish(str(e))
    handle=u.register_slate_post_tick_callback(tick)
