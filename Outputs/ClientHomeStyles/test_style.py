import unreal as u,json,time
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
p=u.GameplayStatics.get_player_pawn(w,0);h=u.GameplayStatics.get_player_controller(w,0).get_hud()
style='Storybook' if 'Storybook' in w.get_name() else 'Kenney' if 'Kenney' in w.get_name() else 'Papercraft'
targets=[('Study',-560,210,None),('Kitchen',-1230,80,None),('Bathroom',540,350,None),('Living',1160,80,None),('Fur',-240,350,2),('Pawprints',530,500,6),('Snack',-1058,150,5),('Pot',1169,380,1),('Window',1280,240,3)]
s={'i':0,'phase':0,'time':time.monotonic(),'results':[]}
def flags(tag):return [c.get_editor_property('render_custom_depth') for a in u.GameplayStatics.get_all_actors_with_tag(w,'CH_Highlight_'+tag) for c in a.get_components_by_class(u.PrimitiveComponent)]
def tick(dt):
 if time.monotonic()-s['time']<1.5:return
 s['time']=time.monotonic()
 if s['i']>=len(targets):
  Path('D:/Multimodal/Outputs/ClientHomeStyles/'+style+'_playtest.json').write_text(json.dumps(s['results'],indent=2));u.unregister_slate_post_tick_callback(handle);return
 name,x,y,expected=targets[s['i']]
 if s['phase']==0:
  if h.get_editor_property('Popup'):h.call_method('Confirm')
  p.set_actor_location(u.Vector(x,y,110),False,True);s['phase']=1
 else:
  if expected is None:u.SystemLibrary.execute_console_command(w,'HighResShot 1 filename=D:/Multimodal/Outputs/ClientHomeStyles/'+style+'_'+name+'.png')
  else:
   before=flags(name);count=h.get_editor_property('Count');nearby=h.get_editor_property('Nearby');h.call_method('Interact');after=flags(name)
   s['results'].append({'clue':name,'nearby':nearby,'expected':expected,'passed':nearby==expected and all(before) and not any(after) and h.get_editor_property('Count')==count+1})
  s['phase']=0;s['i']+=1
handle=u.register_slate_post_tick_callback(tick)
