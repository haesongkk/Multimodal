"""World-space paw hints. All screen-space journal text is rendered by UMG."""
def make_hud(graph,B):
    B.get_node_type_pins(graph,'HUD|Project')
    B.get_node_type_pins(graph,'HUD|DrawTexture')
    B.get_node_type_pins(graph,'Math|Vector|MakeVector')
    get=lambda n:'(Variables|Default|Get'+n+')'
    out=['(event EventReceiveDrawHUD (SizeX SizeY)','(if (not '+get('Popup')+')']
    for i,actor,seen in [(1,'PotActor','PotSeen'),(2,'FurActor','FurSeen'),(3,'WindowActor','WindowSeen'),(4,'ExitActor','Deduced'),(5,'SnackActor','SnackSeen'),(6,'PawprintsActor','PawprintsSeen')]:
        target=get(actor);point='paw'+str(i)
        cond=f'(< (Transformation|GetHorizontalDistanceTo :self (HUD|GetOwningPawn) :OtherActor {target}) 300.0)'
        if i==4:cond=f'(and {get("Deduced")} {cond})'
        tint='"(R=0.95,G=0.65,B=0.38,A=1)"'
        location=f'(Transformation|GetActorLocation :self {target})'
        if i==3:
            # The open sash pivot is outside the house. Bring its hint inside
            # the window opening, below the upper-left journal panel.
            location=f'(Math|Vector|MakeVector :X (- (.x {location}) 90.0) :Y (.y {location}) :Z (- (.z {location}) 65.0))'
        out += [f'(if {cond}',f'(bind {point} (HUD|Project :Location {location}))',
            f'(HUD|DrawTexture :Texture "/Game/Multimodal/04_UI/Textures/ClientHome/T_PawStamp.T_PawStamp" :ScreenX (- (.x {point}) 12.0) :ScreenY (- (.y {point}) 24.0) :ScreenW 24.0 :ScreenH 24.0 :TextureU 0.0 :TextureV 0.0 :TextureUWidth 1.0 :TextureVHeight 1.0 :TintColor {tint})',')']
    return '\n'.join(out+['))'])+'\n'
