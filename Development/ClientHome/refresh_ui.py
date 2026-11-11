"""Refresh only owned UI assets, preserving current gameplay and scene."""
import unreal as u, runpy
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B, _BlueprintCache
import toolset_registry
out=Path(__file__).parent
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
lang=u.InternationalizationLibrary.get_current_language()
try:
    u.InternationalizationLibrary.set_current_language('en',False)
    with toolset_registry.tool_raising_exceptions():
        # Build popup separately before this HUD-only refresh.
        hud=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_HUD_Minimal')
        _BlueprintCache.invalidate(hud)
        graph=B.get_graph(hud,'EventGraph')
        code=(out/'BP_CH_Minimal_HUD.dsl').read_text(encoding='utf-8')
        code=code[:code.index('(event EventReceiveDrawHUD')]+runpy.run_path(str(out/'minimal_hud_layout.py'))['make_hud'](graph,B)
        B.write_graph_dsl(graph,code)
        B.compile_blueprint(hud,True)
        assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(hud)
        (out/'BP_CH_Minimal_HUD.dsl').write_text(code,encoding='utf-8')
        u.log('CLIENT_HOME_UI_REFRESH_OK')
finally:u.InternationalizationLibrary.set_current_language(lang,False)
