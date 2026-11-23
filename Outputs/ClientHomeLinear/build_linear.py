import unreal as u, json, math
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B, _BlueprintCache
from editor_toolset.toolsets.actor import ActorTools as A
OUT=Path('D:/Multimodal/Outputs/ClientHomeLinear')
MAP='/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Linear'
SRC='/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal'
GEO='/Game/Multimodal/03_Graphics/Meshes/Buildings/ClientHome/Linear'
eas=u.get_editor_subsystem(u.EditorAssetSubsystem)
les=u.get_editor_subsystem(u.LevelEditorSubsystem)
aas=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
actors={a.get_name():a for a in aas.get_all_level_actors()}
baseline=json.loads((OUT/'inventory_before.json').read_text())
visibility={r['name']:r for r in json.loads((OUT/'visibility_before.json').read_text())}
for r in baseline:
    a=actors[r['name']];v=visibility[r['name']]
    a.set_actor_location(u.Vector(*r['loc']),False,True)
    a.set_actor_scale3d(u.Vector(*r['scale']))
    a.set_actor_hidden_in_game(v['hidden']);a.set_is_temporarily_hidden_in_editor(v['temp_hidden'])
    a.set_actor_enable_collision(v['collision'])
    a.set_folder_path(r['folder'] if r['folder']!='None' else '')
def hide(a):
    a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True);a.set_actor_enable_collision(False)
def move(a,dx,dy,zone):
    p=a.get_actor_location();a.set_actor_location(u.Vector(p.x+dx,p.y+dy,p.z),False,True)
    a.set_folder_path('ClientHome/Linear/'+zone)
report=[]
shell=[]
for r in baseline:
    a=actors[r['name']]; label=r['label']; x,y,z=r['loc']; folder=r['folder']
    if visibility[r['name']]['hidden']: continue
    # Existing architecture is replaced by UV-preserving slices, not scaled furniture.
    if folder in ['ClientHome/CameraCutaway','ClientHome/ClosedBathroomBoundary','ClientHome/FridgeEntry'] or label.startswith(('House_','Crown_Molding','Cube')):
        hide(a);shell.append(label);continue
    if folder=='ClientHome/SmallBathroom':
        move(a,-150,1060,'Bathroom');report.append([label,'Bathroom',-150,1060]);continue
    if label=='CH_ClearSky_Backdrop':
        a.set_actor_scale3d(a.get_actor_scale3d()*2);continue
    if label in ['PlayerStart','CH_Minimal_ExitTarget']:
        move(a,-1000,378,'Entry');continue
    if label.startswith('Fridge_'):
        move(a,-365,490,'Kitchen');report.append([label,'Kitchen',-365,490]);continue
    if label.startswith('CH_Native_Desk_'):
        move(a,280,810,'StudyDesk');report.append([label,'StudyDesk',280,810]);continue
    if label.startswith('CH_Minimal_Fur'):
        move(a,200,500,'StudyDesk');continue
    if label.startswith('CH_Minimal_Snack'):
        move(a,-850,260,'Kitchen');continue
    if label.startswith('CH_Minimal_Pawprint'):
        move(a,-350,0,'StudyReading');continue
    if folder.endswith('CH_Reading_B') or folder.endswith('CH_Reading_A') or 'Reading' in label or 'StudyPlant' in label:
        move(a,-350,0,'StudyReading');report.append([label,'StudyReading',-350,0]);continue
    if label in ['CH_Cozy_CatRug','CH_Cozy_CatPlantPot','CH_Cozy_CatPlantLeaves','CH_Cozy_CatCornerGlow']:
        move(a,280,810,'StudyDesk');continue
    if label=='CH_Cozy_HallRunner':
        move(a,-50,70,'StudyReading');continue
    if r['class'].endswith(('PostProcessVolume','SkyLight','ExponentialHeightFog','LightmassImportanceVolume','InstancedFoliageActor','LevelSequenceActor')):
        continue
    if 'GroupActor' in r['class']:continue
    if x < -650 and y < 0:
        # Entrance door, frame, welcome mat, and small side window.
        move(a,-1000,378,'Entry');report.append([label,'Entry',-1000,378]);continue
    if -620 < x < -250 and -10 < y < 360:
        # Dining table and every plate, chair, pendant and rug travel together.
        move(a,-300,250,'Dining');report.append([label,'Dining',-300,250]);continue
    if x < -220 and y >= 0:
        move(a,-1000,0,'Kitchen');report.append([label,'Kitchen',-1000,0]);continue
    if x>420 and y>=-150:
        dy=180 if y<360 else 0
        # Window/curtains stay attached to their original wall elevation.
        if 'Window' in label or 'Curtain' in label or 'Rod' in label or 'RectLight' in label:dy=0
        move(a,500,dy,'Living');report.append([label,'Living',500,dy]);continue
    if -220<=x<=420 and y>=0:
        move(a,-350,0,'StudyReading');report.append([label,'StudyReading',-350,0]);continue
    # Old unused decorations outside the retained room footprints.
    hide(a)

# Geometry slices retain source UVs/material slots and avoid stretching wallpaper.
def slice_mesh(source, name, cuts, offset, replacement_materials=None):
    c=source.get_component_by_class(u.StaticMeshComponent)
    dm=u.DynamicMesh()
    _,result=u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(c.static_mesh,dm,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
    u.GeometryScript_MeshTransforms.transform_mesh(dm,source.get_actor_transform())
    for axis,value,keep_less in cuts:
        normal=[0,0,0];normal[axis]=1
        rot=u.MathLibrary.make_rot_from_z(u.Vector(*normal))
        p=[0,0,0];p[axis]=value
        opts=u.GeometryScriptMeshPlaneCutOptions(fill_holes=False,flip_cut_side=not keep_less)
        u.GeometryScript_MeshBooleans.apply_mesh_plane_cut(dm,u.Transform(location=u.Vector(*p),rotation=rot),opts)
    assert dm.get_triangle_count()>0,name
    opts=u.GeometryScriptCreateNewStaticMeshAssetOptions(enable_collision=True,collision_mode=u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE,enable_nanite=False)
    mesh,result=u.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm,GEO+'/SM_CH_Linear_'+name,opts)
    assert mesh,name
    source_mats=c.get_materials()
    mats=replacement_materials or source_mats
    mesh.set_editor_property('static_materials',[u.StaticMaterial(material_interface=m) for m in mats])
    a=aas.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*offset));a.set_actor_label('CH_Linear_'+name)
    a.static_mesh_component.set_static_mesh(mesh)
    for i,m in enumerate(mats):a.static_mesh_component.set_material(i,m)
    a.set_folder_path('ClientHome/Linear/Architecture')
    eas.save_loaded_asset(mesh)
    return a
floor=actors['House_Floor_2']
slice_mesh(floor,'FloorRight',[(1,-40,False),(1,680,True)],(-1000,0,0))
slice_mesh(floor,'FloorLeft',[(1,-40,False),(1,680,True)],(744,0,0))
rear=actors['StaticMeshActor_9']
slice_mesh(rear,'RearRight',[(1,665,False)],(-1000,0,0))
wallpaper=u.load_asset('/Game/ExternalAssets/StylizedKitchen/Materials/MI_Wallpaper_A')
mats=list(rear.static_mesh_component.get_materials())
for i in [1,3,4]:mats[i]=wallpaper
# Door-sized opening behind the study into the bathroom extension.
slice_mesh(rear,'RearLeftA',[(1,665,False),(0,-374,True)],(744,0,0),mats)
slice_mesh(rear,'RearLeftB',[(1,665,False),(0,24,False)],(744,0,0),mats)
for suffix,n in [('Base','StaticMeshActor_11'),('Crown','StaticMeshActor_12')]:
    slice_mesh(actors[n],suffix+'Right',[(1,660,False)],(-1000,0,0))
    slice_mesh(actors[n],suffix+'LeftA',[(1,660,False),(0,-374,True)],(744,0,0))
    slice_mesh(actors[n],suffix+'LeftB',[(1,660,False),(0,24,False)],(744,0,0))
# Preserve the left living-room window wall. Right entrance wall is cut into panels.
slice_mesh(rear,'LivingEnd',[(0,900,False),(1,-40,False)],(744,0,0),mats)
right=actors['StaticMeshActor_345']
slice_mesh(right,'EntryEndBack',[(1,235,False)],(-1000,0,0))
slice_mesh(right,'EntryEndFront',[(1,-40,False),(1,70,True)],(-1000,0,0))

cube=u.load_asset('/Engine/BasicShapes/Cube')
trim=u.load_asset('/Game/ExternalAssets/StylizedKitchen/Materials/MI_Molding_Trim')
def box(label,loc,dimensions,material,hidden=False):
    a=aas.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*loc));a.set_actor_label(label)
    c=a.static_mesh_component;c.set_static_mesh(cube);c.set_material(0,material)
    a.set_actor_scale3d(u.Vector(*(v/100 for v in dimensions)))
    a.set_folder_path('ClientHome/Linear/Architecture')
    if hidden:a.set_actor_hidden_in_game(True)
    return a
box('CH_Linear_FrontSkirting',(-86,-40,20),(3490,12,24),trim)
box('CH_Linear_FrontBoundary',(-86,-58,160),(3500,20,300),trim,True)
box('CH_Linear_EntryLintel',(-1837,152,327),(18,166,54),trim)
box('CH_Linear_EntryJambA',(-1837,68,155),(18,10,270),trim)
box('CH_Linear_EntryJambB',(-1837,236,155),(18,10,270),trim)
box('CH_Linear_LivingBoundary',(1666,320,170),(15,720,300),trim,True)
box('CH_Linear_RightBoundary',(-1855,320,170),(15,720,300),trim,True)

# Give the new map its own pawn/camera and GameMode; original assets stay intact.
player_src='/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Minimal'
player_dst='/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Linear'
gm_src='/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Minimal'
gm_dst='/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Linear'
bp=eas.duplicate_asset(player_src,player_dst);assert bp
_BlueprintCache.invalidate(bp)
graph=B.get_graph(bp,'EventGraph')
# Change only literal camera bounds in the existing graph.
pin_changes=[]
for node in B.find_nodes(graph):
    for pin in node.list_all_pins():
        value=pin.get_pin_value()
        replacements={'-350.000000':'-1450.000000','430.000000':'1250.000000','-75.000000':'280.000000','80.000000':'340.000000','-350.0':'-1450.0','430.0':'1250.0','-75.0':'280.0','80.0':'340.0'}
        if value in replacements:
            assert pin.set_pin_value(replacements[value]);pin_changes.append([value,replacements[value]])
B.compile_blueprint(bp)
gm=eas.duplicate_asset(gm_src,gm_dst);assert gm
u.get_default_object(gm.generated_class()).set_editor_property('default_pawn_class',bp.generated_class())
B.compile_blueprint(gm)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode',gm.generated_class())
eas.save_loaded_asset(bp);eas.save_loaded_asset(gm)
assert les.save_current_level()
(OUT/'build_report.json').write_text(json.dumps({'map':MAP,'moved':report,'hidden_shell':shell,'camera_pin_changes':pin_changes},indent=2),encoding='utf-8')
u.log('CLIENT_HOME_LINEAR_BUILD_COMPLETE')
