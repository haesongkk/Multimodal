"""Fresh PIE test: actual nearest-target selection and equally weighted clues."""
import unreal as u,json
from pathlib import Path

def run(scenario='core_first'):
    world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();assert world
    hud=u.GameplayStatics.get_player_controller(world,0).get_hud();pawn=u.GameplayStatics.get_player_pawn(world,0)
    p=lambda n:hud.get_editor_property(n)
    ui=p('PopupUI');records=[];steps=[];elapsed=0.;index=0
    positions={1:(740,320),2:(650,20),3:(870,350),5:(-230,-100),6:(301,-450),4:(-760,-238)}
    order=(1,2,3,5,6) if scenario=='core_first' else (5,6,3,2,1)
    def check(name,value):
        records.append({'test':name,'passed':bool(value)});assert value,name
    def step(t,fn):steps.append((t,fn))
    def move(idx):
        x,y=positions[idx];pawn.set_actor_location(u.Vector(x,y,114),False,False)
    def confirm():hud.call_method('Confirm')
    def interact():hud.call_method('Interact')
    def visible():return ui.get_editor_property('PopupCard').is_visible()==p('Popup')
    def count_ui(n):return str(ui.get_editor_property('JournalCount').get_text())==f'{n} / 5'
    step(.5,lambda:check('fresh journal',p('Count')==0 and p('Popup') and count_ui(0) and visible()))
    step(.1,confirm)
    for number,idx in enumerate(order,1):
        step(.1,lambda idx=idx:move(idx))
        step(.5,lambda idx=idx:check('nearest clue '+str(idx),p('Nearby')==idx))
        step(.1,interact)
        step(.3,lambda n=number:check('equal count and journal '+str(n),p('Count')==n and count_ui(n) and p('Popup') and visible()))
        step(.1,lambda n=number:check('paw stamps '+str(n),all(abs(ui.get_editor_property('PawFound'+str(i)).get_render_opacity()-(1 if i<n else 0))<.01 for i in range(5))))
        step(.1,lambda:check('no hierarchy wording','보조' not in p('Title') and '핵심' not in p('Message')))
        step(.1,confirm)
        if number<5:
            step(.1,lambda n=number:check('no early deduction '+str(n),not p('Deduced')))
            step(.1,interact);step(.1,lambda n=number:check('repeat preserves count '+str(n),p('Count')==n));step(.1,confirm)
            if number in (3,4):
                step(.1,lambda:move(4));step(.5,interact)
                step(.1,lambda n=number:check('door locked '+str(n),not p('DoorOpen') and p('Popup')));step(.1,confirm)
        else:
            step(.2,lambda:check('deduction at five',p('Deduced') and p('Popup') and str(ui.get_editor_property('PopupMessage').get_text())==p('Message')))
    step(.1,lambda:check('one count only',p('ExtraCount')==0 and p('Count')==5))
    if scenario!='core_first':
        step(.1,confirm);step(.1,lambda:move(4));step(.5,interact)
        step(1.6,lambda:check('door animation completes',p('DoorOpen') and abs(p('DoorAngle')-90)<.1))
        step(.4,lambda:check('exit waits for crossing',not p('Complete') and not p('Popup') and visible()))
    def finish(error=None):
        u.unregister_slate_post_tick_callback(handle)
        Path('D:/Multimodal/Saved/ClientHome/cozy-'+scenario+'-test.json').write_text(json.dumps({'checks':records,'error':error},ensure_ascii=False,indent=2),encoding='utf-8')
        u.log('COZY_TEST_'+scenario+': '+str(error or 'PASS')+' '+str(len(records)))
    def tick(dt):
        nonlocal index,elapsed
        try:
            elapsed+=dt
            if elapsed<steps[index][0]:return
            elapsed=0.;steps[index][1]();index+=1
            if index==len(steps):finish()
        except Exception as exc:finish(str(exc))
    handle=u.register_slate_post_tick_callback(tick)
if __name__=='__main__':run()
