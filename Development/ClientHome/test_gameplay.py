"""PIE integration checks. Only the temporary play world is changed.
Calls the same Blueprint Interact/Confirm functions used by E/Enter.
Does not save a map or asset. Run after StartPIE.
"""
import json
from pathlib import Path
import unreal as u

world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world and 'Lvl_ClientHome_Blockout' in world.get_name()
controller=u.GameplayStatics.get_player_controller(world,0)
pawn=u.GameplayStatics.get_player_pawn(world,0)
hud=controller.get_hud()
assert hud.get_class().get_name()=='BP_CH_HUD_C'
records=[]
def check(label,condition):
    records.append({'test':label,'passed':bool(condition)})
    assert condition,label
def prop(n): return hud.get_editor_property(n)
def check_popup(label):
    widget=prop('PopupUI')
    check(label,widget.is_in_viewport() and widget.is_visible()==prop('Popup') and
          str(widget.get_editor_property('PopupTitle').get_text())==prop('Title') and
          str(widget.get_editor_property('PopupMessage').get_text())==prop('Message'))
def confirm(): hud.call_method('Confirm')
def interact(): hud.call_method('Interact')
def move(x,y): pawn.set_actor_location(u.Vector(x,y,96),False,False)
def snapshot():
    return {n:prop(n) for n in ['Count','PotSeen','FurSeen','WindowSeen','Deduced','DoorOpen','DoorAngle','Complete','Popup','Nearby']}
steps=[]
driving=False
drive_start=0.0
def start_drive():
    global driving,drive_start
    move(0,-180)
    drive_start=pawn.get_actor_location().y
    driving=True
def stop_drive():
    global driving
    driving=False
    check('character movement advances on input',pawn.get_actor_location().y > drive_start+50)
def step(delay,fn): steps.append((delay,fn))
step(.3,lambda:check('fresh session resets progress',prop('Count')==0 and not prop('Complete')))
step(.1,lambda:check_popup('intro widget matches HUD'))
step(.1,confirm)
step(.1,lambda:check('initial popup closes',not prop('Popup')))
step(.1,lambda:check_popup('confirmed widget is hidden'))
step(.1,start_drive)
step(.6,stop_drive)
step(.1,lambda:move(0,-180))
step(.1,lambda:pawn.add_actor_world_offset(u.Vector(-1000,0,0),True,False))
step(.1,lambda:check('wall collision blocks swept movement',pawn.get_actor_location().x > -590))
step(.1,lambda:move(-400,-390))
step(.1,lambda:pawn.add_actor_world_offset(u.Vector(0,-400,0),True,False))
step(.1,lambda:check('closed door physically blocks exit',pawn.get_actor_location().y > -500))
step(.3,interact)
step(.1,lambda:check('exit locked before clues',prop('Popup') and not prop('DoorOpen')))
step(.1,confirm)
step(.1,lambda:move(450,150))
step(.3,lambda:check('nearest clue wins in overlapping ranges',prop('Nearby')==2))
clue_order=globals().get('CLUE_ORDER',('pot','fur','window'))
assert sorted(clue_order)==['fur','pot','window']
clue_points={'pot':(-130,-180,'PotSeen'),'fur':(320,120,'FurSeen'),'window':(480,110,'WindowSeen')}
for count,label in enumerate(clue_order,1):
    x,y,flag=clue_points[label]
    step(.1,lambda x=x,y=y:move(x,y))
    step(.3,interact)
    step(.1,lambda label=label,count=count,flag=flag:check(label+' records exactly once',prop('Count')==count and prop(flag) and prop('Popup')))
    step(.1,lambda label=label:check_popup(label+' widget matches HUD'))
    step(.1,confirm)
    if count==1:
        step(.1,interact)
        step(.1,lambda:check('repeat clue does not increase count',prop('Count')==1))
        step(.1,confirm)
step(.1,lambda:check('third clue confirmation shows deduction',prop('Deduced') and prop('Popup')))
step(.1,lambda:check_popup('deduction widget matches HUD'))
step(.1,confirm)
step(.1,lambda:move(-400,-390))
step(.3,interact)
step(1.5,lambda:check('door rotates exactly 90 degrees',prop('DoorOpen') and abs(prop('DoorAngle')-90)<.01 and abs(prop('DoorActor').get_actor_rotation().yaw+90)<.01))
step(.1,lambda:pawn.add_actor_world_offset(u.Vector(0,-220,0),True,False))
step(.3,lambda:check('crossing doorway completes investigation',prop('Complete') and prop('Count')==3))
step(.1,lambda:check_popup('completion widget matches HUD'))
step(.1,lambda:check('completion shows exit hint','[Esc]' in str(prop('PopupUI').get_editor_property('PopupHint').get_text())))

elapsed=0.0
index=0
def finish(error=None):
    u.unregister_slate_post_tick_callback(handle)
    output=Path(u.Paths.project_saved_dir())/'ClientHome'/'gameplay-test-report.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    report={'checks':records,'state':snapshot(),'error':error,'scope':'PIE Blueprint logic, proximity and door; keyboard input is tested separately'}
    report['clue_order']=clue_order
    payload=json.dumps(report,ensure_ascii=False,indent=2)
    output.write_text(payload,encoding='utf-8')
    output.with_name('gameplay-test-'+'-'.join(clue_order)+'.json').write_text(payload,encoding='utf-8')
    if error: u.log_error('CLIENT_HOME_TEST_FAILED: '+error)
    else: u.log('CLIENT_HOME_TEST_OK: '+str(len(records))+' checks')
def tick(dt):
    global elapsed,index
    try:
        if driving: pawn.add_movement_input(u.Vector(0,1,0),1.0,False)
        elapsed+=dt
        if elapsed < steps[index][0]: return
        elapsed=0
        steps[index][1]()
        index+=1
        if index==len(steps): finish()
    except Exception as ex: finish(str(ex))
handle=u.register_slate_post_tick_callback(tick)
