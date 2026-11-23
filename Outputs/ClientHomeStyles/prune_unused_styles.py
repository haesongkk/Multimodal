import unreal as u,json
from pathlib import Path
e=u.get_editor_subsystem(u.EditorAssetSubsystem);reg=u.AssetRegistryHelpers.get_asset_registry()
opts=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=True,include_hard_management_references=True)
roots=['/Game/ExternalAssets/KenneyFurnitureKit','/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Papercraft','/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Materials']
candidates={str(a.package_name) for root in roots for a in reg.get_assets_by_path(root,recursive=True)}
protected=set()
for p in candidates:
 if any(str(x) not in candidates for x in reg.get_referencers(p,opts)):protected.add(p)
pending=list(protected)
while pending:
 p=pending.pop()
 for x in reg.get_dependencies(p,opts):
  x=str(x)
  if x in candidates and x not in protected:protected.add(x);pending.append(x)
remove=candidates-protected;deleted=[]
# Delete only a closed set with no incoming reference from any retained asset.
for p in sorted(remove):
 assert not any(str(x) not in remove for x in reg.get_referencers(p,opts)),p
assets=[u.load_asset(p) for p in sorted(remove) if e.does_asset_exist(p)]
if assets:e.delete_loaded_assets(assets)
deleted=[p for p in sorted(remove) if not e.does_asset_exist(p)]
assert len(deleted)==len(remove)
Path('D:/Multimodal/Outputs/ClientHomeStyles/cleanup_report.json').write_text(json.dumps({'deleted':deleted,'retained_shared_assets':sorted(protected)},indent=2))
