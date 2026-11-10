"""Use the project's stock Manny and locomotion on the existing home Character."""
import unreal as u

def configure(player,B,A):
    source=u.get_default_object(u.load_asset('/Game/TopDown/Blueprints/BP_TopDownCharacter').generated_class())
    source_mesh=source.get_component_by_class(u.SkeletalMeshComponent)
    cdo=u.get_default_object(player.generated_class())
    capsule=cdo.get_component_by_class(u.CapsuleComponent)
    mesh=cdo.get_component_by_class(u.SkeletalMeshComponent)
    mesh.set_skeletal_mesh_asset(source_mesh.get_editor_property('skeletal_mesh_asset'))
    mesh.set_animation_mode(u.AnimationMode.ANIMATION_BLUEPRINT)
    mesh.set_anim_instance_class(source_mesh.get_editor_property('anim_class'))
    mesh.set_editor_property('relative_location',u.Vector(0,0,1-capsule.get_unscaled_capsule_half_height()))
    mesh.set_editor_property('relative_rotation',source_mesh.get_editor_property('relative_rotation'))
    mesh.set_editor_property('relative_scale3d',source_mesh.get_editor_property('relative_scale3d'))
    mesh.set_visibility(True)
    mesh.set_hidden_in_game(False)
    mesh.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    for body in A.get_components(cdo,u.StaticMeshComponent.static_class()):
        body.set_visibility(False)
        body.set_hidden_in_game(True)
        body.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
        body.set_editor_property('cast_shadow',False)
    cdo.set_editor_property('use_controller_rotation_yaw',False)
    movement=cdo.get_component_by_class(u.CharacterMovementComponent)
    movement.set_editor_property('orient_rotation_to_movement',True)
    movement.set_editor_property('rotation_rate',u.Rotator(pitch=0,yaw=640,roll=0))
    B.compile_blueprint(player,True)

if __name__=='__main__':
    from editor_toolset.toolsets.blueprint import BlueprintTools as B,_BlueprintCache
    from editor_toolset.toolsets.actor import ActorTools as A
    assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
    player=u.load_asset('/Game/ClientHome_Haeso/Blueprints/BP_CH_Player_Minimal')
    _BlueprintCache.invalidate(player)
    configure(player,B,A)
    assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(player)
    u.log('HOME_MANNY_SAVED')
