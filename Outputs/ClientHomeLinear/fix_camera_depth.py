import unreal as u,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=u.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Linear')
count=0
for n in B.find_nodes(B.get_graph(bp,'EventGraph')):
 for p in n.list_all_pins():
  if p.get_pin_value() in ['280.0','340.0','280.000000','340.000000']:
   assert p.set_pin_value('490.0');count+=1
B.compile_blueprint(bp)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp)
(_linear_root/'camera_fixed_depth_result.json').write_text(json.dumps({'fixed_y':-510,'pitch':-25,'height':520,'changed_pins':count,'status':str(bp.get_editor_property('status'))},indent=2))
