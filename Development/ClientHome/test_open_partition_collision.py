import unreal as u,json
from pathlib import Path
w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
p=u.GameplayStatics.get_player_pawn(w,0)
def blocked(a,b):
 return bool(u.SystemLibrary.line_trace_single(w,u.Vector(*a),u.Vector(*b),u.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[p],u.DrawDebugTrace.NONE,True))
checks={'open crossing north':not blocked((-300,-260,110),(-90,-260,110)), 'open crossing south':not blocked((-300,-420,110),(-90,-420,110)), 'bathroom wall retained':blocked((-100,-450,110),(-100,-570,110)), 'exterior wall retained':blocked((650,600,110),(650,760,110))}
Path('D:/Multimodal/Saved/ClientHome/open-partition-collision-test.json').write_text(json.dumps(checks,indent=2))
assert all(checks.values()),checks
u.log('OPEN_PARTITION_COLLISION_OK')
