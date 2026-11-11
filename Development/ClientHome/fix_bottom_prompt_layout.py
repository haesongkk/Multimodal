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
for name in ['JournalPrompt','CozyKeysText']:
 w=ws[name]
 write(w,{'autoWrapText':False,'wrapTextAt':0})
 write(w.get_editor_property('slot'),{'horizontalAlignment':'HAlign_Fill','verticalAlignment':'VAlign_Center'})
write(ws['JournalPrompt'],{'justification':'Center'})
write(ws['CozyKeysText'],{'justification':'Center'})
write(ws['CozyKeysText'].get_editor_property('slot'),{'padding':{'left':18,'top':7,'right':18,'bottom':7}})
_BlueprintCache.invalidate(bp)
assert tool.call_method('CompileWidgetBlueprint',(bp,))
B.compile_blueprint(bp,True)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp,False)
u.log('BOTTOM_PROMPT_SINGLE_LINE_SAVED')
