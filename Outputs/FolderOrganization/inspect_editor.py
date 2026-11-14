import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir())
output = root / 'Outputs' / 'FolderOrganization'
registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = []
for data in registry.get_assets_by_path('/Game', recursive=True):
    package = str(data.package_name)
    if '/__External' in package:
        continue
    assets.append({'path': package, 'class': str(data.asset_class_path.asset_name)})
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
result = {
    'project': str(root),
    'current_world': world.get_path_name(),
    'actor_count': len(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()),
    'assets': assets,
    'api_docs': {
        'rename_assets': unreal.AssetTools.rename_assets.__doc__,
        'fixup_referencers': getattr(unreal.AssetTools, 'fixup_referencers', None).__doc__,
        'save_dirty_packages': unreal.EditorLoadingAndSavingUtils.save_dirty_packages.__doc__,
        'rename_asset': unreal.EditorAssetSubsystem.rename_asset.__doc__,
    }
}
(output / 'inventory_before.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
unreal.log('FOLDER_ORGANIZE_INVENTORY_READY')
