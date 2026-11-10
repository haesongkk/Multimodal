"""Repair sparse cutaway topology after compaction and remove ghost furniture shadows."""
import unreal as u,json
from pathlib import Path
base=Path('D:/Multimodal/Saved/ClientHome')
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
baseline={r['label']:r for r in json.loads((base/'precompact-actors.json').read_text())}
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
result=[]
for name,a in by.items():
    if not name.startswith('CH_Minimal_Cutaway_'):continue
    path='/Game/ClientHome_Haeso/Meshes/Polished/SM_CH_Polished_'+name
    c=a.get_component_by_class(u.StaticMeshComponent)
    if assets.does_asset_exist(path):c.set_static_mesh(u.load_asset(path));continue
    mesh=assets.duplicate_asset(baseline[name]['mesh'],path)
    d=mesh.get_static_mesh_description(0);polys={};vertices=0
    # Polygon deletion leaves holes in IDs. Walk every valid vertex, not a
    # range bounded by polygon count, to avoid partially transformed triangles.
    for i in range(d.get_vertex_count()):
        vid=u.VertexID();vid.set_editor_property('id_value',i)
        if not d.is_vertex_valid(vid):continue
        wp=u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(vid))
        wp.x=wp.x+220 if wp.x<=0 else (220+wp.x*.45 if wp.x<400 else wp.x)
        d.set_vertex_position(vid,u.MathLibrary.inverse_transform_location(a.get_actor_transform(),wp));vertices+=1
        for pid in d.get_vertex_connected_polygons(vid):polys[pid.get_editor_property('id_value')]=pid
    removed=[]
    for pid in polys.values():
        pts=[u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(pid)]
        lo=[min(getattr(v,k) for v in pts) for k in ['x','y','z']];hi=[max(getattr(v,k) for v in pts) for k in ['x','y','z']]
        if lo[0]>=-230 and hi[0]<=-190 and lo[1]>=-526 and hi[1]<=-125 and not (hi[1]<-495 and hi[1]-lo[1]<2):removed.append(pid)
    for pid in removed:d.delete_polygon(pid)
    mesh.build_from_static_mesh_descriptions([d],False,False)
    assert assets.save_loaded_asset(mesh)
    c.set_static_mesh(mesh)
    a.set_actor_enable_collision(False)
    result.append({'actor':name,'vertices':vertices,'removed_partition_polygons':len(removed)})
# Removed furniture must not leave invisible silhouettes in the open passage.
removed=set(json.loads((base/'compact-layout-report.json').read_text())['removed_groups'])
removed|=set(json.loads((base/'compact-extra-hidden.json').read_text()))|{'SM_Carpet_02'}
for name in removed:
    a=by[name];c=a.get_component_by_class(u.StaticMeshComponent)
    if c:c.set_editor_property('cast_hidden_shadow',False)
# The camera-facing kitchen wall is already cut away; its hanging pictures
# must follow it rather than float above the counter without support.
for name in ['Rooster_Pictures_Picture_Frame_C','Rooster_Pictures_Picture_Frame_D']:
    a=by[name]
    a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
    a.set_actor_enable_collision(False)
    a.get_component_by_class(u.StaticMeshComponent).set_editor_property('cast_hidden_shadow',False)
by['Broom'].set_actor_location(u.Vector(-360,-405,20.953573),False,False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
if result:(base/'polished-layout-report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('OPEN_HOME_POLISHED')
