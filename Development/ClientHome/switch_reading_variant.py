"""Switch the two reading arrangements; also supports a temporary PIE preview."""
import unreal as u

def run(variant='B',save=True):
 assert variant in ('A','B')
 editor=u.get_editor_subsystem(u.UnrealEditorSubsystem);world=editor.get_game_world()
 actors=u.GameplayStatics.get_all_actors_of_class(world,u.Actor) if world else u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
 counts={'A':0,'B':0}
 for a in actors:
  for v in ('A','B'):
   if a.actor_has_tag('CH_Reading_'+v):
    active=v==variant;a.set_actor_hidden_in_game(not active)
    if not world:a.set_is_temporarily_hidden_in_editor(not active)
    a.set_actor_enable_collision(active and a.actor_has_tag('CH_FurnitureCollision'));counts[v]+=1
 assert all(counts.values()),counts
 if save and not world:assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
 u.log('READING_VARIANT_'+variant+': '+str(counts))
if __name__=='__main__':run()
