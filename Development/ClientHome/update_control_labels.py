"""Keep dynamic bottom hints on one line with a stable full-width text slot."""
import unreal as u,json
from editor_toolset.toolsets.object import ObjectTools as O
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
bp=u.load_asset('/Game/ClientHome_Haeso/UI/WBP_CH_Popup')
tool=u.get_default_object(u.UMGToolSet)
ws={str(i.widget_name):i.widget for i in tool.call_method('GetWidgets',(bp,)).widgets}
def write(o,data):
 O.list_properties(o);assert O.set_properties(o,json.dumps(data))
write(ws['CozyKeysText'],{'text':'WASD  이동하기     E  조사하기'})
_BlueprintCache.invalidate(bp)
assert tool.call_method('CompileWidgetBlueprint',(bp,))
B.compile_blueprint(bp,True)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp,False)
u.log('KEY_LABELS_UPDATED')
