"""Relocate the entrance below the fridge, with a real opening and exit landing."""
import unreal as u,json
from pathlib import Path
base=Path('D:/Multimodal/Saved/ClientHome')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert (base/'Lvl_ClientHome_Minimal.before-fridge-entry.umap').exists()
actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
# Cut both the real collision walls and the hidden light-blocking mesh.
labels=['House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM','Cube5']
report=[]
for name in labels:
 a=by[name];c=a.get_component_by_class(u.StaticMeshComponent)
 dst='/Game/ClientHome_Haeso/Meshes/FridgeEntry/SM_CH_'+name
 mesh=u.load_asset(dst)
 if not mesh:
  mesh=assets.duplicate_asset(c.static_mesh.get_path_name(),dst)
  dm=u.DynamicMesh();res=u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(mesh,dm,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
  assert 'SUCCESS' in str(res[-1]),res
  dm.transform_mesh(a.get_actor_transform())
  cutter=u.DynamicMesh();cutter.append_box(u.GeometryScriptPrimitiveOptions(),u.Transform(location=u.Vector(-850,-238,10)),100,144,295)
  dm.apply_mesh_boolean(u.Transform(),cutter,u.Transform(),u.GeometryScriptBooleanOperation.SUBTRACT,u.GeometryScriptMeshBooleanOptions())
  dm.inverse_transform_mesh(a.get_actor_transform())
  res=u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm,mesh,u.GeometryScriptCopyMeshToAssetOptions(),u.GeometryScriptMeshWriteLOD())
  assert 'SUCCESS' in str(res[-1]),res
  mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  assert assets.save_loaded_asset(mesh,False)
 c.set_static_mesh(mesh);report.append(name)
# Translate the doorway as a rigid assembly; preserve its existing swing axis.
baseline={r['label']:r for r in json.loads((base/'right-wall-before.json').read_text())}
dx=-830-baseline['Assets_Proxy_Door_Proxy']['pos'][0];dy=-180-baseline['Assets_Proxy_Door_Proxy']['pos'][1]
for name in ['Assets_Proxy_Door_Proxy','Door_Frame_SM','Door_Frame_A2']:
 x,y,z=baseline[name]['pos'];by[name].set_actor_location(u.Vector(x+dx,y+dy,z),False,False)
# Frame assets use solid box collision; the carved wall now supplies the jamb collision.
for name in ['Door_Frame_SM','Door_Frame_A2']:by[name].set_actor_enable_collision(False)
by['SM_Carpet_04'].set_actor_location(u.Vector(-752,-238,20.9533),False,False)
by['CH_Minimal_ExitTarget'].set_actor_location(u.Vector(-925,-238,110),False,False)
# Keep entry-side flowers with the relocated threshold.
for name in ['SM_FlowerPot_19','SM_FlowersPlant_23']:
 x,y,z=baseline[name]['pos'];by[name].set_actor_location(u.Vector(-790+x-427.77,-365+y+515.84,z),False,False)
def box(name,pos,scale,visible,material=None):
 a=by.get(name) or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));a.set_actor_label(name)
 a.set_actor_location(u.Vector(*pos),False,False);a.set_actor_scale3d(u.Vector(*scale))
 c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
 if material:c.set_material(0,material)
 a.set_actor_hidden_in_game(not visible);a.set_actor_enable_collision(True)
 a.set_folder_path('ClientHome/FridgeEntry')
 return a
floor=by['House_Floor'].get_component_by_class(u.StaticMeshComponent).get_material(0)
box('CH_Entry_Landing',(-920,-238,18.5),(1.8,1.6,.05),True,floor)
box('CH_Entry_OldOpeningSeal',(465,-330,155),(.20,1.40,2.70),False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(base/'fridge-entry-report.json').write_text(json.dumps({'door':[-830,-180,22],'exit':[-925,-238,110],'cut_meshes':report},indent=2))
u.log('FRIDGE_ENTRY_SAVED')
