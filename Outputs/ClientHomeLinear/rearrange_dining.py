import unreal as u,json
rows=json.loads((_linear_root/'dining_before.json').read_text())
actors={a.get_name():a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()}
assert 'LV_ClientHome_Linear.' in u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()
for r in rows:
 if r['label']=='RectLight':continue
 fridge=r['label'].startswith('Fridge_')
 cx,cy=(-1130.133,578.932) if fridge else (-753.522,381.722)
 tx,ty=(cx,cy) if fridge else (cx-300,cy-50)
 x,y,z=r['loc'];pitch,yaw,roll=r['rot'];a=actors[r['name']]
 a.set_actor_location(u.Vector(tx+y-cy,ty-(x-cx),z),False,True)
 a.set_actor_rotation(u.Rotator(pitch=pitch,yaw=yaw-90,roll=roll),False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
