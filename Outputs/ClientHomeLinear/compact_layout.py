import unreal as u,json
rows=json.loads((_linear_root/'compact_before.json').read_text())
actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
changes=[]
for r in rows:
 a=actors[r['name']];f=r['folder'];label=r['label'];x,y,z=r['loc'];sx,sy,sz=r['scale']
 if f.endswith('/Architecture'):
  assert abs(r['rot'][1])<.01,(label,r['rot'])
  x*=.95;a.set_actor_scale3d(u.Vector(sx*.95,sy,sz))
 elif label=='CH_Cozy_HallRunner':x=539.;y=430.
 elif f.endswith(('/Kitchen','/Dining','/Entry')) or 'Exit' in label:x+=91.5
 elif f.endswith('/Living'):x-=70.75
 elif f.endswith('/Bathroom'):x-=28.5
 elif f.endswith('/StudyReading'):x+=65
 elif f.endswith('/StudyDesk'):pass
 else:continue
 a.set_actor_location(u.Vector(x,y,z),False,True)
 changes.append({'label':label,'location':[x,y,z]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'compact_result.json').write_text(json.dumps(changes,indent=2))
