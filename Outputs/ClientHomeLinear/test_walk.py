import unreal as u,json,time,math
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
p=u.GameplayStatics.get_player_pawn(world,0);pc=u.GameplayStatics.get_player_controller(world,0);hud=pc.get_hud()
hud.call_method('Confirm')
p.set_actor_location(u.Vector(-1730,140,115),False,True)
waypoints=[(-1530,120),(-1150,120),(-750,120),(-350,120),(100,120),(450,120),(850,120),(930,300),(1050,400),(1190,530),(1350,355)]
state={'index':0,'elapsed':0.,'last_distance':99999.,'stuck':0.,'results':[]}
def tick(dt):
 try:
  i=state['index']
  if i>=len(waypoints):
   state['complete']=True
   (_linear_root/'walk_test.json').write_text(json.dumps(state,indent=2))
   u.unregister_slate_post_tick_callback(handle);return
  x,y=waypoints[i];pos=p.get_actor_location();dx=x-pos.x;dy=y-pos.y;dist=math.hypot(dx,dy)
  state['elapsed']+=dt
  if dist<25:
   state['results'].append({'target':[x,y],'actual':[pos.x,pos.y,pos.z],'seconds':state['elapsed'],'passed':True})
   state['index']+=1;state['elapsed']=0.;state['stuck']=0.;state['last_distance']=99999.
  else:
   p.add_movement_input(u.Vector(dx/dist,dy/dist,0),1.0,False)
   if abs(state['last_distance']-dist)<.5:state['stuck']+=dt
   else:state['stuck']=0.
   state['last_distance']=dist
   if state['elapsed']>12 or state['stuck']>3:
    state['results'].append({'target':[x,y],'actual':[pos.x,pos.y,pos.z],'distance':dist,'passed':False})
    state['complete']=False
    (_linear_root/'walk_test.json').write_text(json.dumps(state,indent=2))
    u.unregister_slate_post_tick_callback(handle);return
  (_linear_root/'walk_progress.json').write_text(json.dumps(state,indent=2))
 except Exception as e:
  (_linear_root/'walk_error.txt').write_text(str(e));u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
