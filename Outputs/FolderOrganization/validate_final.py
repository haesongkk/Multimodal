import json
from pathlib import Path
import unreal

root = Path(unreal.Paths.project_dir()).resolve()
assert root.name == 'Multimodal'
out = root / 'Outputs' / 'FolderOrganization'
plan = json.loads((out / 'move_manifest.json').read_text(encoding='utf-8'))
baseline = json.loads((out / 'map_baseline.json').read_text(encoding='utf-8'))
registry = unreal.AssetRegistryHelpers.get_asset_registry()
eas = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
removed_folders = []
for folder in ['Characters','CocoDetective','Cursor','Level','LevelPrototyping','TopDown']:
    disk = root / 'Content' / folder
    virtual = '/Game/' + folder
    assert not list(disk.rglob('*.*')) if disk.exists() else True, 'Folder not empty: ' + folder
    assert not registry.get_assets_by_path(virtual, recursive=True), 'Registry still has assets: ' + folder
    if disk.exists():
        assert eas.delete_directory(virtual), virtual
        removed_folders.append(folder)

all_assets = registry.get_assets_by_path('/Game', recursive=True)
redirectors = [str(a.package_name) for a in all_assets if str(a.asset_class_path.asset_name)=='ObjectRedirector']
assert not redirectors, redirectors
missing_destinations = [r['destination'] for r in plan if not eas.does_asset_exist(r['destination'])]
assert not missing_destinations, missing_destinations
blueprints = []
for row in plan:
    if row['class'] != 'Blueprint':
        continue
    bp = unreal.load_asset(row['destination'])
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    state = str(bp.get_editor_property('status'))
    assert 'ERROR' not in state.upper(), (row['destination'], state)
    blueprints.append({'path':row['destination'], 'status':state})

maps = []
for row in plan:
    if row['class'] != 'World':
        continue
    assert les.load_level(row['destination']), row['destination']
    current_actors = actors.get_all_level_actors()
    labels = sorted(a.get_actor_label() for a in current_actors)
    assert labels == baseline[row['path']]['labels'], row['destination']
    missing_meshes = []
    for actor in current_actors:
        for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
            if comp.get_editor_property('static_mesh') is None:
                missing_meshes.append(actor.get_actor_label())
    maps.append({'path':row['destination'], 'actor_count':len(labels), 'labels_match':True, 'empty_static_mesh_components':missing_meshes})
    assert les.save_current_level()
assert les.load_level('/Game/Multimodal/01_Maps/Alley/LV_Alley_Proto')
assert unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
result = {'destinations_present':len(plan), 'remaining_redirectors':redirectors, 'removed_empty_folders':removed_folders, 'blueprints':blueprints, 'maps':maps, 'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()], 'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
(out/'validation_final.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
unreal.log('FOLDER_ORGANIZE_FINAL_VALIDATION_DONE')
