import unreal as u,json
from pathlib import Path
root=Path('D:/Multimodal')
eas=u.get_editor_subsystem(u.EditorAssetSubsystem)
paper='/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Papercraft'
external='/Game/ExternalAssets/KenneyFurnitureKit/Models'
tasks=[]
for folder,dest in [(root/'SourceAssets/ClientHome/Papercraft/FBX',paper+'/Meshes'),(root/'SourceAssets/ExternalAssets/KenneyFurnitureKit/Original/Models/FBX format',external)]:
 for file in sorted(folder.glob('*.fbx')):
  if eas.does_asset_exist(dest+'/'+file.stem):continue
  t=u.AssetImportTask();t.filename=str(file);t.destination_path=dest;t.destination_name=file.stem;t.automated=True;t.save=True;t.replace_existing=False
  op=u.FbxImportUI();op.import_mesh=True;op.import_materials=True;op.import_textures=True;op.import_as_skeletal=False;op.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
  op.automated_import_should_detect_type=False;op.static_mesh_import_data.combine_meshes=True;op.static_mesh_import_data.generate_lightmap_u_vs=True;op.static_mesh_import_data.auto_generate_collision=True
  t.options=op;t.factory=u.FbxFactory();tasks.append(t)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for path in eas.list_assets(paper+'/Meshes',recursive=False):
 a=u.load_asset(path)
 if isinstance(a,u.MaterialInterface):
  assert eas.rename_asset(path,paper+'/Materials/'+a.get_name())
  eas.save_asset(paper+'/Materials/'+a.get_name())
rows=[]
for base in [paper+'/Meshes',external]:
 for path in eas.list_assets(base,recursive=False):
  a=u.load_asset(path)
  if isinstance(a,u.StaticMesh):
   b=a.get_bounding_box();rows.append({'path':a.get_path_name(),'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z],'materials':[str(s.material_interface) for s in a.static_materials]})
(root/'Outputs/ClientHomeStyles/import_result.json').write_text(json.dumps(rows,indent=2))
