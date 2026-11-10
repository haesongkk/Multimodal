"""Fresh PIE integration check for the minimally edited Fab home.
Uses actual Interact/Confirm functions, teleports between check points; no saves.
"""
import unreal as u
import json
from pathlib import Path
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world and 'Lvl_ClientHome_Minimal' in world.get_name()
controller=u.GameplayStatics.get_player_controller(world,0)
pawn=u.GameplayStatics.get_player_pawn(world,0); hud=controller.get_hud()
records=[]; steps=[]; elapsed=0; index=0
def p(n): return hud.get_editor_property(n)
def check(name,value):
    records.append({'test':name,'passed':bool(value)})
    assert value,name
def step(t,fn): steps.append((t,fn))
def move(x,y): pawn.set_actor_location(u.Vector(x,y,114),False,False)
def confirm(): hud.call_method('Confirm')
def interact(): hud.call_method('Interact')
def ui():
    w=p('PopupUI')
    return w.is_visible()==p('Popup') and str(w.get_editor_property('PopupMessage').get_text())==p('Message')
step(.4,lambda:check('fresh home session',p('Count')==0 and p('Popup') and ui()))
step(.1,confirm)
step(.1,lambda:check('intro closes',not p('Popup') and ui()))
step(.1,lambda:move(370,-330))
step(.4,interact)
step(.1,lambda:check('door locked until deduction',p('Popup') and not p('DoorOpen')))
step(.1,confirm)
step(.1,lambda:pawn.add_actor_world_offset(u.Vector(220,0,0),True,False))
step(.1,lambda:check('closed door blocks passage',pawn.get_actor_location().x<450))
for idx,label,x,y in [(1,'pot',740,320),(2,'fur',710,-20),(3,'window',870,350)]:
    step(.1,lambda x=x,y=y:move(x,y))
    step(.5,lambda idx=idx,label=label:check(label+' reachable as nearest clue',p('Nearby')==idx))
    step(.1,interact)
    step(.1,lambda idx=idx,label=label:check(label+' recorded and shown',p('Count')==idx and p('Popup') and ui()))
    step(.1,confirm)
    if idx==1:
        step(.1,interact)
        step(.1,lambda:check('repeat clue preserves count',p('Count')==1))
        step(.1,confirm)
step(.1,lambda:check('third clue gives deduction',p('Deduced') and p('Popup') and ui()))
step(.1,confirm)
step(.1,lambda:move(370,-330))
step(.4,interact)
step(.1,lambda:check('exit waits for door animation',not p('Complete')))
step(1.5,lambda:check('source door rotates 90 degrees',p('DoorOpen') and abs(p('DoorAngle')-90)<.1 and abs(p('DoorActor').get_actor_rotation().yaw+90)<.1))
step(.5,lambda:check('open doorway activates exit transition',p('Complete') and p('Popup') and ui()))
step(.1,lambda:check('exit hint shown','[Esc]' in str(p('PopupUI').get_editor_property('PopupHint').get_text())))
def finish(error=None):
    u.unregister_slate_post_tick_callback(handle)
    report={'checks':records,'error':error,'pawn_location':str(pawn.get_actor_location()),'state':{n:p(n) for n in ['Count','Nearby','DoorOpen','DoorAngle','Complete']},'scope':'Blueprint interactions and swept door collision; no full keyboard walk-through'}
    Path('D:/Multimodal/Saved/ClientHome/minimal-play-test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if error: u.log_error('MINIMAL_HOME_TEST_FAILED: '+error)
    else: u.log('MINIMAL_HOME_TEST_OK: '+str(len(records)))
def tick(dt):
    global elapsed,index
    try:
        elapsed+=dt
        if elapsed<steps[index][0]: return
        elapsed=0; steps[index][1](); index+=1
        if index==len(steps): finish()
    except Exception as e: finish(str(e))
handle=u.register_slate_post_tick_callback(tick)
