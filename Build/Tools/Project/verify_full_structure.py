"""Verify all maps and references against the full pre-migration snapshot."""
import unreal as u
import json
import re
import traceback
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from full_structure_audit import snapshot
from editor_toolset.toolsets.blueprint import BlueprintTools

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
out = root/'Outputs/Organization20261113'
mapping = json.loads((out/'AssetMoves.json').read_text())
baseline = json.loads((out/'Baseline.json').read_text(encoding='utf-8'))
report = {'compiled': [], 'maps': {}, 'map_differences': {}, 'missing': [], 'legacy_references': [], 'sandbox_references': [], 'source_metadata_updated': []}
old_roots = ('/Game/Characters/', '/Game/CocoDetective/', '/Game/Cursor/', '/Game/LevelPrototyping/', '/Game/TopDown/')

def normalized(value, remap=False):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if remap:
        for old,new in sorted(mapping.items(),key=lambda p:-len(p[0])):
            text = text.replace(old+'.'+old.rsplit('/',1)[-1],new+'.'+new.rsplit('/',1)[-1]).replace(old,new)
    return re.sub(r'0x[0-9A-Fa-f]+', 'ADDRESS', text)

try:
    assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
    registry = u.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    levels = u.get_editor_subsystem(u.LevelEditorSubsystem)
    rows = registry.get_assets_by_path('/Game',recursive=True)
    # Preserve the source-art files and repair only source paths actually matched.
    sources = {}
    for p in (root/'SourceAssets/ExternalAssets/StylizedKitchen').rglob('*'):
        if p.is_file(): sources.setdefault(p.name.lower(),[]).append(p)
    for row in rows:
        path = str(row.package_name)
        cls = str(row.asset_class_path.asset_name)
        if cls in ('Blueprint','WidgetBlueprint','AnimBlueprint') and not path.startswith(old_roots):
            bp = row.get_asset()
            BlueprintTools.compile_blueprint(bp)
            assert assets.save_loaded_asset(bp,False)
            report['compiled'].append(path)
        if path.startswith('/Game/ExternalAssets/StylizedKitchen/') and cls in ('StaticMesh','Texture2D'):
            obj = row.get_asset()
            data = obj.get_editor_property('asset_import_data')
            if not data: continue
            changed = False
            for index, filename in enumerate(data.extract_filenames()):
                matches = sources.get(filename.replace('\\','/').rsplit('/',1)[-1].lower(),[])
                if len(matches) == 1 and Path(filename) != matches[0]:
                    data.scripted_add_filename(str(matches[0]),index,'')
                    changed = True
            if changed:
                assert assets.save_loaded_asset(obj,False)
                report['source_metadata_updated'].append(path)
    options = u.AssetRegistryDependencyOptions(True,True,False,False,False)
    all_seen = set()
    for old, expected in baseline['maps'].items():
        new = mapping.get(old,old)
        assert levels.load_level(new),new
        actual = snapshot()
        report['maps'][new] = {'before_count':len(expected),'after_count':len(actual),'unchanged':normalized(expected,True)==normalized(actual)}
        if not report['maps'][new]['unchanged']:
            before = {a['name']:a for a in expected}
            after = {a['name']:a for a in actual}
            report['map_differences'][new] = {name:{'before':before.get(name),'after':after.get(name)} for name in before.keys()|after.keys() if normalized(before.get(name),True)!=normalized(after.get(name))}
        seeds = [new]
        # External actors may not be ordinary World registry dependencies.
        for row in rows:
            p=str(row.package_name)
            if p.startswith('/Game/__ExternalActors__/'+new[6:]+'/') or p.startswith('/Game/__ExternalObjects__/'+new[6:]+'/'):seeds.append(p)
        seen=set()
        while seeds:
            p=seeds.pop()
            if p in seen or p.startswith('/Script/'):continue
            seen.add(p)
            # External actor/object packages contain subobjects, not ordinary
            # top-level assets. Check the package file for those engine paths.
            exists = assets.does_asset_exist(p)
            if p.startswith(('/Game/__ExternalActors__/','/Game/__ExternalObjects__/')):
                exists = (root/'Content'/(p[6:]+'.uasset')).is_file()
            if p.startswith('/Game/') and not exists:report['missing'].append([new,p])
            if p.startswith(old_roots):report['legacy_references'].append([new,p])
            if '/01_Maps/' in new and p.startswith('/Game/Multimodal/90_Sandbox/'):report['sandbox_references'].append([new,p])
            seeds.extend(str(v) for v in registry.get_dependencies(p,options))
        all_seen.update(seen)
    report['dependency_count']=len(all_seen)
    report['legacy_assets']=[{'path':str(x.package_name),'class':str(x.asset_class_path.asset_name)} for x in rows if str(x.package_name).startswith(old_roots)]
    report['redirectors']=[str(x.package_name) for x in rows if str(x.asset_class_path.asset_name)=='ObjectRedirector']
    report['success']=not any(report[k] for k in ('map_differences','missing','legacy_references','sandbox_references','legacy_assets','redirectors'))
except Exception:
    report['success']=False
    report['error']=traceback.format_exc()
finally:
    (out/'Verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    u.log('FULL_STRUCTURE_VERIFY: '+str(report.get('success')))
