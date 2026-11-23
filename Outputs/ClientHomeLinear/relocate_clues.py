import unreal as u,json
actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()};changes=[]
for r in json.loads((_linear_root/'clue_relocation_before.json').read_text()):
 label=r['label'];x,y,z=r['loc'];a=actors[r['name']]
 if label.startswith('CH_Minimal_Pawprint'):
  x+=290;y+=135;z=23.8
 elif label.startswith('CH_Minimal_Fur'):
  x+=420;y+=345;a.set_folder_path('ClientHome/Linear/Bathroom')
 else:continue
 a.set_actor_location(u.Vector(x,y,z),False,True);changes.append({'label':label,'location':[x,y,z],'tags':[str(t) for t in a.tags]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'clue_relocation_result.json').write_text(json.dumps(changes,indent=2))
