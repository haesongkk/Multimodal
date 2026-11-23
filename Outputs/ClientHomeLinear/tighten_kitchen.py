import unreal as u,json
rows=json.loads((_linear_root/'kitchen_tight_before.json').read_text())
actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
changes=[]
for r in rows:
 a=actors[r['name']];label=r['label']
 dx=-12 if label.startswith('Fridge_') else (-350 if str(a.get_folder_path()).endswith('/Dining') and label!='RectLight' else 0)
 if not dx:continue
 x,y,z=r['loc'];a.set_actor_location(u.Vector(x+dx,y,z),False,True)
 changes.append({'label':label,'location':[x+dx,y,z]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'kitchen_tight_result.json').write_text(json.dumps(changes,indent=2))
