import unreal as u,json
rows=json.loads((_linear_root/'study_result.json').read_text())
actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
changes=[]
for r in rows:
 a=actors[r['label']];folder=str(a.get_folder_path())
 dx=150 if folder.endswith('/StudyReading') else 200
 x,y,z=r['location'];a.set_actor_location(u.Vector(x+dx,y,z),False,True)
 changes.append({'label':r['label'],'location':[x+dx,y,z]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'study_spacing_result.json').write_text(json.dumps(changes,indent=2))
