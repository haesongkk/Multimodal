import unreal as u,runpy
from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
from editor_toolset.toolsets.actor import ActorTools as A
p=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_Player_Minimal')
old=u.InternationalizationLibrary.get_current_language()
u.InternationalizationLibrary.set_current_language('en',False)
try:
 _BlueprintCache.invalidate(p)
 runpy.run_path('D:/Multimodal/Development/ClientHome/minimal_follow_camera.py')['configure'](p,B,A)
 assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(p)
 u.log('COMPACT_CAMERA_SAVED')
finally:u.InternationalizationLibrary.set_current_language(old,False)
