"""Remove the dialogue eyebrow and use a right-aligned Space confirmation hint."""
import unreal as u,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
from editor_toolset.toolsets.object import ObjectTools as O
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);bp=u.load_asset('/Game/ClientHome_Haeso/UI/WBP_CH_Popup');hud=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_HUD_Minimal')
lang=u.InternationalizationLibrary.get_current_language()
try:
 u.InternationalizationLibrary.set_current_language('en',False)
 tool=u.get_default_object(u.UMGToolSet);ws={str(i.widget_name):i.widget for i in tool.call_method('GetWidgets',(bp,)).widgets}
 def write(o,data):
  O.list_properties(o);assert O.set_properties(o,json.dumps(data))
 write(ws['PopupEyebrow'],{'text':'','visibility':'Collapsed'})
 write(ws['PopupHint'],{'text':'[Space]','justification':'Right','autoWrapText':False})
 write(ws['PopupHint'].get_editor_property('slot'),{'horizontalAlignment':'HAlign_Fill'})
 _BlueprintCache.invalidate(bp)
 g=B.get_graph(bp,'Present');code=Path('D:/Multimodal/Development/ClientHome/WBP_CH_Popup.dsl').read_text(encoding='utf-8');B.write_graph_dsl(g,code)
 assert tool.call_method('CompileWidgetBlueprint',(bp,));B.compile_blueprint(bp,True);assert assets.save_loaded_asset(bp,False)
 g=B.get_graph(hud,'EventGraph');editor=u.BlueprintGraphEditor.get_graph_editor(g);changed=0
 for info in B.get_node_infos(editor.list_all_nodes()):
  for pin in info.input_pins:
   if pin.name=='Key' and 'Enter' in pin.value:
    u.log('CONFIRM_KEY '+pin.value);B.set_pin_value(pin.pin_id,pin.value.replace('Enter','SpaceBar'));changed+=1
 assert changed>0,changed
 B.compile_blueprint(hud,True);assert assets.save_loaded_asset(hud,False)
 u.log('SPACE_POPUP_SAVED '+str(changed))
finally:u.InternationalizationLibrary.set_current_language(lang,False)
