"""Remove only the kitchen/entrance partition from owned structural mesh copies."""
import unreal as u,json
from pathlib import Path
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
base=Path('D:/Multimodal/Saved/ClientHome')
assert (base/'Lvl_ClientHome_Minimal.before-partition.umap').exists()
report=json.loads((base/'open-partition-report.json').read_text()) if (base/'open-partition-report.json').exists() else []
labels={'House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM'}
labels|={'CH_Minimal_Cutaway_'+n for n in list(labels)}
for a in actors.get_all_level_actors():
    name=a.get_actor_label()
    if name not in labels:continue
    c=a.get_component_by_class(u.StaticMeshComponent)
    path='/Game/ClientHome_Haeso/Meshes/OpenKitchen/SM_CH_Open_'+name
    if assets.does_asset_exist(path):
        c.set_static_mesh(u.load_asset(path));continue
    mesh=assets.duplicate_asset(c.static_mesh.get_path_name(),path)
    d=mesh.get_static_mesh_description(0)
    # Enumerate via vertices: cutaway descriptions may have sparse polygon IDs.
    polygons={}
    for i in range(d.get_vertex_count()):
        vid=u.VertexID();vid.set_editor_property('id_value',i)
        if not d.is_vertex_valid(vid):continue
        for pid in d.get_vertex_connected_polygons(vid):polygons[pid.get_editor_property('id_value')]=pid
    removed=[]
    for pid in polygons.values():
        pts=[u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(pid)]
        lo=[min(getattr(v,k) for v in pts) for k in ['x','y','z']]
        hi=[max(getattr(v,k) for v in pts) for k in ['x','y','z']]
        in_partition=lo[0]>=-230 and hi[0]<=-190 and lo[1]>=-526 and hi[1]<=-125
        bathroom_end=hi[1]<-495 and hi[1]-lo[1]<2
        if in_partition and not bathroom_end:removed.append(pid)
    assert removed,name
    for pid in removed:d.delete_polygon(pid)
    mesh.build_from_static_mesh_descriptions([d],False,False)
    mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assert assets.save_loaded_asset(mesh)
    c.set_static_mesh(mesh)
    report.append({'actor':name,'removed_polygons':len(removed),'mesh':path})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
if report:(base/'open-partition-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('KITCHEN_PARTITION_OPEN_SAVED: '+str(report))
