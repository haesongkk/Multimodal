"""Replace stale pre-migration template instances with their migrated equivalents."""
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve()
assert root.name == 'Multimodal'
out = root / 'Outputs' / 'FolderOrganization'
plan = json.loads((out / 'repair_candidates_verified.json').read_text(encoding='utf-8-sig'))
assert len(plan) == 22
assert all(row['unchanged_from_backup'] and row['destination_exists'] for row in plan)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
eas = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
fixed = []
for row in plan:
    if row['class'] == 'World':
        continue
    data = registry.get_asset_by_object_path(row['path'] + '.' + row['path'].rsplit('/',1)[-1])
    if not data.is_valid() or str(data.asset_class_path.asset_name) == 'ObjectRedirector':
        continue
    source = unreal.find_object(None, row['path'] + '.' + row['path'].rsplit('/',1)[-1])
    destination = unreal.load_asset(row['destination'])
    assert source and destination and source != destination, row['path']
    assert source.get_class() == destination.get_class(), row['path']
    assert eas.save_loaded_asset(destination, only_if_is_dirty=False), row['destination']
    assert eas.consolidate_assets(destination, [source]), row['path']
    fixed.append(row['path'])
    (out / 'repair_result.json').write_text(json.dumps(fixed, indent=2), encoding='utf-8')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log('FOLDER_ORGANIZE_DUPLICATES_REPAIRED ' + str(len(fixed)))
