"""Switch the running Unreal editor to either saved comparison map and play it."""
import sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Outputs/ClientHomeLinear'))
from mcp_client import call
style=sys.argv[1] if len(sys.argv)>1 else 'Storybook'
if style not in ('Original','Storybook'):raise SystemExit('Use Original or Storybook')
call('call_tool',{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StopPIE','arguments':{}})
bridge=ROOT/'Outputs/ClientHomeLinear';done=ROOT/'Outputs/ClientHomeStyles/preview_ready.txt'
token=str(time.time_ns())
job="import unreal as u,gc\nfrom pathlib import Path\ngc.collect();u.SystemLibrary.collect_garbage()\nassert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_"+style+"')\nPath("+repr(str(done))+ ").write_text("+repr(token)+")\n"
(bridge/'job.py').write_text(job,encoding='utf-8')
for _ in range(120):
 if done.exists() and done.read_text()==token:break
 time.sleep(.5)
else:raise SystemExit('Map load did not finish; check job_status.txt in ClientHomeLinear.')
print(call('call_tool',{'toolset_name':'EditorToolset.EditorAppToolset','tool_name':'StartPIE','arguments':{'options':{'bSimulate':False,'playMode':'PlayMode_InEditorFloating','warmupSeconds':0}}}))
