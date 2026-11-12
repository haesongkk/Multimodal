"""User-approved migration. Execute only inside the project's Unreal Editor."""
import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve()
assert root.name == 'Multimodal', str(root)
out = root / 'Outputs' / 'FolderOrganization'
plan = json.loads((out / 'move_manifest.json').read_text(encoding='utf-8'))
eas = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
registry = unreal.AssetRegistryHelpers.get_asset_registry()
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

# Preserve a baseline of every map before any reference changes.
baseline = {}
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
original_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split('.')[0]
for row in plan:
    if row['class'] != 'World':
        continue
    assert level_subsystem.load_level(row['path']), row['path']
    actors = actor_subsystem.get_all_level_actors()
    baseline[row['path']] = {'actor_count': len(actors), 'labels': sorted(a.get_actor_label() for a in actors)}
assert level_subsystem.load_level(original_world)
(out / 'map_baseline.json').write_text(json.dumps(baseline, indent=2), encoding='utf-8')

rows = [row for row in plan if row['class'] != 'World']
renames = []
for row in rows:
    assert not eas.does_asset_exist(row['destination']), 'Destination exists: ' + row['destination']
    asset = unreal.load_asset(row['path'])
    assert asset, 'Load failed: ' + row['path']
    folder, name = row['destination'].rsplit('/', 1)
    assert eas.does_directory_exist(folder) or eas.make_directory(folder), folder
    renames.append(unreal.AssetRenameData(asset=asset, new_package_path=folder, new_name=name))
success = unreal.AssetToolsHelpers.get_asset_tools().rename_assets(renames)
completed = [row for row in rows if eas.does_asset_exist(row['destination'])]
(out / 'result_nonmaps.json').write_text(json.dumps({'success': success, 'planned':len(rows), 'completed':len(completed)}, indent=2), encoding='utf-8')
assert success and len(completed) == len(rows), 'Migration incomplete; stop and inspect log'
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
unreal.log('FOLDER_ORGANIZE_NONMAPS_DONE ' + str(len(completed)))
