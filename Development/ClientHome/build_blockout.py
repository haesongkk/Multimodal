"""Create ONLY new ClientHome_Haeso assets; run inside UE 5.8 editor.

No team assets or project settings are edited. This is a spatial blockout,
not the final interaction implementation. Refuses to overwrite its outputs.
"""
import json
from pathlib import Path
import unreal

# Leave the editor available for MCP inspection after command-line execution.
unreal.EditorPythonScripting.set_keep_python_script_alive(True)

ROOT = '/Game/ClientHome_Haeso'
MAP = ROOT + '/Maps/Lvl_ClientHome_Blockout'
COLORS = {
    'Floor': (0.40, 0.28, 0.17),
    'Wall': (0.82, 0.76, 0.62),
    'Sage': (0.22, 0.40, 0.32),
    'Wood': (0.28, 0.13, 0.06),
    'Cream': (0.85, 0.78, 0.59),
    'Clue': (0.95, 0.55, 0.06),
    'Soil': (0.08, 0.04, 0.02),
    'Fur': (0.90, 0.86, 0.75),
    'Exit': (0.10, 0.45, 0.65),
}


def build():
    if not unreal.SystemLibrary.get_engine_version().startswith('5.8.'):
        raise RuntimeError('Use UE 5.8.x; no assets were created.')
    assets = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    outputs = [MAP] + [ROOT + '/Materials/M_CH_' + n for n in COLORS]
    for path in outputs:
        if assets.does_asset_exist(path):
            raise RuntimeError('Refusing to overwrite existing asset: ' + path)
    dirty = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    dirty += list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    if dirty:
        raise RuntimeError('Start with a clean editor session; unsaved packages exist.')

    meshes = {n: unreal.load_asset('/Engine/BasicShapes/' + n) for n in ('Cube', 'Sphere', 'Cylinder')}
    if not all(meshes.values()):
        raise RuntimeError('Engine basic shapes unavailable.')
    if not levels.new_level(MAP):
        raise RuntimeError('Could not create isolated map.')
    mats = {}
    for name, rgb in COLORS.items():
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'M_CH_' + name, ROOT + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
        if material is None:
            raise RuntimeError('Material creation failed: ' + name)
        color = unreal.MaterialEditingLibrary.create_material_expression(material, unreal.MaterialExpressionConstant3Vector)
        color.set_editor_property('constant', unreal.LinearColor(*rgb, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(color, '', unreal.MaterialProperty.MP_BASE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(material)
        if not assets.save_loaded_asset(material):
            raise RuntimeError('Material save failed: ' + name)
        mats[name] = material

    created = []

    def shape(label, xyz, size, material, folder, mesh='Cube', rotation=(0, 0, 0), collision=True):
        actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*xyz),
                                              unreal.Rotator(pitch=rotation[0], yaw=rotation[1], roll=rotation[2]))
        actor.set_actor_label('CH_' + label)
        actor.set_folder_path('ClientHome/' + folder)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_static_mesh(meshes[mesh])
        component.set_material(0, mats[material])
        actor.set_actor_scale3d(unreal.Vector(*(v / 100 for v in size)))
        actor.set_actor_enable_collision(collision)
        created.append({'label': 'CH_' + label, 'position_cm': xyz, 'size_cm': size, 'folder': folder})
        return actor

    # 12 x 10 m interior. 300 cm walls, east window, south entrance.
    shape('Floor', (0, 0, -10), (1200, 1000, 20), 'Floor', 'Architecture')
    shape('Porch', (-400, -610, -10), (240, 220, 20), 'Floor', 'Architecture')
    shape('Wall_North', (0, 500, 150), (1220, 20, 300), 'Wall', 'Architecture')
    shape('Wall_West', (-600, 0, 150), (20, 1000, 300), 'Wall', 'Architecture')
    shape('Wall_South_Left', (-535, -500, 150), (130, 20, 300), 'Wall', 'Architecture')
    shape('Wall_South_Right', (135, -500, 150), (930, 20, 300), 'Wall', 'Architecture')
    shape('Entrance_Lintel', (-400, -500, 270), (140, 20, 60), 'Wall', 'Architecture')
    shape('Wall_East_South', (600, -220, 150), (20, 560, 300), 'Wall', 'Architecture')
    shape('Wall_East_North', (600, 400, 150), (20, 200, 300), 'Wall', 'Architecture')
    shape('Window_SillWall', (600, 180, 50), (20, 240, 100), 'Wall', 'Architecture')
    shape('Window_Lintel', (600, 180, 270), (20, 240, 60), 'Wall', 'Architecture')
    shape('Window_Sill', (580, 180, 100), (60, 260, 10), 'Cream', 'Architecture')
    # Open leaf is a placeholder, not an animated door.
    shape('Door_Open_Placeholder', (-470, -570, 115), (12, 140, 230), 'Exit', 'Architecture')

    # Furniture leaves the entry -> living -> window route clear.
    shape('Sofa_Base', (-385, 235, 28), (120, 260, 56), 'Sage', 'Furniture')
    shape('Sofa_Back', (-440, 235, 65), (22, 260, 90), 'Sage', 'Furniture')
    for y in (115, 355):
        shape('Sofa_Arm_' + str(y), (-385, y, 55), (120, 20, 70), 'Sage', 'Furniture')
    shape('Rug', (-160, 235, 2), (260, 300, 4), 'Cream', 'Furniture', collision=False)
    shape('CoffeeTable', (-160, 260, 36), (95, 140, 12), 'Wood', 'Furniture')
    for x in (-195, -125):
        for y in (210, 310):
            shape('TableLeg_%s_%s' % (x, y), (x, y, 15), (9, 9, 30), 'Wood', 'Furniture')
    shape('Kitchen_Counter', (300, -430, 45), (360, 110, 90), 'Cream', 'Furniture')
    shape('Kitchen_Top', (300, -430, 95), (370, 120, 10), 'Wood', 'Furniture')
    shape('Fridge', (510, -410, 100), (100, 140, 200), 'Cream', 'Furniture')
    shape('Entry_ShoeCabinet', (-550, -300, 55), (65, 150, 110), 'Wood', 'Furniture')
    shape('CatTree_Base', (320, 420, 8), (110, 110, 16), 'Wood', 'PetProps')
    shape('CatTree_Post', (320, 420, 68), (18, 18, 120), 'Cream', 'PetProps', mesh='Cylinder')
    shape('CatTree_Platform', (320, 420, 130), (90, 90, 12), 'Sage', 'PetProps')
    shape('CatBed', (130, 430, 12), (100, 70, 24), 'Sage', 'PetProps', mesh='Sphere')
    for x in (60, 110):
        shape('Bowl_' + str(x), (x, -380, 8), (32, 32, 16), 'Cream', 'PetProps', mesh='Cylinder')

    # Unique labels/tags provide future interaction attachment points.
    pot = shape('Clue_Pot', (80, 160, 22), (42, 42, 55), 'Clue', 'Clues', mesh='Cylinder', rotation=(75, 15, 0))
    pot.set_editor_property('tags', [unreal.Name('Home_Pot')])
    shape('Spilled_Soil', (125, 170, 3), (95, 70, 6), 'Soil', 'Clues', mesh='Sphere', collision=False)
    fur = shape('Clue_Fur', (350, 170, 5), (45, 24, 10), 'Fur', 'Clues', mesh='Sphere', collision=False)
    fur.set_editor_property('tags', [unreal.Name('Home_Fur')])
    window = shape('Clue_WindowFrame', (585, 60, 175), (25, 10, 150), 'Clue', 'Clues')
    window.set_editor_property('tags', [unreal.Name('Home_Window')])

    player = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-400, -360, 100), unreal.Rotator(pitch=0, yaw=90, roll=0))
    player.set_actor_label('CH_PlayerStart')
    player.set_folder_path('ClientHome/Test')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property('default_game_mode', unreal.GameModeBase)
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 650), unreal.Rotator(pitch=-55, yaw=-35, roll=0))
    light.set_actor_label('CH_Sun')
    light.set_folder_path('ClientHome/Lighting')
    for x, y in ((-250, 150), (300, 150), (0, -250)):
        fill = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, 260))
        fill.set_actor_label('CH_Fill_%s_%s' % (x, y))
        fill.set_folder_path('ClientHome/Lighting')
        comp = fill.get_component_by_class(unreal.PointLightComponent)
        comp.set_editor_property('intensity', 3000.0)
        comp.set_editor_property('attenuation_radius', 1000.0)
    if not levels.save_current_level():
        raise RuntimeError('Map save failed.')
    # Verify the saved package can be reopened and has no team-content dependencies.
    if not levels.load_level(MAP):
        raise RuntimeError('Saved map could not be reopened.')
    loaded_actors = list(actors.get_all_level_actors())
    for clue_id in ('Home_Pot', 'Home_Fur', 'Home_Window'):
        matches = [a for a in loaded_actors if a.actor_has_tag(unreal.Name(clue_id))]
        if len(matches) != 1:
            raise RuntimeError('Saved map must contain exactly one clue: ' + clue_id)
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    options = unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=True, include_hard_package_references=True,
        include_searchable_names=False, include_soft_management_references=False,
        include_hard_management_references=False)
    dependencies = [str(p) for p in registry.get_dependencies(MAP, options)]
    unexpected = [p for p in dependencies if p.startswith('/Game/') and not p.startswith(ROOT + '/')]
    if unexpected:
        raise RuntimeError('Unexpected team-content dependencies: ' + str(unexpected))
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
        unreal.Vector(-1100, -1350, 1450), unreal.Rotator(pitch=-42, yaw=50, roll=0))
    report = Path(unreal.Paths.project_saved_dir()) / 'ClientHome' / 'blockout-report.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({'map': MAP, 'engine': unreal.SystemLibrary.get_engine_version(), 'shapes': created,
                                 'verified': {'reopened': True, 'unique_clues': True, 'team_content_dependencies': unexpected},
                                 'dependencies': dependencies,
                                 'limitations': ['No clue interaction yet', 'Door is a static placeholder', 'Alley not connected']}, indent=2), encoding='utf-8')
    unreal.log('CLIENT_HOME_BLOCKOUT_OK: ' + MAP)


build()
