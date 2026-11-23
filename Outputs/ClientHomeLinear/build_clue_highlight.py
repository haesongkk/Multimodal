import unreal as u,json
out=_linear_root
path='/Game/Multimodal/08_Effects/Materials/ClientHome/M_CH_ClueOutline'
eas=u.get_editor_subsystem(u.EditorAssetSubsystem);mat=u.load_asset(path) if eas.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset('M_CH_ClueOutline','/Game/Multimodal/08_Effects/Materials/ClientHome',u.Material,u.MaterialFactoryNew())
mat.set_editor_property('material_domain',u.MaterialDomain.MD_POST_PROCESS);mat.set_editor_property('blendable_location',u.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING)
ml=u.MaterialEditingLibrary;ml.delete_all_material_expressions(mat)
custom=ml.create_material_expression(mat,u.MaterialExpressionCustom,400,0)
custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
inputs=['Scene','Texel','Clock','StencilSupport','DepthSupport','SceneDepthSupport']
custom_inputs=[]
for name in inputs:
 ci=u.CustomInput();ci.set_editor_property('input_name',name);custom_inputs.append(ci)
custom.set_editor_property('inputs',custom_inputs)
custom.set_editor_property('code','''
float2 uv=GetDefaultSceneTextureUV(Parameters,25);
float center=abs(StencilSupport.r-201.0)<0.5 ? 1.0:0.0;
center *= DepthSupport.r <= SceneDepthSupport.r+3.0 ? 1.0:0.0;
float edge=0.0;
float2 offsets[8]={float2(1,0),float2(-1,0),float2(0,1),float2(0,-1),float2(0.707,0.707),float2(-0.707,0.707),float2(0.707,-0.707),float2(-0.707,-0.707)};
[unroll] for(int i=0;i<8;i++){
 float2 p=uv+offsets[i]*Texel*2.0;
 float st=SceneTextureLookup(p,25,false).r;
 float cd=SceneTextureLookup(p,13,false).r;
 float sd=SceneTextureLookup(p,1,false).r;
 float hit=(abs(st-201.0)<0.5 && cd<=sd+3.0)?1.0:0.0;
 edge=max(edge,hit);

}
float pulse=0.72+0.18*sin(Clock*2.0943951);
float mask=saturate(edge-center)+center*0.12;
return lerp(Scene.rgb,float3(1.0,0.86,0.61),saturate(mask*pulse));
''')
for idx,slot,typ in [(0,'Scene',u.SceneTextureId.PPI_POST_PROCESS_INPUT0),(1,'StencilSupport',u.SceneTextureId.PPI_CUSTOM_STENCIL),(2,'DepthSupport',u.SceneTextureId.PPI_CUSTOM_DEPTH),(3,'SceneDepthSupport',u.SceneTextureId.PPI_SCENE_DEPTH)]:
 n=ml.create_material_expression(mat,u.MaterialExpressionSceneTexture,-400,idx*200);n.set_editor_property('scene_texture_id',typ);ml.connect_material_expressions(n,'Color',custom,slot)
 if slot=='StencilSupport':ml.connect_material_expressions(n,'InvSize',custom,'Texel')
time=ml.create_material_expression(mat,u.MaterialExpressionTime,-400,850);ml.connect_material_expressions(time,'',custom,'Clock');ml.connect_material_property(custom,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
ml.recompile_material(mat);assert eas.save_loaded_asset(mat)
aas=u.get_editor_subsystem(u.EditorActorSubsystem);actors=aas.get_all_level_actors();volume=next((a for a in actors if a.get_actor_label()=='CH_ClueHighlight_PostProcess'),None) or aas.spawn_actor_from_class(u.PostProcessVolume,u.Vector())
volume.set_actor_label('CH_ClueHighlight_PostProcess');volume.set_folder_path('ClientHome/Linear/Effects');volume.set_editor_property('unbound',True);volume.set_editor_property('priority',100.)
settings=volume.get_editor_property('settings');settings.set_editor_property('weighted_blendables',u.WeightedBlendables(array=[u.WeightedBlendable(weight=1.,object=mat)]));volume.set_editor_property('settings',settings)
report=[]
for a in actors:
 if a.get_editor_property('hidden'):continue
 label=a.get_actor_label();tags=[str(t) for t in a.tags];group=None
 for key in ['Pot','Fur','Window','Snack','Pawprints']:
  if 'Home_'+key in tags:group=key
 if label.startswith('CH_Minimal_Fur'):group='Fur'
 if label.startswith('CH_Minimal_Pawprint'):group='Pawprints'
 if label.startswith('CH_Minimal_Snack'):group='Snack'
 if not group:continue
 tags.append('CH_Highlight_'+group);a.tags=list(dict.fromkeys(tags))
 for c in a.get_components_by_class(u.PrimitiveComponent):c.set_render_custom_depth(True);c.set_custom_depth_stencil_value(201)
 report.append({'label':label,'group':group})
u.SystemLibrary.execute_console_command(u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world(),'r.CustomDepth 3')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(out/'highlight_actors.json').write_text(json.dumps(report,indent=2))
