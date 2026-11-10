"""Audit the structural edit against its pre-edit actor manifest (outside PIE)."""
import unreal as u,json,math
from pathlib import Path
base=Path('D:/Multimodal/Saved/ClientHome')
baseline=json.loads((base/'precompact-actors.json').read_text(encoding='utf-8'))
report=json.loads((base/'compact-layout-report.json').read_text(encoding='utf-8'))
actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert len(actors)==len(baseline)
hidden=set(json.loads((base/'compact-extra-hidden.json').read_text()))|set(report['removed_groups'])|{'Plane','SM_Carpet_02','Assets_Proxy_kitchen_Shelf_A_Proxy2'}
for row in baseline:
    name=row['label'];a=actors[name];p=a.get_actor_location();x,y,z=row['location']
    if name in report['moved']:x=x+220 if x<=0 else (220+x*.45 if x<400 else x)
    if name=='Broom':x,y,z=-360,-405,20.953573
    assert math.dist([p.x,p.y,p.z],[x,y,z])<.1,(name,'position')
    scale=a.get_actor_scale3d()
    assert math.dist([scale.x,scale.y,scale.z],row['scale'])<.001,(name,'scale')
    c=a.get_component_by_class(u.StaticMeshComponent)
    if name in report['structure']:
        assert any(folder in c.static_mesh.get_path_name() for folder in ['/Meshes/CompactV2/','/Meshes/OpenKitchen/','/Meshes/Polished/']),name
    elif c and c.static_mesh:assert c.static_mesh.get_path_name()==row['mesh'],name
    if name in hidden:assert a.get_editor_property('hidden'),name
for name in ['Assets_Proxy_LR_Desk_Proxy','SM_LeatherCouch','SM_LeatherCouch2','SM_Carpet_02']:
    assert actors[name].get_editor_property('hidden') and not actors[name].get_actor_enable_collision(),name
for tag in ['Home_Pot','Home_Fur','Home_Window','Home_Snack','Home_Pawprints','Home_Door','Home_Exit']:
    found=[a for a in actors.values() if a.actor_has_tag(tag)]
    assert len(found)==1 and (tag=='Home_Exit' or not found[0].get_editor_property('hidden')),tag
(base/'compact-audit.json').write_text(json.dumps({'passed':True,'actors':len(actors),'hidden_central_props':len(report['removed_groups']),'shortened_cm':220},indent=2),encoding='utf-8')
u.log('COMPACT_AUDIT_OK')
