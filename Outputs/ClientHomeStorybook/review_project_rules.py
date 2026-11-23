import unreal as u,json,re
from pathlib import Path
reg=u.AssetRegistryHelpers.get_asset_registry()
root='/Game/Multimodal/90_Sandbox/'
assets=list(reg.get_assets_by_path(root+'Experiments/ClientHome',recursive=True))+list(reg.get_assets_by_path(root+'Maps/ClientHome',recursive=True))
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=True,include_hard_management_references=True)
prefix={'World':'LV_','Blueprint':'BP_','StaticMesh':'SM_','Material':'M_','Texture2D':'T_'}
issues=[];outside=[]
for a in assets:
 p=str(a.package_name);name=str(a.asset_name);kind=str(a.asset_class_path.asset_name)
 if not re.fullmatch('[A-Za-z0-9_]+',name) or not name.startswith(prefix.get(kind,'UNEXPECTED_')):issues.append(p)
 for ref in reg.get_referencers(p,options):
  ref=str(ref)
  if ref.startswith('/Game/') and not ref.startswith(root):outside.append({'asset':p,'referencer':ref})
report={'asset_count':len(assets),'invalid_asset_names':issues,'non_sandbox_referencers':outside,'maps':[str(a.asset_name) for a in assets if str(a.asset_class_path.asset_name)=='World'],'dirty_maps':[x.get_path_name() for x in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'dirty_content':[x.get_path_name() for x in u.EditorLoadingAndSavingUtils.get_dirty_content_packages()]}
Path('D:/Multimodal/Outputs/ClientHomeStorybook/project_rules_audit.json').write_text(json.dumps(report,indent=2))
