"""Remove the bathroom extension and close the shortened entrance boundary."""
import unreal as u,json
from pathlib import Path
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
out=Path('D:/Multimodal/Saved/ClientHome')
assert (out/'Lvl_ClientHome_Minimal.before-no-bathroom.umap').exists()
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
struct={'House_Ceiling_SM','House_Walls_SM','House_Floor','House_Molding_SM','House_Outer_Walls_SM','Crown_Molding_SM','Bathroom_Walls_Trim_SM'}
report={'hidden':[],'meshes':[]}
for name,a in by.items():
    c=a.get_component_by_class(u.StaticMeshComponent)
    structural=name in struct or name.startswith('CH_Minimal_Cutaway_') or name.startswith('Cube')
    if structural and c and c.static_mesh:
        path='/Game/ClientHome_Haeso/Meshes/NoBathroom/SM_CH_'+name
        if assets.does_asset_exist(path):c.set_static_mesh(u.load_asset(path));continue
        mesh=assets.duplicate_asset(c.static_mesh.get_path_name(),path);d=mesh.get_static_mesh_description(0);polys={}
        for i in range(d.get_vertex_count()):
            vid=u.VertexID();vid.set_editor_property('id_value',i)
            if not d.is_vertex_valid(vid):continue
            p=u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(vid))
            for pid in d.get_vertex_connected_polygons(vid):polys[pid.get_editor_property('id_value')]=pid
            p.y=max(p.y,-550.)
            d.set_vertex_position(vid,u.MathLibrary.inverse_transform_location(a.get_actor_transform(),p))
        removed=[]
        for pid in polys.values():
            pts=[u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(pid)]
            # Collapsed former room faces cannot leave duplicate planes at the cut.
            if all(abs(p.y+550)<.01 for p in pts):removed.append(pid)
        for pid in removed:d.delete_polygon(pid)
        if d.get_polygon_count()==0:
            a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False)
            c.set_editor_property('cast_hidden_shadow',False)
        else:
            mesh.build_from_static_mesh_descriptions([d],False,False)
            mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            assert assets.save_loaded_asset(mesh)
            c.set_static_mesh(mesh)
        report['meshes'].append(name)
    elif a.get_actor_location().y<-550 and (c or isinstance(a,u.Light) or isinstance(a,u.DecalActor) or isinstance(a,u.ReflectionCapture)):
        a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False)
        if c:c.set_editor_property('cast_hidden_shadow',False)
        if isinstance(a,u.Light):a.get_component_by_class(u.LightComponent).set_visibility(False)
        report['hidden'].append(name)

def wall(name,pos,scale,mat):
    a=by.get(name)
    if not a:a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));a.set_actor_label(name)
    a.set_actor_location(u.Vector(*pos),False,False);a.set_actor_scale3d(u.Vector(*scale))
    c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cube'))
    c.set_material(0,u.load_asset(mat));a.set_folder_path('ClientHome/ClosedBathroomBoundary')
    return a
wall('CH_NoBath_EndWall',(340,-540,188),(2.4,.20,3.34),'/Game/StylizedKitchen/Materials/MI_Wallpaper_A')
wall('CH_NoBath_Corner',(230,-520,188),(.20,.60,3.34),'/Game/StylizedKitchen/Materials/MI_Wallpaper_A')
wall('CH_NoBath_Baseboard',(340,-528,27),(2.4,.045,.12),'/Game/StylizedKitchen/Materials/MI_Molding_Trim')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(out/'no-bathroom-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('BATHROOM_REMOVED_SAVED')
