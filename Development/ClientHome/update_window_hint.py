import unreal as u,runpy
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
root=Path('D:/Multimodal/Development/ClientHome')
p=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_HUD_Minimal')
lang=u.InternationalizationLibrary.get_current_language()
u.InternationalizationLibrary.set_current_language('en',False)
try:
 _BlueprintCache.invalidate(p)
 g=B.get_graph(p,'EventGraph')
 code=(root/'BP_CH_Minimal_HUD.dsl').read_text(encoding='utf-8')
 code=code[:code.index('(event EventReceiveDrawHUD')]+runpy.run_path(str(root/'minimal_hud_layout.py'))['make_hud'](g,B)
 B.write_graph_dsl(g,code)
 B.compile_blueprint(p,True)
 assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(p,False)
 (root/'BP_CH_Minimal_HUD.dsl').write_text(code,encoding='utf-8')
 u.log('WINDOW_HINT_MOVED_SAVED')
finally:u.InternationalizationLibrary.set_current_language(lang,False)
