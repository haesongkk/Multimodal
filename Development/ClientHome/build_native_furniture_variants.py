"""Replace prototype props with Fab furnishings and keep switchable reading variants."""
import unreal as u,json
from pathlib import Path
ROOT='/Game/ClientHome_Haeso';base=Path('D:/Multimodal/Saved/ClientHome')
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(ROOT+'/Maps/Lvl_ClientHome_Minimal.')
actors=u.get_editor_subsystem(u.EditorActorSubsystem);by={a.get_actor_label():a for a in actors.get_all_level_actors()}
if not (base/'example-furnishings.json').exists():
 import runpy
 runpy.run_path(str(Path(__file__).with_name('inspect_example_furniture.py')))
 by={a.get_actor_label():a for a in actors.get_all_level_actors()}
rows=json.loads((base/'example-furnishings.json').read_text());source={r['label']:r for r in rows}
for n in ['CatTree','CatBed','PlayBall0','PlayBall1','PlayBall2','ReadingLamp','TeaMug']:
 a=by.pop('CH_Cozy_'+n,None)
 if a:actors.destroy_actor(a)
def clone(label,row,pos,rotation=None,tag=None,collision=False):
 a=by.get(label)
 if not a:a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*pos));a.set_actor_label(label);by[label]=a
 c=a.get_component_by_class(u.StaticMeshComponent);c.set_static_mesh(u.load_asset(row['mesh']))
 for i,m in enumerate(row['materials']):
  if m:c.set_material(i,u.load_asset(m))
 a.set_actor_location(u.Vector(*pos),False,False);a.set_actor_scale3d(u.Vector(*row['scale']))
 p,y,r=rotation or row['rot'];a.set_actor_rotation(u.Rotator(pitch=p,yaw=y,roll=r),False)
 a.set_actor_enable_collision(collision)
 a.set_folder_path('ClientHome/NativeFurniture/'+(tag or 'Common'))
 if tag:a.set_editor_property('tags',[u.Name(tag)]+([u.Name('CH_FurnitureCollision')] if collision else []))
 return a
# Keep A as a real, reversible comparison, including its original bookcases.
a_names=['CH_Cozy_'+s for s in ['ReadingRug','ReadingChair','ReadingTable','OpenBook']]
a_names+=['SM_Bookshelf3','SM_Bookshelf4']+[n for n in by if n.startswith('CH_Cozy_Book_')]
for n in a_names:
 a=by[n];coll=a.actor_has_tag('CH_FurnitureCollision') or a.get_actor_enable_collision();a.set_editor_property('tags',[u.Name('CH_Reading_A')]+([u.Name('CH_FurnitureCollision')] if coll else []))
# Replace the prototype mug and lamp with matching textured source props.
center,extent=by['CH_Cozy_ReadingTable'].get_actor_bounds(False);top=center.z+extent.z
for label,src,pos in [('TeaCup','SM_Mug_A',(181,417,top+.5)),('Candle','SM_Candle8',(174,438,top+.5))]:
 a=clone('CH_Native_A_'+label,source[src],pos,tag='CH_Reading_A')
 o,e=a.get_actor_bounds(False);p=a.get_actor_location();p.z+=top+.5-(o.z-e.z);a.set_actor_location(p,False,False)
# The foreground gets the source map's writing desk with its authored arrangement.
for row in rows:
 x,y,z=row['pos'];name=row['label']
 if -290<x<50 and -350<y<-140 and not name.startswith(('Cube','House_')):
  pitch,yaw,roll=row['rot']
  clone('CH_Native_Desk_'+name,row,(-80+(y+250),-410-(x+190),z),(pitch,yaw-90,roll),collision=name=='Assets_Proxy_LR_Desk_Proxy')
chair=source['Vintage_Dining_Chair']
clone('CH_Native_Desk_Chair',chair,(-80,-285,21),(0,0,0),collision=True)
# Source library nook: retain relative positions, materials, scale, and all book dressing.
selected=[]
for row in rows:
 x,y,z=row['pos'];name=row['label']
 if -220<x<240 and 350<y<675 and not name.startswith(('Cube','House_')):
  coll=name in ['SM_LeatherCouch','SM_LeatherCouch2','SM_TableMin','SM_TableBasse_2','SM_Bookshelf','SM_Bookshelf2']
  clone('CH_Native_B_'+name,row,(x+90,y,z),tag='CH_Reading_B',collision=coll);selected.append(name)
# Start with A so matching screenshots can be captured before switching to B.
for a in by.values():
 for tag in ['CH_Reading_A','CH_Reading_B']:
  if a.actor_has_tag(tag):
   active=tag=='CH_Reading_A';a.set_actor_hidden_in_game(not active);a.set_is_temporarily_hidden_in_editor(not active)
   a.set_actor_enable_collision(active and a.actor_has_tag('CH_FurnitureCollision'))
   c=a.get_component_by_class(u.StaticMeshComponent)
   if c:c.set_editor_property('cast_hidden_shadow',False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(base/'native-furniture-report.json').write_text(json.dumps({'example_nook':selected,'active':'A','prototype_props_removed':7},indent=2))
u.log('NATIVE_FURNITURE_AB_READY')
