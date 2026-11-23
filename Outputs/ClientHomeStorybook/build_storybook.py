import unreal as u,json,math
from pathlib import Path
exec(Path('D:/Multimodal/Outputs/ClientHomeStyles/build_style_map.py').read_text().rsplit('build(STYLE)',1)[0])
SB='/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Storybook'
e=u.get_editor_subsystem(u.EditorAssetSubsystem);ml=u.MaterialEditingLibrary
COL={'Walnut':(.16,.075,.032),'Oak':(.31,.18,.075),'Ivory':(.71,.64,.48),'Linen':(.58,.46,.29),'Sage':(.18,.28,.19),'DeepSage':(.075,.155,.115),'Clay':(.40,.145,.070),'Honey':(.50,.285,.065),'Ink':(.025,.045,.05),'Brass':(.48,.29,.075),'Glass':(.16,.30,.32),'Leaf':(.10,.25,.10),'Blue':(.065,.135,.19),'Wine':(.25,.065,.065)}
def mat(name,color,kind='plain'):
 path=SB+'/Materials/M_CH_Story_'+name
 m=u.load_asset(path) if e.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset('M_CH_Story_'+name,SB+'/Materials',u.Material,u.MaterialFactoryNew())
 ml.delete_all_material_expressions(m)
 pos=ml.create_material_expression(m,u.MaterialExpressionWorldPosition)
 c=ml.create_material_expression(m,u.MaterialExpressionCustom);i=u.CustomInput();i.set_editor_property('input_name','P');c.set_editor_property('inputs',[i]);c.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
 col='float3('+','.join(str(x) for x in color)+')'
 code='return '+col+';'
 if kind=='wood':code='float g=sin(P.x*.085+sin(P.y*.055)*1.3+sin(P.x*.013)*2.0); return '+col+'*(.97+.025*g);'
 if kind=='cloth':code='float w=sin(P.x*8.0)*sin(P.y*8.0)+sin(P.z*8.0)*.4; return '+col+'*(.97+.025*w);'
 if kind=='wall':code='float2 q=float2(P.x/40.,P.z/50.);float2 f=frac(q)-.5;float leaf=step(abs(f.x+f.y*.4)*1.8+abs(f.y)*.8,.11);float paper=.99+.008*sin(P.x*3.4)*sin(P.z*3.7);float3 upper='+col+'*paper*(1.-leaf*.055);float3 lower=float3(.15,.235,.18);return lerp(lower,upper,smoothstep(106.,109.,P.z));'
 if kind=='floor':code='float row=floor(P.y/26.);float2 q=float2((P.x+fmod(row,2.)*80.)/160.,P.y/26.);float2 f=frac(q);float seam=step(.004,f.x)*step(.012,f.y);float h=frac(sin(dot(floor(q),float2(12.9898,78.233)))*43758.5453);float grain=sin(P.x*.11+sin(P.y*.8)*.35);return '+col+'*(.92+h*.14+grain*.017)*lerp(.55,1.,seam);'
 if kind=='tile':code='float2 q=P.xy/28.;float2 f=frac(q);float line=step(.025,f.x)*step(.025,f.y);float alternate=fmod(floor(q.x)+floor(q.y),2.);float3 a=float3(.62,.60,.46);float3 b=float3(.25,.37,.29);return lerp(float3(.72,.66,.53),lerp(a,b,alternate),line);'
 c.set_editor_property('code',code);ml.connect_material_expressions(pos,'',c,'P');ml.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
 r=ml.create_material_expression(m,u.MaterialExpressionConstant);r.set_editor_property('r',.42 if name=='Brass' else .73 if name in ['Ivory','Glass'] else .88);ml.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS)
 if name=='Brass':
  n=ml.create_material_expression(m,u.MaterialExpressionConstant);n.set_editor_property('r',.55);ml.connect_material_property(n,'',u.MaterialProperty.MP_METALLIC)
 ml.recompile_material(m);e.save_loaded_asset(m);return m
def art(index):
 name=['Cat','Cottage','Flowers','Lake'][index];path=SB+'/Materials/M_CH_Story_Art'+name
 if e.does_asset_exist(path):return u.load_asset(path)
 m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_CH_Story_Art'+name,SB+'/Materials',u.Material,u.MaterialFactoryNew())
 tex=ml.create_material_expression(m,u.MaterialExpressionTextureSample);tex.set_editor_property('texture',u.load_asset(SB+'/Textures/T_CH_StorybookArt'))
 uv=ml.create_material_expression(m,u.MaterialExpressionTextureCoordinate)
 c=ml.create_material_expression(m,u.MaterialExpressionCustom);i=u.CustomInput();i.set_editor_property('input_name','UV');c.set_editor_property('inputs',[i]);c.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT2);c.set_editor_property('code','return UV*.498+float2('+str((index%2)*.5+.001)+','+str((index//2)*.5+.001)+');')
 ml.connect_material_expressions(uv,'',c,'UV');ml.connect_material_expressions(c,'',tex,'UVs');ml.connect_material_property(tex,'RGB',u.MaterialProperty.MP_BASE_COLOR)
 r=ml.create_material_expression(m,u.MaterialExpressionConstant);r.set_editor_property('r',.95);ml.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS);ml.recompile_material(m);e.save_loaded_asset(m);return m
def run():
 assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_name()=='LV_ClientHome_Storybook'
 palette={n:mat(n,c,'wood' if n in ['Walnut','Oak'] else 'cloth' if n in ['Linen','Honey','Sage'] else 'plain') for n,c in COL.items()}
 wall=mat('Wallpaper',(.70,.63,.49),'wall');floor=mat('Floor',(.30,.185,.085),'floor');tile=mat('Tile',(.6,.6,.4),'tile');arts=[art(i) for i in range(4)]
 original={r['label']:r for r in json.loads((ROOT/'Outputs/ClientHomeLinear/style_inventory.json').read_text())};bounds=json.loads((ROOT/'Outputs/ClientHomeLinear/style_mesh_bounds.json').read_text())
 aas=u.get_editor_subsystem(u.EditorActorSubsystem);actors=aas.get_all_level_actors();counts={'crafted':0,'restored_shapes':0,'retained_support':0,'paintings':0};artindex=0
 def reset(a,r):a.set_actor_location(u.Vector(*r['pos']),False,True);a.set_actor_rotation(u.Rotator(pitch=r['rot'][0],yaw=r['rot'][1],roll=r['rot'][2]),True);a.set_actor_scale3d(u.Vector(*r['scale']))
 for a in actors:
  label=a.get_actor_label();r=original.get(label);c=a.get_component_by_class(u.StaticMeshComponent)
  if isinstance(a,u.PostProcessVolume) and label=='PostProcessVolume2':
   s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_bias',-1.05);s.set_editor_property('override_auto_exposure_bias',True);s.set_editor_property('vignette_intensity',.16);s.set_editor_property('override_vignette_intensity',True);a.set_editor_property('settings',s)
  if not c or not c.static_mesh or not r:continue
  if label=='CH_ClearSky_Backdrop' or label.startswith(('CH_Minimal_Fur','CH_Minimal_Pawprint','CH_Minimal_Snack')):continue
  name=r['mesh'].split('.')[-1];cat,ken=category(name)
  if name in ['Cube','Sphere','Plane'] or name.startswith('SM_CH_'):
   if label.startswith(('CH_Linear_','CH_SmallBath_')):
    m=floor if 'Floor' in label else palette['DeepSage'] if any(t in label for t in ['Trim','Base','Crown','Skirting','Jamb']) else wall
    if 'Bath_TileFloor' in name:m=tile
    if label.startswith('CH_SmallBath_') and 'Tile' in label and 'Floor' not in label:m=palette['Sage']
    for i in range(c.get_num_materials()):c.set_material(i,m)
   continue
  craft={'Armchair':'Armchair','Chair':'Chair','Desk':'Desk','Bookshelf':'Bookshelf','Cabinet':'Cabinet','UpperCabinet':'UpperCabinet','Table':'Table','Fridge':'Fridge','Television':'Television','Frame':'Frame','Lamp':'Pendant','Rug':'Rug'}.get(cat)
  # Rounded fixtures and small everyday objects are stronger silhouettes in the original set.
  restore=cat in ['Bathtub','Toilet','Sink','Pan','Utensil','Fruit','Bottle','Bowl','Mug','Plate','Clock'] or name in ['SM_Kitchen_Countertop_B','SM_Kitchen_Countertop_C','SM_Stove_A','SM_Toaster','SM_Blender','SM_Microwave']
  if name in ['SM_Carpet_01','SM_Carpet_02'] or 'Native_B_SM_Carpet_02' in label:craft='RoundRug'
  if label.startswith('CH_SmallBath_') and 'Mirror' in label:craft=None;restore=True
  if restore:
   reset(a,r);c.set_static_mesh(u.load_asset(r['mesh']));c.set_editor_property('override_materials',[]);counts['restored_shapes']+=1
   color='Ivory' if cat in ['Bathtub','Toilet','Sink','Bowl','Mug','Plate'] else 'Brass' if cat=='Utensil' else 'Sage' if cat in ['Pan','Bottle'] else 'Honey' if cat=='Fruit' else 'Walnut'
   if cat=='Fruit' and any(k in name for k in ['Apple','Carrot','Clementine']):color='Clay'
   if 'Countertop_C' in name:color='Ivory'
   if 'Countertop_B' in name:color='Sage'
   if 'Stove' in name:color='DeepSage'
   if cat=='Clock':color='Brass'
   for i in range(c.get_num_materials()):c.set_material(i,palette[color])
  elif craft:
   reset(a,r);mesh=u.load_asset(SB+'/Meshes/SM_CH_Story_'+craft);turn=source_turn(name,cat)+180
   if cat=='Frame':
    b=bounds[r['mesh']];ext=[y-x for x,y in zip(b['min'],b['max'])];choices=[90,270] if ext[0]<ext[1] else [0,180];tr=a.get_actor_transform()
    def score(t):
     v=u.Vector(-math.sin(math.radians(t)),math.cos(math.radians(t)),0);d=u.MathLibrary.transform_location(tr,v)-a.get_actor_location();return -d.y
    turn=max(choices,key=score)
   fit(a,c,mesh,turn,bounds[r['mesh']]);counts['crafted']+=1
   for i,slot in enumerate(mesh.static_materials):
    n=slot.material_interface.get_name().replace('M_CH_Story_','') if slot.material_interface else ''
    if n=='Art':
     idx=artindex%4;c.set_material(i,arts[idx]);artindex+=1;counts['paintings']+=1
    elif n in palette:c.set_material(i,palette[n])
   if cat=='Armchair' and '/Living' in r['folder']:
    for i,slot in enumerate(mesh.static_materials):
     if slot.material_interface and slot.material_interface.get_name().endswith('_Honey'):c.set_material(i,palette['Clay'])
  else:
   counts['retained_support']+=1
   # Recolor authored support props to the same palette.
   aliases={'Wood':'Walnut','Cream':'Ivory','Paper':'Ivory','Teal':'Sage','Blue':'Blue','Ochre':'Honey','Rose':'Clay','Leaf':'Leaf','Dark':'Ink','Brass':'Brass','Water':'Glass'}
   for i,slot in enumerate(c.static_mesh.static_materials):
    n=slot.material_interface.get_name().replace('M_Paper_','') if slot.material_interface else ''
    if cat=='Book' and n=='Rose':c.set_material(i,palette[['Blue','Honey','DeepSage','Wine'][sum(map(ord,label))%4]])
    elif n in aliases:c.set_material(i,palette[aliases[n]])
  # Preserve clue identity on the original invisible anchors already present in the copied preview.
  if 'Home_Pot' in r['tags'] or 'Home_Window' in r['tags']:a.tags=[t for t in a.tags if not str(t).startswith('Home_')]
 # Shape the wall panels with real trim, leaving every doorway opening intact.
 cube=u.load_asset('/Engine/BasicShapes/Cube')
 def trim(label,pos,size,m):
  a=aas.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));a.set_actor_label(label);a.set_folder_path('ClientHome/Storybook/Architecture');a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,m);a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);a.set_actor_scale3d(u.Vector(*[v/100 for v in size]))
 for a in actors:
  if '_Dado_' in a.get_actor_label():aas.destroy_actor(a)
 for r in original.values():
  if not r['label'].startswith('CH_Linear_Rear'):continue
  x,y,z=r['center'];ex,ey,ez=r['extent'];front=y-ey-2
  for zz,h,m in [(108,5,palette['Walnut']),(103,2,palette['Brass']),(29,5,palette['DeepSage'])]:trim('CH_Story_Rail_'+r['label']+'_'+str(zz),(x,front,zz),(ex*2,3,h),m)
  for i in range(int(ex*2/100)+1):
   xx=x-ex+i*100
   if xx<x+ex-3:trim('CH_Story_Stile_'+r['label']+'_'+str(i),(xx,front,66),(3,2,72),palette['DeepSage'])
 assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
 e.save_directory(SB,only_if_is_dirty=False,recursive=True)
 (ROOT/'Outputs/ClientHomeStorybook/build_result.json').write_text(json.dumps(counts,indent=2))
run()
