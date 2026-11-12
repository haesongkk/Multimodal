import json
from pathlib import Path
import unreal
root = Path(unreal.Paths.project_dir()).resolve()
out = root / 'Outputs' / 'FolderOrganization'
registry = unreal.AssetRegistryHelpers.get_asset_registry()
data = []
for ad in registry.get_assets_by_path('/Game', recursive=True):
    p = str(ad.package_name)
    if '/__External' in p:
        continue
    data.append({'path':p, 'class':str(ad.asset_class_path.asset_name)})
samples = {}
for p in ['/Game/Characters/Mannequins/Materials/Manny/MI_Manny_01_New','/Game/ExternalAssets/UnrealTemplates/Characters/Mannequins/Materials/Manny/MI_Manny_01_New']:
    obj = unreal.find_object(None, p + '.' + p.rsplit('/',1)[-1])
    samples[p] = {'loaded_class':obj.get_class().get_name() if obj else None, 'loaded_path':obj.get_path_name() if obj else None}
result = {'assets':data, 'samples':samples, 'dirty_maps':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()], 'dirty_content':[p.get_path_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}
(out/'inventory_after_partial.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
unreal.log('FOLDER_ORGANIZE_INSPECTION_DONE')
