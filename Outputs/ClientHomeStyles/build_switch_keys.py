import unreal as u,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
e=u.get_editor_subsystem(u.EditorAssetSubsystem)
bp=u.load_asset('/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Framework/BP_CH_Player_StylePreview');g=B.get_graph(bp,'EventGraph')
for n in list(B.find_nodes(g)):
 if str(n.get_node_title()) in ['F1','F2','F3','F4','Open Level (by Name)']:B.delete_node(n)
for i,style in enumerate(['Original','Storybook'],1):
 key=B.create_node(g,'Input|KeyboardEvents|F'+str(i),u.IntPoint(0,6250+i*250))
 call=B.create_node(g,'게임|OpenLevel(byName)',u.IntPoint(300,6250+i*250))
 assert key.find_output_pin('Pressed').try_create_connection(call.find_execute_pin())
 assert call.find_input_pin('LevelName').set_pin_value('/Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_'+style)
 call.find_input_pin('bAbsolute').set_pin_value('true')
B.compile_blueprint(bp);assert e.save_loaded_asset(bp)
for style in ['Papercraft','Kenney']:
 path='/Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_'+style
 if e.does_asset_exist(path):e.delete_asset(path)
Path('D:/Multimodal/Outputs/ClientHomeStyles/switch_keys_result.json').write_text(json.dumps({'keys':{'F1':'Original','F2':'Storybook'},'status':str(bp.get_editor_property('status'))}))
