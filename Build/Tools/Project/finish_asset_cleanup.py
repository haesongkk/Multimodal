"""Finish a saved rename interrupted during old-package cleanup, using Unreal APIs."""
from pathlib import Path
import json
import traceback
import unreal as u

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
out = root / 'Outputs/Organization'
result = {}
try:
    mapping = json.loads((out / 'AssetMoves.json').read_text())
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
    prefixes = ('/Game/ClientHome_Haeso', '/Game/StylizedKitchen')
    remaining = [x for prefix in prefixes for x in registry.get_assets_by_path(prefix, recursive=True)]
    unexpected = []
    for row in remaining:
        path = str(row.package_name)
        assert path in mapping and assets.does_asset_exist(mapping[path]), path
        for ref in registry.get_referencers(path, u.AssetRegistryDependencyOptions(True, True, False, False, False)):
            if not str(ref).startswith(prefixes): unexpected.append((path, str(ref)))
    result['outside_referencers'] = unexpected
    assert not unexpected, unexpected
    result['before'] = len(remaining)
    allowed_remaining = {
        '/Game/StylizedKitchen/Materials/MM_Base_Mat_3',
        '/Game/StylizedKitchen/Meshes/SM_Walls_Trim',
    }
    assert {str(row.package_name) for row in remaining} <= allowed_remaining
    for row in remaining:
        if str(row.package_name) in allowed_remaining:
            path = str(row.package_name)
            target = u.load_asset(mapping[path])
            source = row.get_asset()
            assert target and source
            assets.consolidate_assets(target, [source])
            assets.save_loaded_asset(target, False)
    failures = []
    for path in sorted(allowed_remaining):
        if assets.does_asset_exist(path):
            assets.delete_asset(path)
        package_file = (root / 'Content' / path.removeprefix('/Game/')).with_suffix('.uasset')
        if package_file.exists(): failures.append(str(package_file))
    assert not failures, failures
    result['success'] = True
except Exception:
    result['success'] = False
    result['error'] = traceback.format_exc()
finally:
    (out / 'CleanupResult.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    u.log('ORGANIZATION_CLEANUP: ' + json.dumps(result, ensure_ascii=False))
