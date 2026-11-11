"""Fixed-angle, bounded camera follow for the entire furnished house."""
from pathlib import Path
import unreal as u

def configure(player, B, A):
    cdo=u.get_default_object(player.generated_class())
    camera=A.get_components(cdo,u.CameraComponent.static_class())[0]
    camera.set_editor_property('absolute_location',True)
    camera.set_editor_property('absolute_rotation',True)
    camera.set_editor_property('relative_location',u.Vector(378,-650,720))
    camera.set_editor_property('relative_rotation',u.Rotator(pitch=-35,yaw=90,roll=0))
    camera.set_editor_property('use_pawn_control_rotation',False)
    camera.set_editor_property('field_of_view',60)
    camera.set_editor_property('constrain_aspect_ratio',True)
    camera.set_editor_property('aspect_ratio',16/9)
    graph=B.get_graph(player,'EventGraph')
    getters=[n for n in B.find_node_types(graph,'GetViewCamera') if n.startswith('Variables|') and n.endswith('|GetViewCamera')]
    assert len(getters)==1,getters
    nodes=[getters[0],'Transformation|GetActorLocation','Transformation|GetWorldLocation',
           'Transformation|SetWorldLocation','Math|Vector|MakeVector','Math|Interpolation|VInterpTo']
    for node in nodes:B.get_node_type_pins(graph,node)
    cam='('+getters[0]+')'
    def clamp(v,lo,hi):return f'(select (< {v} {lo}) {lo} (select (> {v} {hi}) {hi} {v}))'
    # Look straight from the old left wall (-Y) toward the right wall (+Y).
    x=clamp('(.x position)',-650.,750.)
    y='(- '+clamp('(.y position)',-350.,430.)+' 1000.0)'
    target=f'(Math|Vector|MakeVector :X {x} :Y {y} :Z 720.0)'
    desired='(bind position (Transformation|GetActorLocation))\n(bind destination '+target+')\n'
    code='(event EventBeginPlay\n'+desired+'(Transformation|SetWorldLocation :self '+cam+' :NewLocation destination))\n'
    code+='(event EventTick (DeltaSeconds)\n'+desired+'(Transformation|SetWorldLocation :self '+cam+' :NewLocation (Math|Interpolation|VInterpTo :Current (Transformation|GetWorldLocation :self '+cam+') :Target destination :DeltaTime DeltaSeconds :InterpSpeed 3.5)))\n'
    B.write_graph_dsl(graph,code)
    (Path(__file__).parent/'BP_CH_Minimal_Player.dsl').write_text(code,encoding='utf-8')
    B.compile_blueprint(player,True)
