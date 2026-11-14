"""Compact bathroom from the Fab example, with a camera-right doorway and cutaway front."""
import unreal as u,json,shutil
from pathlib import Path
base=Path('D:/Multimodal/Outputs/ClientHome');root='/Game/Multimodal'
e=u.get_editor_subsystem(u.UnrealEditorSubsystem);assert not e.get_game_world()
assert e.get_editor_world().get_path_name().startswith(root+'/01_Maps/ClientHome/LV_ClientHome_Minimal.')
backup=base/'Lvl_ClientHome_Minimal.before-small-bathroom.umap'
if not backup.exists():shutil.copyfile('D:/Multimodal/Content/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal.umap',backup)
rows={r['label']:r for r in json.loads((Path('D:/Multimodal/SourceAssets/Data/ClientHome/example-furnishings.json')).read_text())}
actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
def mapped(p):
 x,y,z=p;return (520-.8*x,-190-(y+1190)*320/660,21+(z-21)*.8)
def spawn(name,mesh,pos,rot=(0,0,0),scale=(1,1,1),materials=None,collision=True):
 label='CH_SmallBath_'+name;a=by.get(label)
 if not a:a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));a.set_actor_label(label);by[label]=a
 c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(mesh)
 if materials:
  for i,m in enumerate(materials):
   if m:c.set_material(i,u.load_asset(m))
 a.set_actor_location(u.Vector(*pos),False,False);a.set_actor_rotation(u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False)
 a.set_actor_scale3d(u.Vector(*scale));a.set_actor_enable_collision(collision);a.set_folder_path('ClientHome/SmallBathroom')
 return a
# Build a clean compact shell with the example's original tile and trim materials.
# The source architecture is an open house-wide mesh, so boolean cropping creates caps.
for old in ['House_Floor','House_Walls_SM','House_Outer_Walls_SM','Bathroom_Walls_Trim_SM','House_Molding_SM']:
 actor=by.get('CH_SmallBath_'+old)
 if actor:actors.destroy_actor(actor);by.pop('CH_SmallBath_'+old)
def box(name,pos,size,material,collision=True):
 dst=root+'/03_Graphics/Meshes/Buildings/ClientHome/SmallBathroom/SM_CH_Bath_'+name
 mesh=u.load_asset(dst) or assets.duplicate_asset('/Engine/BasicShapes/Cube',dst)
 # Keep tile density consistent with physical size, independent of wall length.
 source=u.load_asset('/Engine/BasicShapes/Cube').get_static_mesh_description(0)
 mesh.build_from_static_mesh_descriptions([source],False,False)
 d=mesh.get_static_mesh_description(0)
 for i in range(d.get_vertex_instance_count()):
  vi=u.VertexInstanceID();vi.set_editor_property('id_value',i)
  if not d.is_vertex_instance_valid(vi):continue
  poly=d.get_vertex_instance_connected_polygons(vi)[0]
  pts=[d.get_vertex_position(v) for v in d.get_polygon_vertices(poly)]
  flatx=max(v.x for v in pts)-min(v.x for v in pts)<.01
  flatz=max(v.z for v in pts)-min(v.z for v in pts)<.01
  uv=d.get_vertex_instance_uv(vi,0)
  if flatz:su,sv=size[0]/100,size[1]/100
  elif flatx:su,sv=size[1]/100,size[2]/100
  else:su,sv=size[0]/100,size[2]/100
  d.set_vertex_instance_uv(vi,u.Vector2D(uv.x*su,uv.y*sv),0)
 mesh.build_from_static_mesh_descriptions([d],False,False)
 assert assets.save_loaded_asset(mesh,False)
 return spawn(name,mesh,pos,scale=tuple(v/100 for v in size),materials=[material],collision=collision)
mat='/Game/ExternalAssets/StylizedKitchen/Materials/'
box('TileFloor',(717.5675,-350,20),(395.135,320,4),mat+'MI_Bathroom_Floor_Tiles')
# Back and left walls show the source's green tile; right wall has a 124 cm doorway.
for name,x,y,sx,sy in [('Back',717.5675,-190,407.135,12),('Left',915.135,-350,3.21,320),('RightBack',520,-280,12,180),('RightFront',520,-502,12,16)]:
 box(name+'Tile',(x,y,101),(sx,sy,160),mat+'MI_Walls_Tile')
 box(name+'Upper',(x,y,221),(sx,sy,80),mat+'MM_Base_Mat_2')
 box(name+'Trim',(x,y,181),(sx+2,sy+2,5),mat+'MM_Base_Mat_3')
box('DoorLintel',(520,-432,255),(12,124,12),mat+'MI_Walls_Tile')
front=by.pop('CH_SmallBath_FrontCutaway',None)
if front:actors.destroy_actor(front)
# Keep fixtures at 80% of the generous source-map size, and retain their hand-painted dressing.
fixtures=['Bathroom_Bathtub','Toilet','Bathroom_Sink','Bathroom_Mirror','Bathroom_Water_Glass','SM_Soap_01','Bathroom_Shower_Head','Bathroom_Towel_Rack2','Bathroom_Towels2','Bathroom_Mat_A']
sink=rows['Bathroom_Sink']['pos'];sink_target=mapped(sink)
for name in fixtures:
 row=rows[name];pos=mapped(row['pos']);pitch,yaw,roll=row['rot'];scale=tuple(v*.8 for v in row['scale'])
 if name in ['Bathroom_Mirror','Bathroom_Water_Glass','SM_Soap_01']:
  x,y,z=row['pos'];pos=(sink_target[0]-.8*(x-sink[0]),sink_target[1]-.8*(y-sink[1]),sink_target[2]+.8*(z-sink[2]))
 if name=='Bathroom_Mat_A':pos=(755,-386,22);scale=tuple(v*.55 for v in row['scale'])
 if name in ['Bathroom_Sink','Bathroom_Mirror','Bathroom_Water_Glass','SM_Soap_01','Bathroom_Shower_Head','Bathroom_Towel_Rack2','Bathroom_Towels2']:pos=(pos[0]-44.865,pos[1],pos[2])
 if name=='Bathroom_Bathtub':pos=(pos[0]-25,pos[1],pos[2])
 spawn(name,u.load_asset(row['mesh']),pos,(pitch,yaw+180,roll),scale,row['materials'],name in ['Bathroom_Bathtub','Toilet','Bathroom_Sink'])
# Original wooden bathroom frame, full enough for the player capsule to pass.
row=rows['Door_Frame_A']
spawn('DoorFrame',u.load_asset(row['mesh']),(520,-434,21),(0,0,0),(row['scale'][0],row['scale'][1]*.94,.8),row['materials'],False)
# Open the matching wooden door outward so it does not obscure the bathroom.
row=rows['Assets_Proxy_Door_Proxy']
spawn('OpenDoor',u.load_asset(row['mesh']),(520,-370,21),(0,-90,0),(1,1,.88),row['materials'],True)
# Clear the obsolete hidden mirror/partition and cut an access opening in retained house collision.
for name in ['Assets_Proxy_Mirror_Proxy','Cube']:
 a=by.get(name)
 if a:a.set_actor_enable_collision(False)
for name in ['House_Walls_SM','House_Outer_Walls_SM']:
 a=by[name];c=a.get_component_by_class(u.StaticMeshComponent)
 dst=root+'/03_Graphics/Meshes/Buildings/ClientHome/SmallBathroom/SM_CH_Bath_Access_'+name
 mesh=u.load_asset(dst)
 if not mesh:mesh=assets.duplicate_asset(c.static_mesh.get_path_name(),dst)
 dm=u.DynamicMesh();u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
 dm.transform_mesh(a.get_actor_transform())
 cut=u.DynamicMesh();cut.append_box(u.GeometryScriptPrimitiveOptions(),u.Transform(location=u.Vector(475,-432,10)),160,124,270)
 dm.apply_mesh_boolean(u.Transform(),cut,u.Transform(),u.GeometryScriptBooleanOperation.SUBTRACT,u.GeometryScriptMeshBooleanOptions())
 dm.inverse_transform_mesh(a.get_actor_transform())
 u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,u.GeometryScriptCopyMeshToAssetOptions(),u.GeometryScriptMeshWriteLOD())
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 assert assets.save_loaded_asset(mesh,False)
 c.set_static_mesh(mesh)
# Soft local lighting; fixtures and tile retain the original example's color palette.
light=by.get('CH_SmallBath_WarmLight')
if not light:light=actors.spawn_actor_from_class(u.PointLight,u.Vector(740,-345,235));light.set_actor_label('CH_SmallBath_WarmLight')
c=light.get_component_by_class(u.PointLightComponent);c.set_editor_property('intensity',12);c.set_editor_property('attenuation_radius',440);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',4100);c.set_editor_property('cast_shadows',False)
light.set_folder_path('ClientHome/SmallBathroom')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('SMALL_BATHROOM_SAVED')
