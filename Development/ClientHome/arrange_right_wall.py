"""Mirror the kitchen, move the shelf nook, and open the left camera sightline.

Uses the pre-edit manifest so rerunning cannot accumulate transformations.
Only owned map actors and duplicated render-only wall meshes are modified.
"""
import unreal as u, json
from pathlib import Path

base=Path('D:/Multimodal/Saved/ClientHome')
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
assert (base/'Lvl_ClientHome_Minimal.before-right-wall.umap').exists()
rows=json.loads((base/'right-wall-before.json').read_text())
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
report={'kitchen':[], 'study':[], 'cutaway':[]}
for row in rows:
    name=row['label']; x,y,z=row['pos']; a=by[name]
    if row['hidden']:continue
    # Furniture and every tabletop/shelf prop, excluding the house structure.
    prop=row['mesh'] and not name.startswith(('House_', 'CH_Minimal_Cutaway_', 'Cube', 'Sky'))
    if prop and -840<x<-230 and 570<y<670:
        a.set_actor_location(u.Vector(x+620,y,z),False,False)
        report['study'].append(name)
    elif (prop and -840<x<-230 and -530<y<300) or name in ('SpotLight','PointLight','RectLight'):
        pitch,yaw,roll=row['rot'];sx,sy,sz=row['scale']
        # World-Y reflection: M R M and a local negative Y scale preserve the
        # exact arrangement, including tilted crockery and fridge magnets.
        a.set_actor_transform(u.Transform(location=u.Vector(x,150-y,z),rotation=u.Rotator(pitch=pitch,yaw=-yaw,roll=-roll),scale=u.Vector(sx,-sy,sz)),False,False)
        report['kitchen'].append(name)
    elif name=='RectLight2':
        a.set_actor_location(u.Vector(x+620,y,z),False,False)

for row in rows:
    name=row['label']
    if not name.startswith('CH_Minimal_Cutaway_'):continue
    a=by[name];c=a.get_component_by_class(u.StaticMeshComponent)
    dst='/Game/ClientHome_Haeso/Meshes/LeftCamera/SM_CH_'+name
    mesh=u.load_asset(dst)
    if not mesh:
        mesh=assets.duplicate_asset(row['mesh'],dst)
        d=mesh.get_static_mesh_description(0);polygons={}
        for i in range(d.get_vertex_count()):
            vid=u.VertexID();vid.set_editor_property('id_value',i)
            if d.is_vertex_valid(vid):
                for pid in d.get_vertex_connected_polygons(vid):polygons[pid.get_editor_property('id_value')]=pid
        removed=[]
        for pid in polygons.values():
            pts=[u.MathLibrary.transform_location(a.get_actor_transform(),d.get_vertex_position(v)) for v in d.get_polygon_vertices(pid)]
            if max(p.y for p in pts)<-125:removed.append(pid)
        for pid in removed:d.delete_polygon(pid)
        mesh.build_from_static_mesh_descriptions([d],False,False)
        assert assets.save_loaded_asset(mesh)
        report['cutaway'].append([name,len(removed)])
    c.set_static_mesh(mesh)
    a.set_actor_enable_collision(False)
for name in ('CH_NoBath_EndWall','CH_NoBath_Baseboard','CH_NoBath_Corner','Assets_Proxy_Mirror_Proxy'):
    a=by[name];a.set_actor_hidden_in_game(True)
    a.get_component_by_class(u.StaticMeshComponent).set_editor_property('cast_hidden_shadow',True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(base/'right-wall-report.json').write_text(json.dumps(report,indent=2))
u.log('RIGHT_WALL_LAYOUT_SAVED: '+str({k:len(v) for k,v in report.items()}))
