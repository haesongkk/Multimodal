"""Preserve bathroom materials while softly revealing the player through occluding surfaces."""
import unreal as u
from pathlib import Path
ROOT='/Game/ClientHome_Haeso';DEST=ROOT+'/Materials/BathroomFade'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);M=u.MaterialEditingLibrary
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
mpc=u.load_asset(DEST+'/MPC_CH_Occlusion')
if not mpc:
 mpc=u.AssetToolsHelpers.get_asset_tools().create_asset('MPC_CH_Occlusion',DEST,u.MaterialParameterCollection,u.MaterialParameterCollectionFactoryNew())
 param=u.CollectionVectorParameter();param.set_editor_property('parameter_name','PlayerPosition');param.set_editor_property('default_value',u.LinearColor(0,0,0,0))
 mpc.set_editor_property('vector_parameters',[param]);assert assets.save_loaded_asset(mpc,False)
cache={}
def faded(original):
 if original.get_name().startswith('Reveal_'):original=u.load_asset('/Game/StylizedKitchen/Materials/'+original.get_name()[7:])
 if original.get_name().startswith('Fade_'):original=u.load_asset('/Game/StylizedKitchen/Materials/'+original.get_name()[5:])
 key=original.get_path_name()
 if key in cache:return cache[key]
 if original.get_path_name().startswith(DEST):return original
 dst=DEST+'/Reveal_'+original.get_name()
 result=u.load_asset(dst)
 if not result:
  if isinstance(original,u.MaterialInstance):result=assets.duplicate_asset(key,dst)
  else:result=u.AssetToolsHelpers.get_asset_tools().create_asset('Reveal_'+original.get_name(),DEST,u.Material,u.MaterialFactoryNew())
 cache[key]=result
 if isinstance(original,u.MaterialInstance):
  M.set_material_instance_parent(result,faded(original.get_editor_property('parent')))
  M.update_material_instance(result)
 else:
  # A fresh material avoids legacy imported opacity optimization flags.
  M.delete_all_material_expressions(result)
  expressions=list(M.get_material_expressions(original));copies={}
  for expression in expressions:
   copies[expression.get_path_name()]=M.duplicate_material_expression(result,None,expression)
  for expression in expressions:
   inputs=M.get_inputs_for_material_expression(original,expression)
   names=M.get_material_expression_input_names(expression)
   for index,input_node in enumerate(inputs):
    if not input_node:continue
    output=M.get_input_node_output_name_for_material_expression(expression,input_node) or ''
    # This source packs RGB + alpha from the same vector; the query returns only its first output.
    if original.get_name()=='MM_Walls_Tile_Master' and isinstance(expression,u.MaterialExpressionAppendVector) and str(names[index])=='B':output='A'
    assert M.connect_material_expressions(copies[input_node.get_path_name()],output,copies[expression.get_path_name()],str(names[index]))
  for pname in ['MP_BASE_COLOR','MP_METALLIC','MP_SPECULAR','MP_ROUGHNESS','MP_EMISSIVE_COLOR','MP_NORMAL','MP_AMBIENT_OCCLUSION','MP_WORLD_POSITION_OFFSET']:
   prop=getattr(u.MaterialProperty,pname);input_node=M.get_material_property_input_node(original,prop)
   if input_node:M.connect_material_property(copies[input_node.get_path_name()],M.get_material_property_input_node_output_name(original,prop),prop)
  for prop in ['two_sided','tangent_space_normal']:
   result.set_editor_property(prop,original.get_editor_property(prop))
  for expression in M.get_material_expressions(result):
   if expression.get_editor_property('desc').startswith('CH_Occlusion'):M.delete_material_expression(result,expression)
  def node(cls,x,y):
   n=M.create_material_expression(result,cls,x,y);n.set_editor_property('desc','CH_Occlusion');return n
  pos=node(u.MaterialExpressionWorldPosition,-650,500)
  camera=node(u.MaterialExpressionCameraPositionWS,-650,650)
  player=node(u.MaterialExpressionCollectionParameter,-650,800);player.set_editor_property('collection',mpc);player.set_editor_property('parameter_name','PlayerPosition')
  custom=node(u.MaterialExpressionCustom,-350,600);custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
  inputs=[]
  for name in ['World','Camera','Player']:
   i=u.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
  custom.set_editor_property('inputs',inputs)
  custom.set_editor_property('code',"""float3 ray = Player.xyz - Camera;
float rayLength = max(length(ray), 1.0);
float3 dir = ray / rayLength;
float along = dot(World - Camera, dir);
float3 offset = World - (Camera + dir * along);
// Widen around the capsule and feather the boundary as the player moves.
float distanceToSight = length(offset);
float reveal = 1.0 - smoothstep(110.0, 200.0, distanceToSight);
float inFront = smoothstep(0.0, 35.0, rayLength - along);
return lerp(1.0, 0.18, reveal * inFront * saturate(Player.a));""")
  assert M.connect_material_expressions(pos,'',custom,'World')
  assert M.connect_material_expressions(camera,'',custom,'Camera')
  assert M.connect_material_expressions(player,'',custom,'Player')
  dither=node(u.MaterialExpressionMaterialFunctionCall,-100,600)
  dither.set_editor_property('material_function',u.load_asset('/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA'))
  u.log('DITHER_INPUTS '+str(M.get_material_expression_input_names(dither)))
  assert M.connect_material_expressions(custom,'',dither,'Alpha Threshold')
  assert M.connect_material_property(dither,'',u.MaterialProperty.MP_OPACITY_MASK)
  result.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED)
  errors=M.recompile_material(result);assert not errors,(result.get_name(),errors)
 assert assets.save_loaded_asset(result,False)
 return result
count=0
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 name=a.get_actor_label()
 if not name.startswith('CH_SmallBath_'):continue
 if not any(s in name for s in ['Tile','Upper','Trim','Lintel','Cutaway','Door']):continue
 if name=='CH_SmallBath_TileFloor':continue
 c=a.get_component_by_class(u.StaticMeshComponent)
 if not c:continue
 for i,mat in enumerate(c.get_materials()):
  if mat:c.set_material(i,faded(mat))
 count+=1
assert count>=10,count
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('BATHROOM_OCCLUSION_MATERIALS_SAVED '+str(count))
