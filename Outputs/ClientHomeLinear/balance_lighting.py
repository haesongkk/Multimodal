"""Balance lighting in the linear map without changing its materials or layout."""
import unreal as u,json
from pathlib import Path
out=Path('D:/Multimodal/Outputs/ClientHomeLinear')
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert 'LV_ClientHome_Linear.' in world.get_path_name()
aas=u.get_editor_subsystem(u.EditorActorSubsystem)
before={r['name']:r for r in json.loads((out/'lighting_before.json').read_text())}
changes=[]
for actor in aas.get_all_level_actors():
    light=actor.get_component_by_class(u.LocalLightComponent)
    if not light or actor.get_name() not in before:continue
    row=before[actor.get_name()];label=actor.get_actor_label()
    if row['hidden']:continue
    if label.startswith('CH_Linear_') or isinstance(light,u.RectLightComponent):
        light.set_intensity(0)
        changes.append({'label':label,'intensity':0})
    else:
        value=float(row['intensity'])*.22
        light.set_mobility(u.ComponentMobility.MOVABLE)
        light.set_intensity(value)
        light.set_light_color(u.LinearColor(1,1,1,1))
        light.set_editor_property('use_temperature',True)
        light.set_editor_property('temperature',4200.)
        light.set_editor_property('attenuation_radius',min(float(row['attenuation_radius']),350.))
        light.set_editor_property('indirect_lighting_intensity',.3)
        changes.append({'label':label,'intensity':value})
label='CH_Linear_UniformCeiling'
actor=next((a for a in aas.get_all_level_actors() if a.get_actor_label()==label),None)
if not actor:actor=aas.spawn_actor_from_class(u.RectLight,u.Vector(-208,320,650))
actor.set_actor_rotation(u.Rotator(pitch=-90,yaw=90,roll=0),False)
actor.set_actor_label(label);actor.set_folder_path('ClientHome/Linear/Lighting')
light=actor.get_component_by_class(u.RectLightComponent)
light.set_mobility(u.ComponentMobility.MOVABLE)
light.set_editor_property('intensity_units',u.LightUnits.LUMENS)
light.set_intensity(8000.)
light.set_light_color(u.LinearColor(1,1,1,1))
light.set_editor_property('use_temperature',True);light.set_editor_property('temperature',4800.)
light.set_editor_property('source_width',3600.);light.set_editor_property('source_height',900.)
light.set_editor_property('attenuation_radius',5000.)
light.set_editor_property('indirect_lighting_intensity',1.)
light.set_editor_property('cast_shadows',True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(out/'lighting_changes.json').write_text(json.dumps(changes,indent=2))
