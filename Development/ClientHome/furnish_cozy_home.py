"""Cozy lived-in furnishing pass, preserving clue and entrance circulation."""
import unreal as u,json
from pathlib import Path
base=Path('D:/Multimodal/Saved/ClientHome')
e=u.get_editor_subsystem(u.UnrealEditorSubsystem);assert not e.get_game_world()
assert e.get_editor_world().get_path_name().startswith('/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal.')
assert (base/'Lvl_ClientHome_Minimal.before-furnishing.umap').exists()
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
by={a.get_actor_label():a for a in actors.get_all_level_actors()}
report={'removed':[],'added':[]}
# Convert the old pantry shelves into a study, removing the redundant chair stack.
old=json.loads((base/'right-wall-report.json').read_text())['study']
for name in old:
 if name in ('SM_Bookshelf3','SM_Bookshelf4'):continue
 a=by.get(name)
 if a:
  assert not any(str(t).startswith('Home_') for t in a.tags)
  actors.destroy_actor(a);by.pop(name)
 report['removed'].append(name)
FAB='/Game/StylizedKitchen/Meshes/'
COCO='/Game/CocoDetective/Props/Meshes/SM_Prop_'
def prop(name,path,x,y,z=21,scale=(1,1,1),rot=(0,0,0),collision=False,ground=True):
 label='CH_Cozy_'+name;a=by.get(label)
 if not a:
  a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,z));a.set_actor_label(label);by[label]=a
 c=a.get_component_by_class(u.StaticMeshComponent);mesh=u.load_asset(path);assert mesh,path;c.set_static_mesh(mesh)
 a.set_actor_location(u.Vector(x,y,z),False,False);a.set_actor_scale3d(u.Vector(*scale));a.set_actor_rotation(u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False)
 if ground:
  center,extent=a.get_actor_bounds(False);p=a.get_actor_location();p.z+=z-(center.z-extent.z);a.set_actor_location(p,False,False)
 a.set_actor_enable_collision(collision);a.set_folder_path('ClientHome/CozyLiving');report['added'].append(label)
 return a
# Reading nook, kept well behind the broad middle passage.
prop('ReadingRug',FAB+'SM_Carpet_03',85,420,21.4,(1.8,1.2,1))
prop('ReadingChair',FAB+'SM_LeatherCouch',-15,415,21,(.9,.9,.9),(0,100,0),True)
table=prop('ReadingTable',FAB+'SM_TableBasse_01',155,410,21,(.8,.8,.8),(0,10,0),True)
center,extent=table.get_actor_bounds(False);top=center.z+extent.z
prop('OpenBook',FAB+'SM_BookOpen_01',143,403,top+.5,(.65,.65,.65),(0,8,0))
prop('TeaMug',COCO+'Mug_01',181,417,top+.5,(.8,.8,.8),(0,-10,0))
prop('ReadingLamp',COCO+'DeskLamp_01',174,438,top+.5,(.8,.8,.8),(0,160,0))
# Books on the existing shelf surfaces, with small irregularities rather than identical rows.
for case,cx in enumerate((26.6941,177.8081)):
 for row,z in enumerate((105,153,202)):
  for cluster,offset in enumerate((-48,17)):
   for i in range(5):
    book=1+(i+row+case+cluster)%6
    prop(f'Book_{case}_{row}_{cluster}_{i}',FAB+f'SM_Book_{book:02d}',cx+offset+i*8,628, z,(1.2,1.2,1.2),(90 if i<4 else 82,180,0))
# A softer foreground corner for Coco, away from the pawprint clue and door route.
prop('CatRug',FAB+'SM_Carpet_05',-70,-350,21.5,(1.65,1.35,1),(0,90,0))
prop('CatTree',COCO+'CatTree_01',-155,-405,22,(.8,.8,.8),(0,12,0),True)
prop('CatBed',COCO+'CatBed_01',50,-365,22,(1.3,1.3,1.3),(0,-8,0))
for i,(x,y,s) in enumerate([(-10,-270,.09),(12,-280,.07),(-27,-288,.06)]):
 a=prop('PlayBall'+str(i),'/Engine/BasicShapes/Sphere',x,y,22,(s,s,s))
 a.get_component_by_class(u.StaticMeshComponent).set_material(0,u.load_asset('/Game/CocoDetective/Materials/'+('MI_Coral' if i%2==0 else 'MI_Sage')))
# A long low rug gives the central circulation area a purpose without adding blockers.
prop('HallRunner',FAB+'SM_Carpet_05',130,50,21.3,(1.3,1.8,1),(0,90,0))
# Plants at the edges soften transitions between the study and the living room.
for name,x,y,s in [('StudyPlant',300,570,1.5),('CatPlant',115,-455,1.4)]:
 pot=prop(name+'Pot',FAB+'SM_FlowerPot_04',x,y,21,(s,s,s))
 p=pot.get_actor_location();prop(name+'Leaves',FAB+'SM_FlowersPlant_01',x,y,p.z+28.5*s,(s,s,s),ground=False)
# Warm diffuse fill prevents the newly furnished middle from sinking into black.
for name,pos,intensity,radius in [('ReadingGlow',(100,410,235),320,650),('CatCornerGlow',(-80,-270,245),230,650)]:
 label='CH_Cozy_'+name;a=by.get(label)
 if not a:a=actors.spawn_actor_from_class(u.PointLight,u.Vector(*pos));a.set_actor_label(label);by[label]=a
 c=a.get_component_by_class(u.PointLightComponent);c.set_mobility(u.ComponentMobility.MOVABLE)
 c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',intensity);c.set_editor_property('attenuation_radius',radius)
 c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',3600);c.set_editor_property('cast_shadows',False)
 a.set_folder_path('ClientHome/CozyLiving');report['added'].append(label)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(base/'cozy-furnishing-report.json').write_text(json.dumps(report,indent=2))
u.log('COZY_FURNISHING_SAVED: '+str({k:len(v) for k,v in report.items()}))
