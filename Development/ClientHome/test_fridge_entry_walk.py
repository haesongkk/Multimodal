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
assert hud.get_editor_property('Count')==5 and hud.get_editor_property('DoorOpen')
if hud.get_editor_property('Popup'): hud.call_method('Confirm')
route=[('through relocated door',-885,-238,None)]
movement=pawn.get_component_by_class(u.CharacterMovementComponent)
original_speed=movement.max_walk_speed
movement.max_walk_speed=90
index=0; elapsed=0.; settling=0.; records=[]; positions=[]
def finish(error=None):
    u.unregister_slate_post_tick_callback(handle)
    movement.max_walk_speed=original_speed
    pawn.get_component_by_class(u.CharacterMovementComponent).stop_movement_immediately()
    result={'passed':error is None,'error':error,'waypoints':records,'final_location':str(pawn.get_actor_location()),'positions':positions,'scope':'CharacterMovement input with real collisions; no teleport, not a hardware keyboard test'}
    Path('D:/Multimodal/Saved/ClientHome/fridge-entry-walk-test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    u.log('FRIDGE_ENTRY_WALK_RESULT: '+str(error or 'PASS'))
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
            if index==len(route):
                assert hud.get_editor_property('Complete'),'exit did not complete'
                assert pos.z>80,'landing has no support'
                finish()
            return
        assert elapsed<30,(name,'blocked',str(pos))
        pawn.add_movement_input(u.Vector(dx/distance,dy/distance,0),min(1.,distance/max(90*dt,1)))
    except Exception as e:finish(str(e))
handle=u.register_slate_post_tick_callback(tick)
