"""Art direction for the owned Fab-based home. Run outside PIE in UE 5.8.
Reuses the licensed source scene; saves only the owned copy and new materials.
Does not install gameplay or alter the working blockout map.
"""
import json, math
from pathlib import Path
import unreal as u

ROOT='/Game/ClientHome_Haeso'
SOURCE='/Game/StylizedKitchen/Levels/Stylized_Interior'
MAP=ROOT+'/Maps/Lvl_ClientHome_Interior'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
levels=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(),'Stop PIE first'
dirty=list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
assert all(p.get_name().startswith(ROOT+'/') for p in dirty),'Foreign unsaved changes'
if dirty: assert u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
if not assets.does_asset_exist(MAP):
    assert levels.load_level(SOURCE)
    source_world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
    assert u.EditorLoadingAndSavingUtils.save_map(source_world,MAP),'Could not save owned map copy'
    del source_world
assert levels.load_level(MAP)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
by={a.get_actor_label():a for a in actors.get_all_level_actors()}

def move(name,xyz,yaw=None):
    a=by[name]
    a.set_actor_location(u.Vector(*xyz),False,False)
    if yaw is not None: a.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
    return a
def hide(a):
    a.set_actor_hidden_in_game(True)
    a.set_is_temporarily_hidden_in_editor(True)
    for c in a.get_components_by_class(u.SceneComponent):
        c.set_visibility(False)
    a.set_actor_enable_collision(False)

# Strip decorative wall damage in the living area; leave the other rooms intact.
for a in list(by.values()):
    if a.get_class().get_name()=='DecalActor' and a.get_actor_location().x>-300:
        actors.destroy_actor(a)
        continue
    c=a.get_component_by_class(u.StaticMeshComponent)
    if c and c.static_mesh:
        n=c.static_mesh.get_name(); p=a.get_actor_location()
        if n.startswith(('SM_FlowerPot','SM_FlowersPlant')) and p.x>700 and p.y>470:
            hide(a)

# Retain two plants as deliberate accents, rather than a dense showroom cluster.
for label in ['SM_FlowerPot_07','SM_FlowersPlant_10']:
    a=by[label]; a.set_actor_hidden_in_game(False); a.set_is_temporarily_hidden_in_editor(False)
    a.get_component_by_class(u.StaticMeshComponent).set_visibility(True)
move('Assets_Proxy_LR_Table_Proxy',(405,575,21),-90)
# Keep tabletop props together; move the whole tea-table vignette away from the clue path.
for a in list(by.values()):
    p=a.get_actor_location()
    if 540<p.x<655 and 50<p.y<205 and 20<p.z<115 and not a.actor_has_tag(u.Name('CH_TeaMoved')):
        a.set_actor_location(u.Vector(p.x-65,p.y-130,p.z),False,False)
        a.set_editor_property('tags',list(a.tags)+[u.Name('CH_TeaMoved')])
move('SM_Carpet_01',(533,3,21))
move('Assets_Proxy_LR_Chair_Proxy',(735,-80,21),-120)
move('Assets_Proxy_LR_Chair_Proxy2',(425,-85,21),-40)
for label,y in [('Kitchen_Curtain_Low3',122),('Kitchen_Curtain_Low4',365)]:
    a=move(label,(901,y,257)); a.set_actor_scale3d(u.Vector(1,.45,1))

def material(name,rgb):
    path=ROOT+'/Materials/M_CH_Interior_'+name
    if assets.does_asset_exist(path): return u.load_asset(path)
    m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_CH_Interior_'+name,ROOT+'/Materials',u.Material,u.MaterialFactoryNew())
    e=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
    e.set_editor_property('constant',u.LinearColor(*rgb,1))
    u.MaterialEditingLibrary.connect_material_property(e,'',u.MaterialProperty.MP_BASE_COLOR)
    r=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant)
    r.set_editor_property('r',.9)
    u.MaterialEditingLibrary.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS)
    u.MaterialEditingLibrary.recompile_material(m)
    assert assets.save_loaded_asset(m)
    return m
mats={n:material(n,c) for n,c in {'Cream':(.66,.56,.39),'Soil':(.055,.027,.012),'Linen':(.52,.36,.19),'Fur':(.91,.79,.56),'Sage':(.16,.24,.16)}.items()}

# The source wall uses vertex-blended torn wallpaper textures. Use the intact
# wallpaper in all three layers of an owned material instance.
wall_path=ROOT+'/Materials/MI_CH_IntactWallpaper'
wall=u.load_asset(wall_path) if assets.does_asset_exist(wall_path) else assets.duplicate_asset('/Game/StylizedKitchen/Materials/MI_Wallpaper_A',wall_path)
replacements=dict([('Base_2(Red)','T_Wallpaper_A_D'),('Base_3(Green)','T_Wallpaper_A_D'),
                          ('Normal_2(Red)','T_Wallpaper_A_N'),('Normal_3(Green)','T_Wallpaper_A_N'),
                          ('MRE_2(Red)','T_Wallpaper_A_MRE'),('MRE_3(Green)','T_Wallpaper_A_MRE')])
values=wall.get_editor_property('texture_parameter_values')
for value in values:
    name=str(value.parameter_info.name)
    if name in replacements: value.set_editor_property('parameter_value',u.load_asset('/Game/StylizedKitchen/Textures/'+replacements[name]))
wall.set_editor_property('texture_parameter_values',values)
u.MaterialEditingLibrary.update_material_instance(wall)
assert assets.save_loaded_asset(wall)
by['House_Walls_SM'].get_component_by_class(u.StaticMeshComponent).set_material(2,wall)
floor_path=ROOT+'/Materials/MI_CH_SoftWoodFloor'
floor=u.load_asset(floor_path) if assets.does_asset_exist(floor_path) else assets.duplicate_asset('/Game/StylizedKitchen/Materials/MI_Wood_Floor',floor_path)
values=floor.get_editor_property('scalar_parameter_values')
for value in values:
    if str(value.parameter_info.name)=='HeightOfTexture': value.set_editor_property('parameter_value',.004)
floor.set_editor_property('scalar_parameter_values',values)
u.MaterialEditingLibrary.update_material_instance(floor)
assert assets.save_loaded_asset(floor)
fc=by['House_Floor'].get_component_by_class(u.StaticMeshComponent)
for i,m in enumerate(fc.get_materials()):
    if m and m.get_name() in ['MI_Wood_Floor','MI_CH_SoftWoodFloor']: fc.set_material(i,floor)

def mesh(label,path,xyz,scale=(1,1,1),rotation=(0,0,0),mat=None,tag=None):
    label='CH_Interior_'+label
    a=by.get(label)
    if not a:
        a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz))
        a.set_actor_label(label); by[label]=a
    c=a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(u.load_asset(path))
    if mat: c.set_material(0,mats[mat])
    a.set_actor_location(u.Vector(*xyz),False,False)
    a.set_actor_rotation(u.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2]),False)
    a.set_actor_scale3d(u.Vector(*scale))
    a.set_actor_enable_collision(False)
    a.set_folder_path('ClientHome/InteriorArt')
    if tag: a.set_editor_property('tags',[u.Name(tag)])
    return a
def prop(label,name,xyz,scale=(1,1,1),rotation=(0,0,0),tag=None):
    return mesh(label,'/Game/StylizedKitchen/Meshes/'+name,xyz,scale,rotation,tag=tag)
def shape(label,xyz,size,mat,kind='Sphere',rotation=(0,0,0),tag=None):
    return mesh(label,'/Engine/BasicShapes/'+kind,xyz,tuple(v/100 for v in size),rotation,mat,tag)

# An open sash replaces the closed source window. Frame dimensions match its aperture.
hide(by['Assets_Proxy_LR_Window_Proxy'])
for name,xyz,size in [('Sill',(915,243,109),(32,188,9)),('Lintel',(915,243,312),(15,188,9)),
                      ('JambNear',(915,151,210),(15,8,204)),('JambFar',(915,335,210),(15,8,204))]:
    shape(name,xyz,size,'Cream','Cube',tag='Home_Window' if name=='Sill' else None)
# Rotated outward around the far jamb; the escape opening stays visually empty.
for name,z in [('LeafBottom',116),('LeafTop',305),('LeafMiddle',210)]:
    shape(name,(968,271,z),(8,160,6),'Cream','Cube',(0,40,0))
shape('LeafEdge',(1020,210,210),(8,8,194),'Cream','Cube')
shape('LeafHinge',(917,332,210),(8,8,194),'Cream','Cube')

# A fallen pot at the base of the window cabinet is the beginning of the trail.
hide(by['SM_FlowerPot_02']); hide(by['SM_FlowersPlant_02'])
prop('FallenPot','SM_FlowerPot_02',(740,205,38),(1.65,1.65,1.65),(76,28,0),tag='Home_Pot')
prop('FallenPlant','SM_FlowersPlant_02',(712,188,28),(.85,.85,.85),(82,25,0))
for i,(x,y,s) in enumerate([(736,220,37),(715,214,24),(754,226,18),(695,218,12)]):
    shape('SoilSpill'+str(i),(x,y,23),(s,s*.67,2.2),'Soil')
for i in range(8):
    x=754+i*15; y=246+math.sin(i*.65)*15
    shape('PawPad'+str(i),(x,y,23.0),(5.5,4.8,.65),'Soil')
    for j in range(3):
        shape('PawToe%d_%d'%(i,j),(x+4,y-3+j*3,23.1),(2.2,2,.6),'Soil')
for i in range(5):
    shape('Fur'+str(i),(867+i*2.2,261+(i%2)*2,126),(9,1.4,.9),'Fur',rotation=(0,i*19,0),tag='Home_Fur' if i==0 else None)

# An empty cat bed and a used scratching post make the missing resident tangible.
shape('CatMat',(770,520,23),(140,100,3),'Linen',rotation=(0,12,0))
shape('CatBed',(770,520,30),(95,67,17),'Sage')
shape('CatBedCushion',(770,517,38),(74,49,9),'Cream')
shape('ScratchBase',(650,560,27),(55,55,10),'Linen','Cube')
shape('ScratchPost',(650,560,68),(15,15,74),'Cream','Cylinder')
for i in range(12):
    shape('ScratchRope'+str(i),(650,560,36+i*5),(16,16,1.6),'Linen','Cylinder')
shape('ToyBall',(705,475,29),(13,13,13),'Sage')
shape('ToyDot',(703,470,33),(5,3,5),'Cream')

# Tone down the strong lens effects from the showroom; preserve its baked lighting.
for a in actors.get_all_level_actors():
    if isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings')
        s.set_editor_property('override_scene_fringe_intensity',True)
        s.set_editor_property('scene_fringe_intensity',0)
        s.set_editor_property('override_bloom_intensity',True)
        s.set_editor_property('bloom_intensity',.2)
        a.set_editor_property('settings',s)

u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(
    u.Vector(400,350,200),u.Rotator(pitch=-15,yaw=-8,roll=0))
u.EditorLevelLibrary.editor_set_game_view(True)
assert levels.save_current_level()
labels=[a.get_actor_label() for a in actors.get_all_level_actors()]
assert len(labels)==len(set(labels)),'Duplicate actor labels'
for tag in ['Home_Pot','Home_Fur','Home_Window']:
    assert sum(a.actor_has_tag(u.Name(tag)) for a in actors.get_all_level_actors())==1,tag
Path('D:/Multimodal/Saved/ClientHome/interior-art-report.json').write_text(json.dumps({
    'map':MAP,'source':SOURCE,'actors':len(labels),'new_art_actors':sum(n.startswith('CH_Interior_') for n in labels),
    'unique_clue_tags':True,'gameplay_connected':False},indent=2),encoding='utf-8')
u.log('CLIENT_HOME_INTERIOR_ART_OK')
