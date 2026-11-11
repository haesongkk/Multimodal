import unreal as u,math
from editor_toolset.toolsets.blueprint import BlueprintTools as B
hud=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_HUD_Minimal')
g=B.get_graph(hud,'EventGraph');ed=u.BlueprintGraphEditor.get_graph_editor(g);count=0
for info in B.get_node_infos(ed.list_all_nodes()):
 for pin in info.input_pins:
  if pin.name=='WorldDirection' and not pin.connected_pins:
   # Rotate the previous diagonal basis 45 degrees; axis-aligned reruns are unchanged.
   x,y,z=[float(v) for v in pin.value.split(',')]
   if abs(x)>.5 and abs(y)>.5:
    B.set_pin_value(pin.pin_id,f'{round((x-y)/math.sqrt(2))},{round((x+y)/math.sqrt(2))},{z}')
   count+=1
assert count>=4 and count%4==0,count
B.compile_blueprint(hud,True)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(hud,False)
u.log('LEFT_CAMERA_INPUT_SAVED')
