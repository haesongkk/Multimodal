import unreal as u,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=u.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Linear')
s=u.get_engine_subsystem(u.SubobjectDataSubsystem)
for h in s.k2_gather_subobject_data_for_blueprint(bp):
 o=u.SubobjectDataBlueprintFunctionLibrary.get_object(u.SubobjectDataBlueprintFunctionLibrary.get_data(h))
 if isinstance(o,u.CameraComponent):o.set_editor_property('relative_rotation',u.Rotator(pitch=-15,yaw=90,roll=0))
count=0
for n in B.find_nodes(B.get_graph(bp,'EventGraph')):
 for p in n.list_all_pins():
  if p.get_pin_value() in ['720.0','720.000000']:
   assert p.set_pin_value('350.0');count+=1
B.compile_blueprint(bp)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(bp)
(_linear_root/'camera_side_result.json').write_text(json.dumps({'pitch':-15,'height':350,'changed_pins':count,'status':str(bp.get_editor_property('status'))},indent=2))
