import unreal as u
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label().startswith(('CH_SmallBath_Left','CH_SmallBath_RightBack')):
  c=a.get_component_by_class(u.StaticMeshComponent)
  mat=u.load_asset('/Game/ExternalAssets/StylizedKitchen/Materials/MI_Wallpaper_A')
  for i in range(c.get_num_materials()):c.set_material(i,mat)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
