"""Fit the entrance wall opening to the actual door and remove its misplaced duplicate frame."""
import unreal as u
actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
# Door_Frame_A2 is the frame aligned with the door hinge. The other copy
# was offset 43 cm toward the foreground and made a second partial outline.
extra=by.get('Door_Frame_SM')
if extra:
 extra.set_actor_hidden_in_game(True);extra.set_is_temporarily_hidden_in_editor(True);extra.set_actor_enable_collision(False)
 extra.get_component_by_class(u.StaticMeshComponent).set_editor_property('cast_hidden_shadow',False)
labels=['House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM','Cube5']
labels+=['CH_RightWall_'+n for n in ['House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM']]
seen=set()
for label in labels:
 a=by.get(label)
 if not a:continue
 c=a.get_component_by_class(u.StaticMeshComponent);mesh=c.static_mesh
 assert mesh.get_path_name().startswith('/Game/ClientHome_Haeso/')
 if mesh.get_path_name() in seen:continue
 seen.add(mesh.get_path_name());d=mesh.get_static_mesh_description(0);count=0
 for i in range(d.get_vertex_count()):
  v=u.VertexID();v.set_editor_property('id_value',i)
  if not d.is_vertex_valid(v):continue
  p=u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v));changed=False
  if -901<p.x<-799 and -311<=p.y<=-165 and 9<=p.z<=306:
   if abs(p.y+310)<.15:p.y=-300;changed=True
   elif abs(p.y+166)<.15:p.y=-176;changed=True
   if abs(p.z-305)<.15:p.z=285;changed=True
  if changed:
   d.set_vertex_position(v,u.MathLibrary.inverse_transform_location(a.get_actor_transform(),p));count+=1
 if count:
  mesh.build_from_static_mesh_descriptions([d],False,False)
  assert assets.save_loaded_asset(mesh,False)
 u.log('DOOR_OPENING_FITTED '+label+' '+str(count))
# Close the original source mesh's missing lintel and narrow frame reveals.
for name,y,z,sy,sz in [('Lintel',-238,320,160,70),('JambFront',-324,187,52,334),('JambBack',-162,187,32,334)]:
 label='CH_Entry_WallFinish_'+name
 a=by.get(label) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(-832.125,y,z))
 a.set_actor_label(label);a.set_actor_location(u.Vector(-832.125,y,z),False,False)
 a.set_actor_scale3d(u.Vector(.0321,sy/100,sz/100));a.set_folder_path('ClientHome/FridgeEntry')
 c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
 c.set_material(0,u.load_asset('/Game/StylizedKitchen/Materials/MI_Kitchen_Wall'))
 c.set_editor_property('cast_shadow',False);a.set_actor_enable_collision(True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
