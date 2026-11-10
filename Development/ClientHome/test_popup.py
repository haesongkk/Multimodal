"""PIE long-text visual probe. Changes only temporary popup text.
Inspect the play window at the desired resolution; restart PIE afterwards.
"""
import unreal as u

world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
hud=u.GameplayStatics.get_player_controller(world,0).get_hud()
popup=hud.get_editor_property('PopupUI')
message=('넘어진 화분 주변에 흙이 흩어져 있다. 작은 발자국은 바닥을 지나 열린 창문 쪽으로 이어진다. '
         '창틀에 걸린 털은 코코의 털과 같은 색이다. 의뢰인의 이야기를 떠올리며 세 단서를 함께 살펴보자. '
         '코코는 화분을 건드린 뒤 창문으로 빠져나간 것 같다. 현관문을 열고 밖으로 나가 다음 흔적을 찾아보자.')
popup.call_method('Present',('단서를 모아 추리하기',message,True,False))
