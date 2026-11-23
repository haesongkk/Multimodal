import unreal as u,json
from pathlib import Path
e=u.get_editor_subsystem(u.EditorAssetSubsystem)
e.save_directory('/Game/Multimodal/90_Sandbox/Experiments/ClientHome',only_if_is_dirty=False,recursive=True)
reg=u.AssetRegistryHelpers.get_asset_registry()
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
maps=['/Game/Multimodal/90_Sandbox/Maps/ClientHome/LV_ClientHome_'+s for s in ['Original','Storybook']]
pending=list(maps);seen=set();missing=[];redirectors=[]
while pending:
 path=pending.pop()
 if path in seen:continue
 seen.add(path)
 data=reg.get_assets_by_package_name(path)
 if not data:missing.append(path)
 if any(str(a.asset_class_path.asset_name)=='ObjectRedirector' for a in data):redirectors.append(path)
 pending.extend(str(x) for x in reg.get_dependencies(path,options) if str(x).startswith('/Game/') and str(x) not in seen)
report={'maps':maps,'checked_packages':len(seen),'missing_dependencies':missing,'redirectors':redirectors,'dirty_maps':[x.get_path_name() for x in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[x.get_path_name() for x in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}
Path('D:/Multimodal/Outputs/ClientHomeStorybook/asset_audit.json').write_text(json.dumps(report,indent=2))
