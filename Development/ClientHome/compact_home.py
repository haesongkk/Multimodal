"""Shorten the redundant central rooms without editing the Fab source assets.

Run once on the furnished Minimal map, outside PIE. The pre-edit map file and
actor manifest are retained so this structural edit can be inspected/reverted.
"""
import unreal as u,json
from pathlib import Path

ROOT='/Game/ClientHome_Haeso'
MAP=ROOT+'/Maps/Lvl_ClientHome_Minimal'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith(MAP+'.')
assert Path('D:/Multimodal/Saved/ClientHome/Lvl_ClientHome_Minimal.precompact.umap').exists()
assert not Path('D:/Multimodal/Saved/ClientHome/compact-layout-report.json').exists(),'Already compacted'

assert levels.load_level(MAP)

def compact_x(x):
    return x+220 if x<=0 else (220+x*.45 if x<400 else x)

def vec(v):return [v.x,v.y,v.z]
baseline=[];report={'removed_groups':[],'moved':[],'structure':[]}
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
structural={'House_Ceiling_SM','House_Walls_SM','House_Floor','House_Molding_SM','House_Outer_Walls_SM','Crown_Molding_SM','Bathroom_Walls_Trim_SM'}
for name,a in by.items():
    c=a.get_component_by_class(u.StaticMeshComponent)
    p=a.get_actor_location(); t=a.get_actor_transform()
    baseline.append({'label':name,'location':vec(p),'rotation':str(a.get_actor_rotation()),'scale':vec(a.get_actor_scale3d()),'hidden':a.get_editor_property('hidden'),'collision':a.get_actor_enable_collision(),'mesh':c.static_mesh.get_path_name() if c and c.static_mesh else None})
Path('D:/Multimodal/Saved/ClientHome/precompact-actors.json').write_text(json.dumps(baseline,indent=2),encoding='utf-8')

for name,a in by.items():
    c=a.get_component_by_class(u.StaticMeshComponent)
    p=a.get_actor_location();t=a.get_actor_transform()
    is_structure=name in structural or name.startswith('CH_Minimal_Cutaway_') or name.startswith('Cube')
    # The desk nook and the pair of spare armchairs, including their set dressing.
    remove=not is_structure and not name.startswith('CH_Minimal_') and ((-460<p.x<300 and -530<p.y<-125) or (-260<p.x<300 and p.y>400))
    if remove and (c or isinstance(a,u.DecalActor) or isinstance(a,u.Light)):
        a.set_actor_hidden_in_game(True)
        a.set_is_temporarily_hidden_in_editor(True)
        a.set_actor_enable_collision(False)
        a.set_folder_path('ClientHome/RemovedCentralRooms')
        if c:c.set_editor_property('cast_hidden_shadow',False)
        if isinstance(a,u.Light):a.get_component_by_class(u.LightComponent).set_visibility(False)
        report['removed_groups'].append(name)
        continue
    if is_structure and c and c.static_mesh:
        path=ROOT+'/Meshes/CompactV2/SM_CH_Compact_'+name
        mesh=u.load_asset(path) if assets.does_asset_exist(path) else assets.duplicate_asset(c.static_mesh.get_path_name(),path)
        assert mesh,path
        desc=mesh.get_static_mesh_description(0)
        for i in range(desc.get_vertex_count()):
            vid=u.VertexID();vid.set_editor_property('id_value',i)
            if not desc.is_vertex_valid(vid):continue
            wp=u.MathLibrary.transform_location(t,desc.get_vertex_position(vid))
            wp.x=compact_x(wp.x)
            desc.set_vertex_position(vid,u.MathLibrary.inverse_transform_location(t,wp))
        mesh.build_from_static_mesh_descriptions([desc],False,False)
        body=mesh.get_editor_property('body_setup')
        body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        assert assets.save_loaded_asset(mesh)
        c.set_static_mesh(mesh)
        c.recreate_physics_state() if hasattr(c,'recreate_physics_state') else None
        report['structure'].append(name)
    elif name not in ['InstancedFoliageActor']:
        new=u.Vector(compact_x(p.x),p.y,p.z)
        if abs(new.x-p.x)>.01:
            a.set_actor_location(new,False,False)
            report['moved'].append(name)
assert levels.save_current_level()
Path('D:/Multimodal/Saved/ClientHome/compact-layout-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('COMPACT_HOME_SAVED: '+str({k:len(v) for k,v in report.items()}))
