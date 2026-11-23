import unreal as u,json,math
from pathlib import Path
exec(Path('D:/Multimodal/Outputs/ClientHomeStyles/build_style_map.py').read_text().rsplit('build(STYLE)',1)[0])
SB='/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Storybook'
def polish():
 assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_name()=='LV_ClientHome_Storybook'
 records={r['label']:r for r in json.loads((ROOT/'Outputs/ClientHomeLinear/style_inventory.json').read_text())}
 bounds=json.loads((ROOT/'Outputs/ClientHomeLinear/style_mesh_bounds.json').read_text())
 mesh=u.load_asset('/Game/Multimodal/90_Sandbox/Experiments/ClientHome/Papercraft/Meshes/SM_CH_Paper_Clock')
 assert mesh
 for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
  r=records.get(a.get_actor_label())
  if not r or category(r['mesh'].split('.')[-1])[0]!='Clock':continue
  a.set_actor_location(u.Vector(*r['pos']),False,True);a.set_actor_rotation(u.Rotator(pitch=r['rot'][0],yaw=r['rot'][1],roll=r['rot'][2]),True);a.set_actor_scale3d(u.Vector(*r['scale']))
  b=bounds[r['mesh']];ext=[y-x for x,y in zip(b['min'],b['max'])];choices=[90,270] if ext[0]<ext[1] else [0,180];tr=a.get_actor_transform()
  def score(t):
   d=u.MathLibrary.transform_location(tr,u.Vector(-math.sin(math.radians(t)),math.cos(math.radians(t)),0))-a.get_actor_location();return -d.y
  c=a.get_component_by_class(u.StaticMeshComponent);fit(a,c,mesh,max(choices,key=score),b)
  for i,slot in enumerate(mesh.static_materials):
   n=slot.material_interface.get_name().replace('M_Paper_','')
   alias={'Wood':'Walnut','Cream':'Ivory','Paper':'Ivory','Dark':'Ink','Brass':'Brass','Teal':'Sage'}.get(n,'Ivory')
   c.set_material(i,u.load_asset(SB+'/Materials/M_CH_Story_'+alias))
 assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
polish()
