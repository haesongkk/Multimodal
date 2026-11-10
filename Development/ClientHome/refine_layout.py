"""Idempotent first exploration pass; only the owned map is edited/saved.

Run in editor Python, outside PIE, before build_gameplay.py.
Keeps existing furniture and routes; adds collision-free visual breadcrumbs.
"""
import unreal as u

ROOT = '/Game/ClientHome_Haeso'
MAP = ROOT + '/Maps/Lvl_ClientHome_Blockout'
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(MAP + '.'), 'Open owned map first'
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(), 'Stop PIE first'
dirty = list(u.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(u.EditorLoadingAndSavingUtils.get_dirty_map_packages())
assert all(p.get_name().startswith(ROOT + '/') for p in dirty), 'Foreign unsaved package'
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
for label in ('CH_Clue_Pot', 'CH_Spilled_Soil', 'CH_Clue_Fur', 'CH_Clue_WindowFrame'):
    assert label in by_label, 'Missing original blockout actor: ' + label

for label, xyz in [('CH_Clue_Pot', (-130, -80, 22)),
                   ('CH_Spilled_Soil', (-75, -60, 3)),
                   ('CH_Clue_Fur', (350, 170, 5))]:
    by_label[label].set_actor_location(u.Vector(*xyz), False, False)

def detail(label, xyz, size, material, mesh='Sphere', yaw=0):
    actor = by_label.get(label)
    if actor is None:
        actor = actors.spawn_actor_from_class(u.StaticMeshActor, u.Vector(*xyz))
        actor.set_actor_label(label)
        by_label[label] = actor
    component = actor.get_component_by_class(u.StaticMeshComponent)
    assert component, label
    component.set_static_mesh(u.load_asset('/Engine/BasicShapes/' + mesh))
    component.set_material(0, u.load_asset(ROOT + '/Materials/M_CH_' + material))
    actor.set_actor_location(u.Vector(*xyz), False, False)
    actor.set_actor_rotation(u.Rotator(pitch=0, yaw=yaw, roll=0), False)
    actor.set_actor_scale3d(u.Vector(*(v / 100 for v in size)))
    actor.set_actor_enable_collision(False)
    actor.set_folder_path('ClientHome/ExplorationDetails')

# Sparse spilled earth, not an explicit arrow or a second collectible.
for i, (x, y, width) in enumerate([(0,-30,24),(65,0,20),(135,45,16),(200,85,12),(260,120,9)]):
    detail('CH_SoilTrail_' + str(i), (x,y,3), (width,width*.65,4), 'Soil')
# A visible, open sash gives the escape clue an actual silhouette.
detail('CH_Window_OpenLeaf', (665,110,105), (150,8,8), 'Cream', 'Cube', 35)
detail('CH_Window_OpenLeaf_Top', (665,110,235), (150,8,8), 'Cream', 'Cube', 35)
detail('CH_Window_OpenLeaf_Hinge', (604,67,170), (8,8,138), 'Cream', 'Cube', 35)
detail('CH_Window_OpenLeaf_Edge', (726,153,170), (8,8,138), 'Cream', 'Cube', 35)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('CLIENT_HOME_LAYOUT_REFINED')
