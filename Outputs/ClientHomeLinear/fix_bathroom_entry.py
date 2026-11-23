import unreal as u,json
rows=json.loads((_linear_root/'compact_before.json').read_text());actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
removed=['CH_SmallBath_DoorFrame','CH_SmallBath_DoorLintel','CH_SmallBath_OpenDoor','CH_SmallBath_RightFrontTile','CH_SmallBath_RightFrontUpper','CH_SmallBath_RightFrontTrim']
changes=[]
for r in rows:
 if not r['folder'].endswith('/Bathroom'):continue
 a=actors[r['name']];label=r['label'];x,y,z=r['loc'];sx,sy,sz=r['scale']
 if label in removed:
  a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False);continue
 x-=28.5;y+=120
 if label=='CH_SmallBath_TileFloor':x=540.55;sx=3.781
 elif label.startswith('CH_SmallBath_Back'):x=540.55;sx=(3.921 if label.endswith('Trim') else 3.901)
 elif label.startswith('CH_SmallBath_Left'):x=729.6
 elif label.startswith('CH_SmallBath_RightBack'):x=351.5;y=830;sy=(3.22 if label.endswith('Trim') else 3.2)
 a.set_actor_location(u.Vector(x,y,z),False,True);a.set_actor_scale3d(u.Vector(sx,sy,sz))
 changes.append({'label':label,'location':[x,y,z]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'bathroom_entry_result.json').write_text(json.dumps({'removed':removed,'changes':changes},indent=2))
