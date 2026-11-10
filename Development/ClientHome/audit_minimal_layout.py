"""Read-only original/example comparison. Restores the owned map before returning."""
import unreal as u,json
from pathlib import Path
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
SOURCE='/Game/StylizedKitchen/Levels/Stylized_Interior'
MAP='/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal'
assert not u.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Save current map first'
def snapshot():
    result={}
    for a in actors.get_all_level_actors():
        t=a.get_actor_transform(); r=a.get_actor_rotation(); p=t.translation; s=t.scale3d
        item={'transform':[round(v,3) for v in [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]],'hidden':a.get_editor_property('hidden')}
        c=a.get_component_by_class(u.StaticMeshComponent)
        if c:
            item['mesh']=c.static_mesh.get_path_name() if c.static_mesh else None
            item['materials']=[m.get_path_name() if m else None for m in c.get_materials()]
        light=a.get_component_by_class(u.LightComponent)
        if light:
            color=light.get_editor_property('light_color')
            item['light']=[light.get_editor_property('intensity'),color.r,color.g,color.b,color.a]
        result[a.get_actor_label()]=item
    return result
try:
    assert levels.load_level(SOURCE)
    original=snapshot()
finally:
    assert levels.load_level(MAP)
current=snapshot()
allowed={'SM_FlowerPot_02','SM_FlowersPlant_02','Assets_Proxy_LR_Window_Proxy','PlayerStart'}
hidden_allowed={'House_Ceiling_SM','House_Walls_SM','House_Outer_Walls_SM','House_Molding_SM','Crown_Molding_SM','Bathroom_Walls_Trim_SM','Kitchen_Window','Kitchen_Curtain_Low','Kitchen_Curtain_Low2','Curtain_Rod','Cube'} | {'Cube'+str(i) for i in range(2,17)}
missing=sorted(set(original)-set(current))
changed={name:[k for k in old if old[k]!=current[name].get(k)] for name,old in original.items() if name in current and old!=current[name]}
unexpected={name:keys for name,keys in changed.items() if not ((name in allowed and keys==['transform']) or (name in hidden_allowed and keys==['hidden']))}
added=sorted(set(current)-set(original))
report={'source_actors':len(original),'preserved_actors':len(original)-len(changed),'changed_original_actors':changed,'missing_original_actors':missing,'added_actors':added,'unexpected_changes':unexpected}
Path('D:/Multimodal/Saved/ClientHome/minimal-layout-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not missing and not unexpected,report
assert len(added)==36 and all(n.startswith('CH_Minimal_') for n in added),added
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(300,-50,175),u.Rotator(pitch=-5,yaw=40,roll=0))
u.EditorLevelLibrary.editor_set_game_view(True)
u.log('MINIMAL_LAYOUT_AUDIT_OK')
