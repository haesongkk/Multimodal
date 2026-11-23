import unreal as u,json
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();pc=u.GameplayStatics.get_player_controller(w,0);p=u.GameplayStatics.get_player_pawn(w,0);hud=pc.get_hud()
targets=[('Snack',-1150,120,5),('Pawprints',-195,200,6),('Fur',235,220,2),('Pot',1190,530,1),('Window',1368,350,3),('Door',-1740,140,4)]
state={'index':0,'phase':0,'elapsed':0.,'results':[]}
def prop(n):return hud.get_editor_property(n)
def tick(dt):
 try:
  state['elapsed']+=dt
  if state['elapsed']<.8:return
  state['elapsed']=0
  i=state['index']
  if i>=len(targets):
   state['count']=prop('Count');state['deduced']=prop('Deduced');state['door_open']=prop('DoorOpen');state['complete']=prop('Complete')
   (_linear_root/'clue_test.json').write_text(json.dumps(state,indent=2))
   u.unregister_slate_post_tick_callback(handle);return
  name,x,y,expected=targets[i]
  if state['phase']==0:
   if prop('Popup'):hud.call_method('Confirm')
   p.set_actor_location(u.Vector(x,y,115),False,True);state['phase']=1
  elif state['phase']==1:
   nearby=prop('Nearby');hud.call_method('Interact')
   state['results'].append({'clue':name,'expected':expected,'nearby':nearby,'count':prop('Count'),'passed':nearby==expected})
   state['phase']=2
  else:
   if prop('Popup'):hud.call_method('Confirm')
   if prop('Popup'):hud.call_method('Confirm')
   state['index']+=1;state['phase']=0
 except Exception as e:
  (_linear_root/'clue_error.txt').write_text(str(e));u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
