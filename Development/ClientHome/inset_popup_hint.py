"""Inset the popup confirmation key from the rounded fabric border."""
import unreal as u,json
from editor_toolset.toolsets.object import ObjectTools as O
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
bp=u.load_asset('/Game/ClientHome_Haeso/UI/WBP_CH_Popup');tool=u.get_default_object(u.UMGToolSet)
ws={str(i.widget_name):i.widget for i in tool.call_method('GetWidgets',(bp,)).widgets}
slot=ws['PopupHint'].get_editor_property('slot')
O.list_properties(slot)
assert O.set_properties(slot,json.dumps({'horizontalAlignment':'HAlign_Fill','padding':{'left':0,'top':0,'right':34,'bottom':12}}))
_BlueprintCache.invalidate(bp)
assert tool.call_method('CompileWidgetBlueprint',(bp,))
B.compile_blueprint(bp,True)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp,False)
u.log('POPUP_HINT_INSET_SAVED')
