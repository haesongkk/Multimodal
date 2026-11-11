import unreal as u,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();p=u.GameplayStatics.get_player_pawn(w,0);h=u.GameplayStatics.get_player_controller(w,0).get_hud();ui=h.get_editor_property('PopupUI')
steps=[];idx=0;elapsed=0;results=[]
def step(fn):steps.append(fn)
def move(x,y):p.set_actor_location(u.Vector(x,y,114),False,False)
def confirm():
 if h.get_editor_property('Popup'):h.call_method('Confirm')
def check(text):
 actual=str(ui.get_editor_property('JournalPrompt').get_text());assert actual==text,actual;results.append(actual)
step(confirm);step(lambda:move(0,0));step(lambda:check('코코가 남긴 흔적을 찾아보자.'))
for x,y in [(740,455),(35,-205),(870,268),(-230,-100),(155,285)]:
 step(lambda x=x,y=y:move(x,y));step(lambda:h.call_method('Interact'));step(confirm)
step(confirm);step(lambda:move(0,0));step(lambda:check('코코의 길을 찾았어! 현관으로 나가 보자.'))
step(lambda:move(-730,-238));step(lambda:check('[E] 현관문 열고 나가기'));step(lambda:move(830,-400))
def tick(dt):
 global idx,elapsed
 try:
  elapsed+=dt
  if elapsed<.5:return
  elapsed=0;steps[idx]();idx+=1
  if idx==len(steps):
   u.unregister_slate_post_tick_callback(handle)
   Path('D:/Multimodal/Saved/ClientHome/completed-hint-test.json').write_text(json.dumps(results,ensure_ascii=False),encoding='utf-8');u.log('COMPLETED_HINT_TEST_PASS')
 except Exception as ex:
  u.unregister_slate_post_tick_callback(handle);u.log_error('COMPLETED_HINT_TEST_FAILED '+str(ex))
handle=u.register_slate_post_tick_callback(tick)
