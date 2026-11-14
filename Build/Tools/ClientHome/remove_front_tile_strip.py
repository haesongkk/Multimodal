"""Remove the obsolete example-bathroom tile strip from the front floor edge."""
import unreal as u
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
a=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='House_Floor')
c=a.get_component_by_class(u.StaticMeshComponent)
assert c.static_mesh.get_path_name().startswith('/Game/Multimodal/')
d=c.static_mesh.get_static_mesh_description(0);polys={}
for i in range(d.get_vertex_count()):
 v=u.VertexID();v.set_editor_property('id_value',i)
 if d.is_vertex_valid(v):
  for p in d.get_vertex_connected_polygons(v):polys[p.get_editor_property('id_value')]=p
removed=[]
for p in polys.values():
 vs=[u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(p)]
 if d.get_polygon_polygon_group(p).get_editor_property('id_value')==0 and all(-550.1<=v.y<=-526.5 for v in vs):removed.append(p)
for p in removed:d.delete_polygon(p)
if removed:
 c.static_mesh.build_from_static_mesh_descriptions([d],False,False)
 c.static_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 assert assets.save_loaded_asset(c.static_mesh,False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('OLD_FRONT_TILE_STRIP_REMOVED '+str(len(removed)))
