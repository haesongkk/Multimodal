import unreal as u,json
aas=u.get_editor_subsystem(u.EditorActorSubsystem);eas=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors={a.get_actor_label():a for a in aas.get_all_level_actors()}
floor=actors['House_Floor'];rear=actors['CH_Minimal_Cutaway_House_Walls_SM'];right=actors['CH_RightWall_House_Walls_SM']
recipes=[('FloorRight',floor,[(1,-40,False),(1,680,True)],None),('FloorLeft',floor,[(1,-40,False),(1,680,True),(0,671,True)],None),('RearRight',rear,[(1,665,False)],None),('RearLeftA',rear,[(1,665,False),(0,-374,True)],'wallpaper'),('RearLeftB',rear,[(1,665,False),(0,24,False),(0,671,True)],'wallpaper'),('LivingEnd',rear,[(0,900,False),(1,-40,False)],'wallpaper'),('EntryEndBack',right,[(1,235,False)],None),('EntryEndFront',right,[(1,-40,False),(1,70,True)],None)]
for suf,label in [('Base','CH_Minimal_Cutaway_House_Molding_SM'),('Crown','CH_Minimal_Cutaway_Crown_Molding_SM')]:
 for tail,cuts in [('Right',[(1,660,False)]),('LeftA',[(1,660,False),(0,-374,True)]),('LeftB',[(1,660,False),(0,24,False),(0,671,True)])]:recipes.append((suf+tail,actors[label],cuts,None))
report=[]
for name,source,cuts,replace in recipes:
 c=source.static_mesh_component;dm=u.DynamicMesh();lod=u.GeometryScriptMeshReadLOD()
 u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(c.static_mesh,dm,u.GeometryScriptCopyMeshFromAssetOptions(),lod)
 _,indices,_,_=u.GeometryScript_AssetUtils.get_section_material_list_from_static_mesh(c.static_mesh,lod)
 materials=[c.get_material(i) for i in indices]
 if replace:
  materials=[u.load_asset('/Game/ExternalAssets/StylizedKitchen/Materials/MI_Wallpaper_A') if i in [1,3,4] else m for i,m in zip(indices,materials)]
 # The new floor should use the original wood surface for every retained section.
 if name.startswith('Floor'):materials=[u.load_asset('/Game/ExternalAssets/StylizedKitchen/Materials/MI_Wood_Floor') for m in materials]
 u.GeometryScript_MeshTransforms.transform_mesh(dm,source.get_actor_transform())
 for axis,value,less in cuts:
  n=[0,0,0];n[axis]=1;p=[0,0,0];p[axis]=value
  u.GeometryScript_MeshBooleans.apply_mesh_plane_cut(dm,u.Transform(location=u.Vector(*p),rotation=u.MathLibrary.make_rot_from_z(u.Vector(*n))),u.GeometryScriptMeshPlaneCutOptions(fill_holes=False,flip_cut_side=not less))
 target=actors['CH_Linear_'+name];mesh=target.static_mesh_component.static_mesh
 opts=u.GeometryScriptCopyMeshToAssetOptions(replace_materials=True,new_materials=materials)
 u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,opts,u.GeometryScriptMeshWriteLOD())
 target.static_mesh_component.set_editor_property('override_materials',materials)
 if name=='LivingEnd':target.set_actor_location(u.Vector(500,0,0),False,True)
 eas.save_loaded_asset(mesh);report.append([name,list(indices),dm.get_triangle_count()])
for label in ['CH_Linear_FrontSkirting','CH_Linear_FrontBoundary']:
 a=actors[label];p=a.get_actor_location();p.x=-208;a.set_actor_location(p,False,True);s=a.get_actor_scale3d();s.x-=2.44;a.set_actor_scale3d(s)
a=actors['CH_Linear_LivingBoundary'];p=a.get_actor_location();p.x=1422;a.set_actor_location(p,False,True)
# Broad warm ceiling lights preserve the existing local practical lights.
for zone,x,intensity in [('Kitchen',-1490,1800),('Dining',-740,1100),('Study',100,1300),('Living',1110,1400)]:
 label='CH_Linear_'+zone+'_Fill'
 a=actors.get(label) or aas.spawn_actor_from_class(u.PointLight,u.Vector(x,310,300))
 a.set_actor_label(label);a.set_folder_path('ClientHome/Linear/Lighting')
 c=a.get_component_by_class(u.PointLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_intensity(intensity)
 c.set_editor_property('attenuation_radius',950.0);c.set_editor_property('source_radius',75.0)
 c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3900.0)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'refinement_report.json').write_text(json.dumps(report,indent=2))
