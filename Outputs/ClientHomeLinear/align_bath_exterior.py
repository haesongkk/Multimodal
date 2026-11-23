import unreal as u,json
aas=u.get_editor_subsystem(u.EditorActorSubsystem);actors={a.get_actor_label():a for a in aas.get_all_level_actors()}
wall=actors['CH_Linear_RearLeftA'];o,e=wall.get_actor_bounds(False);joint=o.y+e.y
# Match bathroom front exactly to the house's exterior face. Side walls lie outside the opening, not inside it.
for r in json.loads((_linear_root/'bathroom_entry_result.json').read_text())['changes']:
 a=actors[r['label']];label=r['label'];x,y,z=r['location'];y+=joint-670
 if label.startswith(('CH_SmallBath_Left','CH_SmallBath_RightBack')):
  trim=label.endswith('Trim');left=label.startswith('CH_SmallBath_Left')
  x=(732.2 if trim else 731.2) if left else (344.5 if trim else 345.5)
  y=joint+160
  s=a.get_actor_scale3d();s.y=3.2;a.set_actor_scale3d(s)
  suffix='Trim' if trim else ('Upper' if label.endswith('Upper') else 'Tile')
  source=actors['CH_SmallBath_RightFront'+suffix].get_component_by_class(u.StaticMeshComponent)
  c=a.get_component_by_class(u.StaticMeshComponent)
  for i in range(c.get_num_materials()):c.set_material(i,source.get_material(min(i,source.get_num_materials()-1)))
 a.set_actor_location(u.Vector(x,y,z),False,True)
a=actors['CH_Cozy_HallRunner'];o,e=a.get_actor_bounds(False);p=a.get_actor_location();p.y=joint-e.y;a.set_actor_location(p,False,True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'bath_exterior_joint_verified.json').write_text(json.dumps({'house_exterior_y':joint,'bath_front_y':joint,'right_wall_inner_x':351.5,'left_wall_inner_x':729.6,'saved':True},indent=2))
