"""Consolidate only the exact nine leftover copies from the reviewed mapping."""
import unreal as u
import json
import traceback
from pathlib import Path
root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
out = root/'Outputs/Organization20261113'
mapping = json.loads((out/'AssetMoves.json').read_text())
verification = json.loads((out/'Verification.json').read_text(encoding='utf-8'))
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
report = {'consolidated':[]}
try:
    for row in verification['legacy_assets']:
        if row['class']=='ObjectRedirector': continue
        old = row['path']
        assert old in mapping and row['class'] != 'World'
        source = u.load_asset(old)
        target = u.load_asset(mapping[old])
        assert source and target and source.get_class()==target.get_class()
        if source.get_path_name()!=target.get_path_name():
            assert assets.consolidate_assets(target,[source]),old
            report['consolidated'].append(old)
    # Dependency traversal found this guide is used by the production town.
    # Keep its behavior and move it into production graphics instead of sandbox.
    original = '/Game/CocoDetective/Meshes/SM_TwoHeadScaleGuide'
    old = mapping[original]
    new = '/Game/Multimodal/03_Graphics/Meshes/Characters/Coco/SM_TwoHeadScaleGuide'
    obj=u.load_asset(old)
    assert obj
    folder,name=new.rsplit('/',1)
    assert u.AssetToolsHelpers.get_asset_tools().rename_assets([u.AssetRenameData(obj,folder,name)])
    assert assets.save_loaded_asset(obj,False)
    mapping[original]=new
    (out/'AssetMoves.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
    assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    report['success']=True
except Exception:
    report['success']=False
    report['error']=traceback.format_exc()
finally:
    (out/'Consolidation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
