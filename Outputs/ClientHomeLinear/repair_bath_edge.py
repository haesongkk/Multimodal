import unreal as u,json
aas=u.get_editor_subsystem(u.EditorActorSubsystem);actors={a.get_actor_label():a for a in aas.get_all_level_actors()}
for label in ['CH_Linear_BathHouseFacingRight','CH_Linear_BathHouseFacingLeft']:
 if label in actors:aas.destroy_actor(actors[label])
for r in json.loads((_linear_root/'bath_jamb_before.json').read_text()):
 a=actors[r['label']];a.set_actor_location(u.Vector(*r['loc']),False,True);a.set_actor_scale3d(u.Vector(*r['scale']))
# Recess bathroom side walls behind the existing house wall, retaining its original silhouette and UVs.
for label,a in actors.items():
 if label.startswith(('CH_SmallBath_Left','CH_SmallBath_RightBack')):
  p=a.get_actor_location();p.y=850;a.set_actor_location(p,False,True)
  s=a.get_actor_scale3d();s.y=2.82 if label.endswith('Trim') else 2.8;a.set_actor_scale3d(s)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
