import unreal as u,json
actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
rows=json.loads((_linear_root/'kitchen_tight_result.json').read_text())
changed=[]
for r in rows:
 a=actors[r['label']]
 if not str(a.get_folder_path()).endswith('/Dining'):continue
 x,y,z=r['location'];a.set_actor_location(u.Vector(x+70,y-90,z),False,True);changed.append(r['label'])
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'dining_nudge_result.json').write_text(json.dumps({'offset':[70,-90,0],'actors':changed,'saved':True},indent=2))
