"""Owned-map art pass. Reuses CocoDetective assets without editing their packages.
Run outside PIE after refine_layout.py. Original furniture remains as collision proxies.
"""
import unreal as u
ROOT='/Game/ClientHome_Haeso'
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(ROOT+'/Maps/Lvl_ClientHome_Blockout.')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
dirty=list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages())+list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
assert all(p.get_name().startswith(ROOT+'/') for p in dirty),'Foreign unsaved package'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}

def material(name,rgb):
    path=ROOT+'/Materials/M_CH_Art_'+name
    if assets.does_asset_exist(path): return u.load_asset(path)
    m=u.AssetToolsHelpers.get_asset_tools().create_asset('M_CH_Art_'+name,ROOT+'/Materials',u.Material,u.MaterialFactoryNew())
    c=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant3Vector)
    c.set_editor_property('constant',u.LinearColor(*rgb,1))
    u.MaterialEditingLibrary.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
    rough=u.MaterialEditingLibrary.create_material_expression(m,u.MaterialExpressionConstant)
    rough.set_editor_property('r',.82)
    u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    u.MaterialEditingLibrary.recompile_material(m)
    assert assets.save_loaded_asset(m)
    return m

mats={n:material(n,c) for n,c in {
    'OakA':(.39,.25,.135),'OakB':(.44,.29,.16),'OakC':(.35,.22,.115),
    'Ivory':(.79,.72,.57),'Sage':(.20,.32,.27),'Terracotta':(.48,.18,.105),
    'Linen':(.62,.54,.39),'Ink':(.045,.075,.072)}.items()}

def mesh(label,path,xyz,scale=(1,1,1),yaw=0,mat=None):
    label='CH_Art_'+label
    a=by.get(label)
    if not a:
        a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz))
        a.set_actor_label(label)
        by[label]=a
    c=a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(u.load_asset(path))
    if mat: c.set_material(0,mats[mat])
    a.set_actor_location(u.Vector(*xyz),False,False)
    a.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
    a.set_actor_scale3d(u.Vector(*scale))
    a.set_actor_enable_collision(False)
    a.set_folder_path('ClientHome/ArtPass')
    return a

def prop(label,name,xyz,scale=(1,1,1),yaw=0):
    return mesh(label,'/Game/CocoDetective/Props/Meshes/SM_Prop_'+name,xyz,scale,yaw)
def box(label,xyz,size,mat,yaw=0):
    return mesh(label,'/Engine/BasicShapes/Cube',xyz,tuple(s/100 for s in size),yaw,mat)

# Keep proven blocking volumes while replacing their visible primitives.
hidden=['Sofa_Base','Sofa_Back','Sofa_Arm_115','Sofa_Arm_355','Rug','CoffeeTable',
        'CatTree_Base','CatTree_Post','CatTree_Platform','CatBed','Entry_ShoeCabinet']
hidden += ['TableLeg_%s_%s'%(x,y) for x in (-195,-125) for y in (210,310)]
for name in hidden:
    by['CH_'+name].get_component_by_class(u.StaticMeshComponent).set_visibility(False)

# Broad parallel boards keep the central investigation route easy to read.
for row in range(10):
    for col in range(4):
        box('Floor_%02d_%02d'%(row,col),(-450+col*300,-450+row*100,.7),
            (298.5,98.5,1.2),['OakA','OakB','OakC'][(row+col*2)%3])
box('NorthSkirting',(0,486,10),(1180,5,20),'Ivory')
box('WestSkirting',(-586,0,10),(5,980,20),'Ivory')
box('NorthRail',(0,486,90),(1180,5,5),'Ivory')
box('NorthPanel',(0,489,45),(1180,3,82),'Sage')
for x in range(-550,600,100): box('WallBatten_'+str(x),(x,486,45),(4,4,82),'Ivory')

prop('Sofa','Sofa_02',(-385,235,0),(1.12,1.1,.85),90)
prop('Rug','Rug_01',(-170,235,1.5),(1.18,1.65,1),90)
prop('CoffeeTable','CoffeeTable_01',(-160,260,0),(1.1,1.1,1.1))
prop('Mug','Mug_01',(-175,250,43),(1,1,1),20)
prop('TablePaper','TableDocument_01',(-145,277,43),(.65,.65,.65),-15)
prop('Bookshelf','Bookshelf_01',(-330,445,0),(1.1,1,1))
prop('CornerPlant','Plant_01',(-520,418,0),(1.1,1.1,1.4))
prop('CatTree','CatTree_01',(320,420,0),(.85,.85,.85))
prop('CatBed','CatBed_01',(130,420,0),(1.15,1.15,1))
prop('CatToy','CatToy_01',(230,335,2),(1,1,1),25)
prop('ShoeCabinet','ShoeCabinet_01',(-550,-300,0),(1,1,1.3),90)
prop('EntryPlant','Plant_01',(-550,-310,91),(.42,.42,.42))

# Curtain stacks frame the open window without covering its interaction point.
for side,y in [('Near',35),('Far',325)]:
    for i in range(4):
        mesh('Curtain_'+side+str(i),'/Engine/BasicShapes/Cylinder',(565,y+i*8,183),(.15,.15,1.5),mat='Linen')
    box('CurtainTie_'+side,(555,y+12,153),(10,42,5),'Terracotta')
box('CurtainRail',(566,190,264),(8,358,8),'Ink')
box('WindowTrimTop',(583,180,248),(24,272,12),'Ivory')
box('WindowTrimFar',(583,307,176),(24,12,144),'Ivory')

# A small leaf cluster makes the toppled pot read as a plant from the game camera.
for i,(x,y,z) in enumerate([(-151,-61,25),(-172,-62,19),(-162,-43,18)]):
    mesh('FallenLeaf'+str(i),'/Engine/BasicShapes/Sphere',(x,y,z),(.42,.18,.06),i*35,mat='Sage')
pot=by['CH_Clue_Pot'].get_component_by_class(u.StaticMeshComponent)
pot.set_material(0,mats['Terracotta'])
by['CH_Clue_WindowFrame'].get_component_by_class(u.StaticMeshComponent).set_material(0,mats['Ivory'])

sun=by['CH_Sun'].get_component_by_class(u.DirectionalLightComponent)
sun.set_light_color(u.LinearColor(1,.88,.69,1))
for a in by.values():
    if a.get_actor_label().startswith('CH_Fill_'):
        a.get_component_by_class(u.PointLightComponent).set_light_color(u.LinearColor(1,.94,.84,1))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('CLIENT_HOME_ART_PASS_OK')
