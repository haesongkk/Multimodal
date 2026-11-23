import unreal as u,json
actors={a.get_actor_label():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
rows=json.loads((_linear_root/'bath_jamb_before.json').read_text())
for r in rows:
 a=actors[r['label']];factor=(r['hi']-r['lo']+25)/(r['hi']-r['lo']);anchor=r['lo'] if r['label'].endswith('LeftA') else r['hi']
 x,y,z=r['loc'];sx,sy,sz=r['scale']
 a.set_actor_scale3d(u.Vector(sx*factor,sy,sz));a.set_actor_location(u.Vector(anchor+(x-anchor)*factor,y,z),False,True)
a=actors['CH_Cozy_HallRunner'];p=a.get_actor_location();p.y=577.5;a.set_actor_location(p,False,True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
