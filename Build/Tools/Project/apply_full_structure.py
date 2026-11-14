"""Apply the reviewed whole-project mapping through Unreal AssetTools only."""
import unreal as u
import json
import traceback
from pathlib import Path

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
out = root / 'Outputs/Organization20261113'
mapping = json.loads((out / 'AssetMoves.json').read_text())
baseline = json.loads((out / 'Baseline.json').read_text(encoding='utf-8'))
classes = {x['path']: x['class'] for x in baseline['assets']}
report = {'batches': [], 'maps': []}
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
tools = u.AssetToolsHelpers.get_asset_tools()

def save_dirty():
    packages = u.EditorLoadingAndSavingUtils.get_dirty_content_packages() + u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    # Some engine operations retain dirty old objects until consolidation. Never
    # re-save those obsolete copies over a successfully saved destination.
    packages = [p for p in packages if not (p.get_name() in mapping and assets.does_asset_exist(mapping[p.get_name()]))]
    if packages: assert u.EditorLoadingAndSavingUtils.save_packages(packages, False)

try:
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    save_dirty()
    nonmaps = [(a,b) for a,b in mapping.items() if classes[a] != 'World' and not assets.does_asset_exist(b)]
    for offset in range(0, len(nonmaps), 40):
        batch = nonmaps[offset:offset+40]
        renames = []
        for old,new in batch:
            assert not assets.does_asset_exist(new), new
            obj = u.load_asset(old)
            assert obj, old
            folder,name = new.rsplit('/',1)
            renames.append(u.AssetRenameData(obj, folder, name))
        assert tools.rename_assets(renames), batch
        save_dirty()
        report['batches'].append([a for a,b in batch])
        (out/'Migration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
    for old,new in mapping.items():
        if classes[old] != 'World': continue
        if assets.does_asset_exist(new):
            report['maps'].append({'old':old,'new':new,'resumed':True})
            continue
        assert levels.load_level(old)
        world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
        folder,name = new.rsplit('/',1)
        assert tools.rename_assets([u.AssetRenameData(world,folder,name)]), old
        # World::Rename re-externalizes actors/objects; save ALL dirty packages.
        save_dirty()
        assert assets.save_loaded_asset(world,False)
        report['maps'].append({'old':old,'new':new})
    # Save every affected map and its external packages, including unmoved maps.
    for old in baseline['maps']:
        target = mapping.get(old,old)
        assert levels.load_level(target)
        assert levels.save_current_level()
        save_dirty()
    report['success'] = True
except Exception:
    report['success'] = False
    report['error'] = traceback.format_exc()
finally:
    (out/'Migration.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
