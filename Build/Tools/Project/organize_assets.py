import unreal as u,json,traceback
from pathlib import Path
out=Path('D:/Multimodal/Outputs/Organization')
r=u.AssetRegistryHelpers.get_asset_registry(); a=u.get_editor_subsystem(u.EditorAssetSubsystem)
def destination(p,c):
    tail=p.split('/ClientHome_Haeso/')[1];name=tail.rsplit('/',1)[-1];base='/Game/Multimodal/'
    if c=='World': return base+('90_Sandbox/Maps/ClientHome/' if 'Blockout' in name else '01_Maps/ClientHome/')+name.replace('Lvl_','LV_',1)
    if c=='Blueprint':
        folder='Characters/Player' if 'Player' in name else ('Buildings' if 'Door' in name else 'Framework')
        return base+'02_Blueprints/'+folder+'/ClientHome/'+name
    if c=='WidgetBlueprint':return base+'04_UI/Widgets/ClientHome/'+name
    if c=='Font':return base+'04_UI/Fonts/ClientHome/'+('FNT_Jua' if name=='F_Jua' else 'FNT_Jua_Imported')
    if c=='FontFace':return base+'04_UI/Fonts/ClientHome/FF_Jua'
    if c=='Texture2D':return base+'04_UI/Textures/ClientHome/'+name
    if c=='StaticMesh':return base+'03_Graphics/Meshes/Buildings/ClientHome/'+tail.split('Meshes/')[1]
    if c in ('Material','MaterialInstanceConstant','MaterialParameterCollection'):
        if name.startswith('Reveal_') or name.startswith('Fade_'):
            name=('MI_' if c=='MaterialInstanceConstant' else 'M_')+'CH_'+name
        return base+'03_Graphics/Materials/Buildings/ClientHome/'+('/'.join(tail.split('/')[1:-1])+'/' if '/' in tail.split('Materials/')[1] else '')+name
    raise RuntimeError((p,c))
try:
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    dirty=u.EditorLoadingAndSavingUtils.get_dirty_content_packages()+u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert u.EditorLoadingAndSavingUtils.save_packages(dirty,False)
    rows=r.get_assets_by_path('/Game/ClientHome_Haeso',recursive=True)+r.get_assets_by_path('/Game/StylizedKitchen',recursive=True)
    mapping={};renames=[]
    for x in rows:
        p=str(x.package_name);c=str(x.asset_class_path.asset_name)
        if c=='ObjectRedirector':continue
        dst=p.replace('/Game/StylizedKitchen/','/Game/ExternalAssets/StylizedKitchen/') if p.startswith('/Game/StylizedKitchen/') else destination(p,c)
        assert not a.does_asset_exist(dst),dst
        obj=x.get_asset();assert obj,p
        mapping[p]=dst;folder,name=dst.rsplit('/',1);renames.append(u.AssetRenameData(obj,folder,name))
    (out/'AssetMoves.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
    assert u.AssetToolsHelpers.get_asset_tools().rename_assets(renames),'rename failed'
    assert a.save_directory('/Game/Multimodal',only_if_is_dirty=False,recursive=True)
    assert a.save_directory('/Game/ExternalAssets/StylizedKitchen',only_if_is_dirty=False,recursive=True)
    dirty=u.EditorLoadingAndSavingUtils.get_dirty_content_packages()+u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    assert u.EditorLoadingAndSavingUtils.save_packages(dirty,False)
    (out/'MigrationResult.json').write_text(json.dumps({'success':True,'moved':len(mapping)}),encoding='utf-8')
except Exception:
    (out/'MigrationResult.json').write_text(json.dumps({'success':False,'error':traceback.format_exc()}),encoding='utf-8');raise
