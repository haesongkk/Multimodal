import unreal as u,json
rows=json.loads((_linear_root/'study_before.json').read_text())
actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
changed=[]
for r in rows:
 a=actors[r['name']];x,y,z=r['loc'];pitch,yaw,roll=r['rot'];label=r['label']
 if r['folder'].endswith('/StudyReading'):
  if label in ['CH_Cozy_HallRunner','SphereReflectionCapture3']:continue
  x-=550
 elif r['folder'].endswith('/StudyDesk'):
  if label.startswith('CH_Minimal_Fur'):x-=400;y+=105
  else:
   x=-200-(x-200);y=610-(y-400);yaw+=180
   if label in ['CH_Cozy_CatPlantPot','CH_Cozy_CatPlantLeaves']:y=565
 else:continue
 a.set_actor_location(u.Vector(x,y,z),False,True)
 a.set_actor_rotation(u.Rotator(pitch=pitch,yaw=yaw,roll=roll),False)
 changed.append({'label':label,'location':[x,y,z]})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(_linear_root/'study_result.json').write_text(json.dumps(changed,indent=2))
