import json
from collections import Counter
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def vec(v): return [round(v.x,3),round(v.y,3),round(v.z,3)]
rows=[]
for a in actors:
    loc=a.get_actor_location(); origin,extent=a.get_actor_bounds(False)
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'folder':str(a.get_folder_path()),'loc':vec(loc),'scale':vec(a.get_actor_scale3d()),'rotation':str(a.get_actor_rotation()),'bounds':[vec(origin),vec(extent)],'parent':a.get_attach_parent_actor().get_name() if a.get_attach_parent_actor() else None,'tags':[str(t) for t in a.tags]}
    c=a.get_component_by_class(unreal.StaticMeshComponent)
    if c:
        row['mesh']=c.static_mesh.get_path_name() if c.static_mesh else None
        row['materials']=[m.get_path_name() if m else None for m in c.get_materials()]
    rows.append(row)
(_linear_root/'inventory_before.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
(_linear_root/'world.txt').write_text(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),encoding='utf-8')
extra=[]
for a in actors:
    extra.append({'name':a.get_name(),'hidden':a.get_editor_property('hidden'),'temp_hidden':a.is_temporarily_hidden_in_editor(),'collision':a.get_actor_enable_collision()})
(_linear_root/'visibility_before.json').write_text(json.dumps(extra,indent=2),encoding='utf-8')
bp=unreal.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Minimal')
cdo=unreal.get_default_object(bp.generated_class())
props={}
for k in dir(cdo):
    if any(s in k.lower() for s in ['camera','bound','clue','home','min','max','follow']):
        try: props[k]=str(cdo.get_editor_property(k))
        except: pass
(_linear_root/'player_properties.json').write_text(json.dumps(props,indent=2),encoding='utf-8')
from editor_toolset.toolsets.blueprint import BlueprintTools, _BlueprintCache
unreal.InternationalizationLibrary.set_current_language('en',False)
for path in ['/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Minimal','/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Minimal']:
    b=unreal.load_asset(path)
    _BlueprintCache.invalidate(b)
    for g in BlueprintTools.list_graphs(b):
        (_linear_root/(b.get_name()+'_'+g.get_name()+'.txt')).write_text(BlueprintTools.read_graph_dsl(g),encoding='utf-8')
