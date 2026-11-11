"""Restore the screen-right exterior wall from the existing doorway-cut source meshes."""
import unreal as u
actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
for name in ['House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM']:
 source=by[name];sc=source.get_component_by_class(u.StaticMeshComponent)
 path='/Game/ClientHome_Haeso/Meshes/RightWall/SM_CH_Right_'+name
 mesh=u.load_asset(path) or assets.duplicate_asset(sc.static_mesh.get_path_name(),path)
 d=sc.static_mesh.get_static_mesh_description(0);polys={}
 for i in range(d.get_vertex_count()):
  v=u.VertexID();v.set_editor_property('id_value',i)
  if d.is_vertex_valid(v):
   for p in d.get_vertex_connected_polygons(v):polys[p.get_editor_property('id_value')]=p
 keep=[]
 for p in polys.values():
  vs=[u.MathLibrary.transform_location(source.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(p)]
  if all(v.x < -795 and v.y >= -550.1 for v in vs):keep.append(p)
  else:d.delete_polygon(p)
 if not keep:continue
 mesh.build_from_static_mesh_descriptions([d],False,False)
 assert assets.save_loaded_asset(mesh,False)
 label='CH_RightWall_'+name
 a=by.get(label) or actors.spawn_actor_from_class(u.StaticMeshActor,source.get_actor_location())
 a.set_actor_label(label);a.set_actor_transform(source.get_actor_transform(),False,False)
 c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(mesh)
 for i,m in enumerate(sc.get_materials()):
  if m:c.set_material(i,m)
 c.set_editor_property('cast_shadow',False)
 a.set_actor_enable_collision(False);a.set_folder_path('ClientHome/CameraCutaway')
 u.log('RIGHT_WALL_RESTORED '+name+' '+str(len(keep)))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
