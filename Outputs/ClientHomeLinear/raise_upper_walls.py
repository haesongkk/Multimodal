import unreal as u,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=u.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Linear')
for h in u.get_engine_subsystem(u.SubobjectDataSubsystem).k2_gather_subobject_data_for_blueprint(bp):
 o=u.SubobjectDataBlueprintFunctionLibrary.get_object(u.SubobjectDataBlueprintFunctionLibrary.get_data(h))
 if isinstance(o,u.CameraComponent):
  o.set_editor_property('relative_rotation',u.Rotator(pitch=-25,yaw=90,roll=0));o.set_editor_property('field_of_view',60.)
B.compile_blueprint(bp);eas=u.get_editor_subsystem(u.EditorAssetSubsystem);assert eas.save_loaded_asset(bp)
actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()};report=[]
for name in ['RearRight','RearLeftA','RearLeftB','LivingEnd','EntryEndBack','EntryEndFront']:
 a=actors['CH_Linear_'+name];c=a.get_component_by_class(u.StaticMeshComponent);mesh=c.static_mesh;dm=u.DynamicMesh();lod=u.GeometryScriptMeshReadLOD()
 u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,u.GeometryScriptCopyMeshFromAssetOptions(),lod)
 _,positions,_=u.GeometryScript_MeshQueries.get_all_vertex_positions(dm,False);vertices=positions.convert_vector_list_to_array();top=max(v.z for v in vertices);changed=0
 if top<479:
  for i,v in enumerate(vertices):
   if v.z>280:
    v.z=280+(v.z-280)*(480-280)/(top-280);u.GeometryScript_MeshEdits.set_vertex_position(dm,i,v,False);changed+=1
  _,indices,_,_=u.GeometryScript_AssetUtils.get_section_material_list_from_static_mesh(mesh,lod)
  mats=[c.get_material(i) for i in indices]
  u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,u.GeometryScriptCopyMeshToAssetOptions(replace_materials=True,new_materials=mats),u.GeometryScriptMeshWriteLOD())
  c.set_editor_property('override_materials',mats);assert eas.save_loaded_asset(mesh)
 report.append({'mesh':name,'old_top':top,'new_top':480,'vertices_changed':changed})
for label,a in actors.items():
 if label.startswith('CH_Linear_Crown'):
  p=a.get_actor_location();p.z=126.026;a.set_actor_location(p,False,True)
 if label in ['CH_SmallBath_BackUpper','CH_SmallBath_LeftUpper','CH_SmallBath_RightBackUpper']:
  p=a.get_actor_location();p.z=(181+480)/2;a.set_actor_location(p,False,True);s=a.get_actor_scale3d();s.z=2.99;a.set_actor_scale3d(s)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'raised_walls_result.json').write_text(json.dumps(report,indent=2))
