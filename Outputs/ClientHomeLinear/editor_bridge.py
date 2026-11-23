import unreal, pathlib, traceback
unreal.EditorPythonScripting.set_keep_python_script_alive(True)
_linear_root = pathlib.Path('D:/Multimodal/Outputs/ClientHomeLinear')
_linear_seen = 0
def _linear_tick(dt):
    global _linear_seen
    p = _linear_root / 'job.py'
    if not p.exists(): return
    stamp = p.stat().st_mtime_ns
    if stamp == _linear_seen: return
    _linear_seen = stamp
    try:
        scope={'unreal':unreal,'_linear_root':_linear_root}
        exec(compile(p.read_text(encoding='utf-8'), str(p), 'exec'), scope)
        (_linear_root/'job_status.txt').write_text('OK '+str(stamp),encoding='utf-8')
    except Exception:
        (_linear_root/'job_status.txt').write_text(traceback.format_exc(),encoding='utf-8')
_linear_handle = unreal.register_slate_post_tick_callback(_linear_tick)
unreal.log('CLIENT_HOME_LINEAR_BRIDGE_READY')
