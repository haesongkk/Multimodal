import unreal as u, json
from pathlib import Path
r=u.AssetRegistryHelpers.get_asset_registry()
assets=r.get_assets_by_path('/Game/ClientHome_Haeso',recursive=True)
report={'world':u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name(),'assets':[{'path':str(a.package_name),'class':str(a.asset_class_path.asset_name)} for a in assets],'dirty':[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]+[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'asset_tools':[x for x in dir(u.AssetToolsHelpers.get_asset_tools()) if 'fix' in x or 'rename' in x]}
Path('D:/Multimodal/Outputs/Organization/Before.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
