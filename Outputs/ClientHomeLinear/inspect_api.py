import unreal,json
r={}
for n in dir(unreal):
 if n.startswith('GeometryScript') and any(s in n for s in ['Boolean','PlaneCutOptions','CreateNewStaticMeshAssetOptions']):
  cls=getattr(unreal,n);r[n]=cls.__doc__
  for k in dir(cls):
   if 'plane_cut' in k:r[n+'.'+k]=getattr(cls,k).__doc__
from editor_toolset.toolsets.actor import ActorTools
bp=unreal.load_asset('/Game/Multimodal/02_Blueprints/Characters/Player/ClientHome/BP_CH_Player_Minimal')
gm=unreal.load_asset('/Game/Multimodal/02_Blueprints/Framework/ClientHome/BP_CH_GameMode_Minimal')
cdo=unreal.get_default_object(gm.generated_class());r['gamemode']={k:str(cdo.get_editor_property(k)) for k in ['default_pawn_class','player_controller_class','hud_class']}
(_linear_root/'api2.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
