"""Read-only owned asset validation; no package saves."""
import json
from pathlib import Path
import unreal as u
from editor_toolset.toolsets.actor import ActorTools as A
ROOT='/Game/ClientHome_Haeso'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
registry=u.AssetRegistryHelpers.get_asset_registry()
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True,include_searchable_names=False,include_soft_management_references=False,include_hard_management_references=False)
foreign={}
shared_art={}
# Read-only project art reuse introduced by style_home.py; no team maps or gameplay.
allowed_art={ '/Game/CocoDetective/Props/Meshes/SM_Prop_'+n for n in (
    'Sofa_02','Rug_01','CoffeeTable_01','Mug_01','TableDocument_01',
    'Bookshelf_01','Plant_01','CatTree_01','CatBed_01','CatToy_01','ShoeCabinet_01') }
paths=assets.list_assets(ROOT,recursive=True,include_folder=False)
for path in paths:
    package=path.split('.')[0]
    deps=[str(x) for x in registry.get_dependencies(package,options)]
    external=[x for x in deps if x.startswith('/Game/') and not x.startswith(ROOT+'/')]
    reused=[x for x in external if x in allowed_art or x.startswith('/Game/StylizedKitchen/')]
    if reused: shared_art[path]=reused
    bad=[x for x in external if x not in reused]
    if bad: foreign[path]=bad
player=u.load_asset(ROOT+'/Blueprints/BP_CH_Player')
cdo=u.get_default_object(player.generated_class())
counts={'cameras':len(A.get_components(cdo,u.CameraComponent.static_class())),'body_meshes':len(A.get_components(cdo,u.StaticMeshComponent.static_class()))}
assert counts=={'cameras':1,'body_meshes':1},counts
assert not foreign,foreign
report={'owned_assets':len(paths),'foreign_game_dependencies':foreign,'shared_art_dependencies':shared_art,'player_components':counts}
out=Path(u.Paths.project_saved_dir())/'ClientHome'/'gameplay-asset-audit.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('CLIENT_HOME_ASSET_AUDIT_OK: '+str(report))
