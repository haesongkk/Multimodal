"""Compile and validate the organized Blueprint project inside Unreal Editor."""
import json
import traceback
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.blueprint import BlueprintTools

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
out = root / 'Outputs/Organization'
report = {'compiled': [], 'maps': [], 'missing': [], 'sandbox_references': []}
try:
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
    levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
    report['source_files_updated'] = []
    for source in (root / 'SourceAssets/ExternalAssets/StylizedKitchen').rglob('*'):
        if not source.is_file(): continue
        package = '/Game/' + source.relative_to(root / 'SourceAssets').with_suffix('').as_posix()
        if not assets.does_asset_exist(package): continue
        imported = u.load_asset(package)
        imported.get_editor_property('asset_import_data').scripted_add_filename(str(source), 0, '')
        assert assets.save_loaded_asset(imported, False)
        report['source_files_updated'].append(package)
    for name, filename in {'T_DetectivePortrait': 'detective-portrait.png', 'T_PawStamp': 'paw-stamp.png', 'T_StitchedPanel': 'stitched-panel.png'}.items():
        texture = u.load_asset('/Game/Multimodal/04_UI/Textures/ClientHome/' + name)
        texture.get_editor_property('asset_import_data').scripted_add_filename(str(root / 'SourceAssets/ClientHome/UIArt' / filename), 0, '')
        assert assets.save_loaded_asset(texture, False)
    face = u.load_asset('/Game/Multimodal/04_UI/Fonts/ClientHome/FF_Jua')
    face.set_editor_property('source_filename', str(root / 'SourceAssets/ClientHome/UIArt/Jua-Regular.ttf'))
    assert assets.save_loaded_asset(face, False)
    for row in registry.get_assets_by_path('/Game/Multimodal', recursive=True):
        if str(row.asset_class_path.asset_name) in ('Blueprint', 'WidgetBlueprint', 'AnimBlueprint'):
            bp = row.get_asset()
            BlueprintTools.compile_blueprint(bp)
            assert assets.save_loaded_asset(bp, False)
            report['compiled'].append(str(row.package_name))
    for map_path in ('/Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_Blockout', '/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal'):
        assert levels.load_level(map_path), map_path
        report['maps'].append(map_path)
    seen = set()
    queue = ['/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal']
    options = u.AssetRegistryDependencyOptions(True, True, False, False, False)
    while queue:
        path = queue.pop()
        if path in seen: continue
        seen.add(path)
        if path.startswith('/Script/'): continue
        if path.startswith('/Game/') and not assets.does_asset_exist(path): report['missing'].append(path)
        if path.startswith('/Game/Multimodal/90_Sandbox/'): report['sandbox_references'].append(path)
        queue.extend(str(x) for x in registry.get_dependencies(path, options))
    report['dependency_count'] = len(seen)
    report['legacy_dependencies'] = sorted(p for p in seen if p.startswith(('/Game/ClientHome_Haeso/', '/Game/StylizedKitchen/')))
    report['legacy_assets'] = [{'path': str(x.package_name), 'class': str(x.asset_class_path.asset_name)} for prefix in ('/Game/ClientHome_Haeso', '/Game/StylizedKitchen') for x in registry.get_assets_by_path(prefix, recursive=True)]
    report['redirectors'] = [str(x.package_name) for prefix in ('/Game/ClientHome_Haeso', '/Game/StylizedKitchen') for x in registry.get_assets_by_path(prefix, recursive=True) if str(x.asset_class_path.asset_name) == 'ObjectRedirector']
    report['success'] = not report['missing'] and not report['sandbox_references'] and not report['redirectors'] and not report['legacy_dependencies']
except Exception:
    report['success'] = False
    report['error'] = traceback.format_exc()
finally:
    (out / 'Verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    u.log('ORGANIZATION_VERIFICATION: ' + json.dumps(report, ensure_ascii=False))
