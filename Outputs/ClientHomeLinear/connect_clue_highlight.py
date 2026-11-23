import unreal as u,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=u.load_asset('/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_HUD_Linear');g=B.get_graph(bp,'DisableClueHighlight');t=json.loads((_linear_root/'highlight_node_pins.json').read_text())
def node(key,x,y=0):return B.create_node(g,t[key]['type'],u.IntPoint(x,y))
def link(a,b):assert a.try_create_connection(b)
entry=B.find_nodes(g,node_class=u.K2Node_FunctionEntry.static_class())[0]
for n in B.find_nodes(g):
 if n!=entry:B.delete_node(n)
query=node('GetAllActorsWithTag',200);link(entry.find_then_pin(),query.find_execute_pin());link(entry.find_output_pin('ClueTag'),query.find_input_pin('Tag'))
loop=node('ForEachLoop',450);link(query.find_then_pin(),loop.find_input_pin('Exec'));link(query.find_output_pin('OutActors'),loop.find_input_pin('Array'))
comp=node('GetComponentByClass',650,200);link(loop.find_output_pin('Array Element'),comp.find_self_pin());assert comp.find_input_pin('ComponentClass').set_pin_value('/Script/Engine.PrimitiveComponent')
cast=node('CastToPrimitiveComponent',850);link(loop.find_output_pin('LoopBody'),cast.find_execute_pin());link(comp.find_result_pin(),cast.find_input_pin('Object'))
setdepth=node('SetRenderCustomDepth',1100);link(cast.find_then_pin(),setdepth.find_execute_pin());link(cast.find_output_pin(t['CastToPrimitiveComponent']['out'][2]),setdepth.find_self_pin());setdepth.find_input_pin('bValue').set_pin_value('false')
B.compile_blueprint(bp)
graph=B.get_graph(bp,'Interact');calltype=B.find_node_types(graph,'DisableClueHighlight')[0];hooked=[]
for n in B.find_nodes(graph):
 if n.get_class().get_name()!='K2Node_VariableSet':continue
 title=str(n.get_node_title()).replace(' ','')
 for key in ['Pot','Fur','Window','Snack','Pawprints']:
  if key+'Seen' in title:
   out=n.find_then_pin();dest=list(out.list_connected_pins());out.break_pin_links();call=B.create_node(graph,calltype,u.IntPoint(0,2500+len(hooked)*200));call.find_input_pin('ClueTag').set_pin_value('CH_Highlight_'+key);link(out,call.find_execute_pin())
   for p in dest:link(call.find_then_pin(),p)
   hooked.append(key)
assert len(hooked)==5,hooked
B.compile_blueprint(bp);assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp)
gm=u.load_asset('/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Linear');u.get_default_object(gm.generated_class()).set_editor_property('hud_class',bp.generated_class());B.compile_blueprint(gm);assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(gm)
(_linear_root/'highlight_runtime_result.json').write_text(json.dumps({'hooked':hooked,'hud_status':str(bp.get_editor_property('status')),'game_mode_status':str(gm.get_editor_property('status'))},indent=2))
