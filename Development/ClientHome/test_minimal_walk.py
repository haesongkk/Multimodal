"""Drive CharacterMovement through the clue route, without teleporting.
Run in fresh PIE. This tests collision/navigation, not keyboard hardware events.
"""
import unreal as u
import json,time,math
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert w and 'Lvl_ClientHome_Minimal' in w.get_name()
pawn=u.GameplayStatics.get_player_pawn(w,0)
hud=u.GameplayStatics.get_player_controller(w,0).get_hud()
assert hud.get_editor_property('Count')==0
if hud.get_editor_property('Popup'): hud.call_method('Confirm')
route=[('pot',650,300,1),('around TV',400,350,None),('clear aisle',400,20,None),
       ('fur',650,20,2),('return aisle',400,20,None),('window approach',400,350,None),('window',870,350,3),
       ('central passage',600,100,None),('door approach',370,0,None),('exit',370,-330,4)]
index=0; elapsed=0.; settling=0.; records=[]; positions=[]
def finish(error=None):
    u.unregister_slate_post_tick_callback(handle)
    pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
    result={'passed':error is None,'error':error,'waypoints':records,'final_location':str(pawn.get_actor_location()),'positions':positions,'scope':'CharacterMovement input with real collisions; no teleport, not a hardware keyboard test'}
    Path('D:/Multimodal/Saved/ClientHome/minimal-walk-test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    u.log('MINIMAL_WALK_RESULT: '+str(error or 'PASS'))
def tick(dt):
    global index,elapsed,settling
    try:
        elapsed+=dt
        name,x,y,near=route[index]; pos=pawn.get_actor_location()
        if len(positions)==0 or math.hypot(pos.x-positions[-1][0],pos.y-positions[-1][1])>70:
            positions.append([round(pos.x,1),round(pos.y,1),round(pos.z,1)])
        dx=x-pos.x;dy=y-pos.y;distance=math.hypot(dx,dy)
        if distance<25:
            pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
            settling+=dt
            if settling<.5:return
            actual=hud.get_editor_property('Nearby')
            assert near is None or actual==near,(name,'nearest',actual,near)
            records.append({'name':name,'position':[pos.x,pos.y,pos.z],'nearby':actual,'seconds':elapsed})
            index+=1;elapsed=0.;settling=0.
            if index==len(route):finish()
            return
        assert elapsed<15,(name,'blocked',str(pos))
        pawn.add_movement_input(u.Vector(dx/distance,dy/distance,0),min(1.,distance/max(270*dt,1)))
    except Exception as e:finish(str(e))
handle=u.register_slate_post_tick_callback(tick)
