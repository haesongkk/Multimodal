"""Original faceted furniture authored for the ClientHome style comparison.
Run with Blender 3.3 background. Units are centimeters; front is -Y.
"""
import bpy, math, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent
OUT=ROOT/'FBX';OUT.mkdir(exist_ok=True)
random.seed(31)
colors={'Wood':(0.28,.13,.065,1),'Oak':(.56,.32,.13,1),'Cream':(.88,.75,.52,1),'Paper':(.95,.88,.70,1),'Teal':(.10,.32,.34,1),'Blue':(.12,.29,.48,1),'Ochre':(.76,.43,.10,1),'Rose':(.56,.22,.19,1),'Leaf':(.22,.40,.20,1),'Dark':(.055,.075,.09,1),'Brass':(.72,.49,.17,1),'Water':(.20,.55,.62,1)}
mats={}
for name,color in colors.items():
 m=bpy.data.materials.new('M_Paper_'+name);m.diffuse_color=color;m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.86;mats[name]=m
parts=[]
def finish(o,name):
 o.data.materials.append(mats[name]);parts.append(o);return o
def box(p,s,m='Wood',bevel=1.0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Cut paper edges','BEVEL');mod.width=min(bevel,min(s)*.18);mod.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,m)
def cyl(p,r,d,m='Cream',n=10,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=d,location=p);return finish(bpy.context.object,m)
def ball(p,s,m='Leaf'):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,m)
def legset(w,d,h,m='Wood'):
 for x in [-w,w]:
  for y in [-d,d]:box((x,y,h/2),(7,7,h),m)
def chair(arm=False):
 legset(32,28,32);box((0,0,37),(78,70,14),'Oak');box((0,-2,47),(66,62,12),'Ochre' if arm else 'Teal',3)
 box((0,29,76),(76,14,64),'Ochre' if arm else 'Teal',4)
 if arm:
  for x in [-39,39]:box((x,0,61),(16,73,30),'Ochre',3)
def table(desk=False):
 legset(40,26,64);box((0,0,68),(100,70,9),'Oak',2)
 if desk:
  for z in [23,44,62]:
   box((29,0,z),(36,58,17),'Wood');box((29,-31,z),(32,3,14),'Oak');box((29,-34,z),(12,4,3),'Brass')
def shelf():
 box((0,15,100),(100,5,200),'Wood')
 for x in [-47,47]:box((x,0,100),(6,40,200),'Oak')
 for z in [5,45,95,145,197]:box((0,0,z),(100,42,6),'Oak')
 for x in [-24,24]:
  box((x,-22,24),(45,4,35),'Wood');cyl((x,-26,24),2,3,'Brass').rotation_euler.x=math.pi/2
def cabinet(upper=False):
 box((0,0,45),(100,58,90),'Teal');box((0,0,93),(104,63,7),'Paper')
 for x in [-25,25]:
  box((x,-30,46),(47,3,82),'Cream' if upper else 'Teal');box((x+15,-33,57),(3,4,18),'Brass')
def fridge():
 box((0,0,98),(90,70,196),'Cream',4)
 for z,h in [(147,90),(48,91)]:box((0,-37,z),(85,5,h),'Paper',2);box((30,-42,z),(4,6,25),'Brass')
 box((-15,-41,139),(24,1,26),'Rose',0);box((12,-41,61),(25,1,19),'Blue',0)
def stove():
 box((0,0,45),(90,65,90),'Teal');box((0,0,92),(94,69,5),'Paper')
 for x in [-23,23]:
  for y in [-16,16]:cyl((x,y,96),15,2,'Dark',12);cyl((x,y,98),8,2,'Brass')
 box((0,-34,45),(70,3,52),'Dark');box((0,-38,69),(65,5,4),'Brass')
 for x in [-28,-9,9,28]:cyl((x,-35,82),4,3,'Brass').rotation_euler.x=math.pi/2
def tub():
 for x in [-37,37]:
  for y in [-18,18]:box((x,y,6),(8,8,12),'Brass')
 box((0,0,27),(105,58,30),'Cream',5);box((0,0,44),(100,55,6),'Water',4)
 for x in [-52,52]:box((x,0,43),(10,62,27),'Paper',4)
 for y in [-29,29]:box((0,y,43),(107,9,27),'Paper',4)
def toilet():
 cyl((0,-5,17),16,34,'Cream',8,r2=23);box((0,23,47),(46,18,64),'Cream',3)
 cyl((0,-8,40),28,12,'Paper',12);cyl((0,-8,47),19,2,'Dark',12);box((15,12,70),(8,4,3),'Brass')
def sink():
 box((0,0,40),(60,42,80),'Teal');box((0,0,83),(68,48,7),'Cream');box((0,0,87),(47,30,2),'Dark',4)
 cyl((0,18,97),3,26,'Brass',8);box((0,10,109),(6,20,5),'Brass')
def book():
 box((0,0,25),(18,35,50),'Rose',.5);box((2,-1,25),(16,31,45),'Paper',0)
 for z in [10,40]:box((-9,-.5,z),(1,34,2),'Brass',0)
def pot(plant=False):
 cyl((0,0,19),15,38,'Rose',9,r2=24);cyl((0,0,39),25,7,'Cream',9);cyl((0,0,43),20,2,'Wood',9)
 if plant:
  cyl((0,0,65),2,46,'Wood',6)
  for i in range(5):
   t=i*2.4;ball((math.cos(t)*13,math.sin(t)*13,64+i*6),(15,10,21),'Leaf')
def bottle():cyl((0,0,25),15,50,'Teal',8);cyl((0,0,58),6,20,'Teal',8);cyl((0,0,69),7,5,'Brass',8)
def bowl():cyl((0,0,10),12,20,'Cream',12,r2=24);cyl((0,0,21),21,2,'Wood',12)
def mug():
 cyl((0,0,20),17,40,'Cream',10);cyl((0,0,41),14,2,'Dark',10)
 for p,s in [((22,0,32),(15,7,6)),((28,0,22),(6,7,25)),((22,0,10),(15,7,6))]:box(p,s,'Cream')
def frame():
 box((0,0,40),(100,5,80),'Wood');box((0,-3,40),(88,2,68),'Cream');box((0,-5,40),(78,1,58),'Blue',0)
 ball((-18,-7,48),(18,1,18),'Ochre');box((15,-7,27),(40,1,19),'Teal',0)
def clock():
 o=cyl((0,0,0),45,8,'Wood',12);o.rotation_euler.x=math.pi/2
 o=cyl((0,-5,0),39,2,'Paper',12);o.rotation_euler.x=math.pi/2
 box((0,-8,11),(3,2,25),'Dark');box((10,-8,0),(24,2,3),'Dark')
 for i in range(12):
  t=i*math.pi/6;box((math.sin(t)*32,-8,math.cos(t)*32),(3,1,3),'Brass',0)
def tv():
 legset(30,15,22);box((0,0,55),(85,45,65),'Wood',4);box((-7,-24,55),(58,4,48),'Dark',3);box((-7,-27,55),(48,1,38),'Teal',3)
 for z in [42,65]:cyl((32,-25,z),5,3,'Brass',8).rotation_euler.x=math.pi/2
def rug():
 box((0,0,1),(100,70,2),'Teal',0);box((0,0,2.1),(91,61,.4),'Cream',0);box((0,0,2.4),(84,54,.3),'Rose',0)
 for x in range(-35,40,10):box((x,0,2.7),(2,50,.2),'Ochre',0)
def lamp():
 cyl((0,0,106),15,6,'Wood');cyl((0,0,72),3,68,'Brass',8);cyl((0,0,19),34,38,'Cream',8,r2=18)
def window():
 box((0,0,60),(90,6,120),'Wood');box((0,-4,60),(78,2,108),'Water',0)
 box((0,-7,60),(5,4,112),'Cream');box((0,-7,60),(80,4,5),'Cream');box((0,-7,3),(105,17,6),'Oak')
def door():
 box((0,0,100),(90,8,200),'Teal');box((0,-5,132),(67,3,100),'Cream');box((0,-5,37),(67,3,45),'Oak');ball((32,-11,85),(4,4,4),'Brass')
def radio():
 box((0,0,25),(80,30,50),'Wood',3);box((-10,-16,25),(45,2,35),'Cream')
 for x in range(-28,11,6):box((x,-18,25),(2,2,30),'Wood',0)
 for z in [15,35]:cyl((27,-17,z),6,4,'Brass').rotation_euler.x=math.pi/2
def microwave():
 box((0,0,25),(85,55,50),'Cream');box((-8,-29,25),(57,3,35),'Dark');box((30,-30,25),(4,5,28),'Brass')
def pan():
 cyl((0,0,7),30,14,'Dark',12,r2=35);cyl((0,0,15),29,1,'Wood',12);box((0,-52,9),(10,45,7),'Wood')
def utensil():box((0,0,30),(5,5,60),'Oak');ball((0,0,65),(12,5,15),'Cream')
def paper():box((0,0,1),(70,50,2),'Paper',0);box((0,0,2.1),(50,2,.3),'Rose',0)
def trash():cyl((0,0,30),23,60,'Teal',10,r2=28);cyl((0,0,62),29,4,'Wood',10)
def export(name,fn):
 global parts
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[];fn()
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CH_Paper_'+name
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,object_types={'MESH'})
models={'Armchair':lambda:chair(True),'Chair':chair,'Desk':lambda:table(True),'Table':table,'Bookshelf':shelf,'Cabinet':cabinet,'UpperCabinet':lambda:cabinet(True),'Fridge':fridge,'Stove':stove,'Bathtub':tub,'Toilet':toilet,'Sink':sink,'Book':book,'Pot':pot,'Plant':lambda:pot(True),'Bottle':bottle,'Bowl':bowl,'Mug':mug,'Frame':frame,'Clock':clock,'Television':tv,'Rug':rug,'Lamp':lamp,'Window':window,'Door':door,'Radio':radio,'Microwave':microwave,'Pan':pan,'Utensil':utensil,'Paper':paper,'Trash':trash,'Fruit':lambda:ball((0,0,15),(15,15,15),'Ochre'),'Box':lambda:box((0,0,30),(40,25,60),'Cream'),'Plate':lambda:cyl((0,0,2),30,4,'Paper',12),'Candle':lambda:cyl((0,0,25),8,50,'Cream',8),'Cloth':lambda:box((0,0,1),(60,45,2),'Teal',0)}
for name,fn in models.items():export(name,fn)
print('AUTHORED_MODELS',len(models))
