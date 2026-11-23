import unreal as u,json
from pathlib import Path
root=Path('D:/Multimodal');e=u.get_editor_subsystem(u.EditorAssetSubsystem)
base='/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Storybook'
tasks=[]
for f in (root/'SourceAssets/ClientHome/Storybook/FBX').glob('*.fbx'):
 t=u.AssetImportTask();t.filename=str(f);t.destination_path=base+'/Meshes';t.destination_name=f.stem;t.automated=True;t.save=True
 op=u.FbxImportUI();op.import_mesh=True;op.import_materials=True;op.import_textures=False;op.import_as_skeletal=False;op.automated_import_should_detect_type=False;op.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.auto_generate_collision=True;t.options=op;t.factory=u.FbxFactory();tasks.append(t)
t=u.AssetImportTask();t.filename=str(root/'SourceAssets/ClientHome/Storybook/T_CH_StorybookArt.png');t.destination_path=base+'/Textures';t.destination_name='T_CH_StorybookArt';t.automated=True;t.save=True;tasks.append(t)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for p in e.list_assets(base+'/Meshes',recursive=False):
 a=u.load_asset(p)
 if isinstance(a,u.MaterialInterface):assert e.rename_asset(p,base+'/Materials/'+a.get_name())
e.save_directory(base,only_if_is_dirty=False,recursive=True)
(root/'Outputs/ClientHomeStorybook/imported.json').write_text(json.dumps({'models':15,'atlas':base+'/Textures/T_CH_StorybookArt'}))
