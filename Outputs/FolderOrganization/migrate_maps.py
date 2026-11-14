import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve()
assert root.name == 'Multimodal'
out = root / 'Outputs' / 'FolderOrganization'
plan = json.loads((out / 'move_manifest.json').read_text(encoding='utf-8'))
baseline = json.loads((out / 'map_baseline.json').read_text(encoding='utf-8'))
eas = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
results = []
for row in [r for r in plan if r['class'] == 'World']:
    already_moved = eas.does_asset_exist(row['destination'])
    assert les.load_level(row['destination'] if already_moved else row['path']), row['path']
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    labels_before = sorted(a.get_actor_label() for a in actors.get_all_level_actors())
    assert labels_before == baseline[row['path']]['labels'], 'Baseline mismatch: ' + row['path']
    folder, name = row['destination'].rsplit('/', 1)
    assert eas.does_directory_exist(folder) or eas.make_directory(folder)
    if not already_moved:
        assert tools.rename_assets([unreal.AssetRenameData(asset=world, new_package_path=folder, new_name=name)]), row['path']
    assert les.save_current_level(), row['destination']
    labels_after = sorted(a.get_actor_label() for a in actors.get_all_level_actors())
    assert labels_after == labels_before, 'Actor mismatch: ' + row['destination']
    results.append({'old':row['path'], 'new':row['destination'], 'actor_count':len(labels_after), 'labels_match':True})
    (out / 'result_maps.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
assert les.load_level('/Game/Multimodal/01_Maps/Alley/LV_Alley_Proto')
unreal.log('FOLDER_ORGANIZE_MAPS_DONE ' + str(len(results)))
