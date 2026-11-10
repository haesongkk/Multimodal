"""Add two optional clues without moving any example furniture."""
import unreal as u
import math
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
def prop(label,mesh,xyz,scale,material=None,tag=None):
    name='CH_Minimal_'+label
    a=by.get(name)
    if not a:
        a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz));a.set_actor_label(name);by[name]=a
    c=a.get_component_by_class(u.StaticMeshComponent)
    c.set_static_mesh(u.load_asset(mesh))
    if material:c.set_material(0,u.load_asset('/Game/ClientHome_Haeso/Materials/'+material))
    a.set_actor_location(u.Vector(*xyz),False,False)
    a.set_actor_scale3d(u.Vector(*scale))
    a.set_actor_enable_collision(False)
    a.set_folder_path('ClientHome/OptionalClues')
    if tag:a.set_editor_property('tags',[u.Name(tag)])
    return a
# Reuse the downloaded bowl, scaled to a small pet bowl beside the kitchen aisle.
prop('Snack_Bowl','/Game/StylizedKitchen/Meshes/SM_Wood_Bowl_A',(-520,190,23),(.9,.9,.9),tag='Home_Snack')
for i,(x,y,z) in enumerate([(-521,189,27),(-516,193,27),(-525,194,27),(-498,208,23.8),(-480,222,23.8)]):
    prop('Snack_Crumb'+str(i),'/Engine/BasicShapes/Sphere',(x,y,z),(.045,.035,.02),'M_CH_Soil')
# Three small paw prints point from the corridor toward the living room.
for i,(x,y,angle) in enumerate([(180,-520,-40),(228,-481,-30),(240,-424,-20)]):
    pad=prop('Pawprint'+str(i)+'_Pad','/Engine/BasicShapes/Sphere',(x,y,23.7),(.14,.12,.008),'M_CH_Soil','Home_Pawprints' if i==0 else None)
    pad.set_actor_rotation(u.Rotator(pitch=0,yaw=angle,roll=0),False)
    radians=math.radians(angle)
    for j,(dx,dy) in enumerate([(-6,5),(-2,9),(3,9),(7,5)]):
        dx,dy=1.4*(dx*math.cos(radians)-dy*math.sin(radians)),1.4*(dx*math.sin(radians)+dy*math.cos(radians))
        toe=prop('Pawprint'+str(i)+'_Toe'+str(j),'/Engine/BasicShapes/Sphere',(x+dx,y+dy,23.7),(.049,.063,.008),'M_CH_Soil')
        toe.set_actor_rotation(u.Rotator(pitch=0,yaw=angle,roll=0),False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('OPTIONAL_CLUES_PLACED: kitchen snack and corridor pawprints')
