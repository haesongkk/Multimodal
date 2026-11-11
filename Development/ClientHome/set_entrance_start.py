"""Start inside the entrance below the refrigerator, facing into the home."""
import unreal as u
editor=u.get_editor_subsystem(u.UnrealEditorSubsystem)
assert not editor.get_game_world()
assert editor.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
starts=[a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.PlayerStart)]
assert len(starts)==1,len(starts)
starts[0].set_actor_location(u.Vector(-730,-238,114),False,False)
starts[0].set_actor_rotation(u.Rotator(pitch=0,yaw=0,roll=0),False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('ENTRANCE_PLAYER_START_SAVED')
