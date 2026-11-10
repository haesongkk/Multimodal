"""Check the deleted extension has no furnishings/floor and the new boundary blocks entry."""
import unreal as u,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();p=u.GameplayStatics.get_player_pawn(w,0)
def blocked(a,b):return bool(u.SystemLibrary.line_trace_single(w,u.Vector(*a),u.Vector(*b),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],u.DrawDebugTrace.NONE,True))
actors={a.get_actor_label():a for a in u.GameplayStatics.get_all_actors_of_class(w,u.Actor)}
checks={'old room has no floor':not blocked((0,-900,150),(0,-900,-30)), 'old room has no wall':not blocked((-600,-900,150),(150,-900,150)), 'entrance end is closed':blocked((301,-450,110),(301,-700,110)), 'kitchen partition remains open':not blocked((-300,-260,110),(-90,-260,110)), 'bathroom furniture hidden':all(actors[n].get_editor_property('hidden') and not actors[n].get_actor_enable_collision() for n in ['Bathroom_Bathtub','Bathroom_Sink','Toilet','Door_Frame_A'])}
Path('D:/Multimodal/Saved/ClientHome/no-bathroom-boundary-test.json').write_text(json.dumps(checks,indent=2))
assert all(checks.values()),checks
u.log('NO_BATHROOM_BOUNDARY_OK')
