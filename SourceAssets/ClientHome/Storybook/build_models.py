"""Original crafted furniture for the fourth ClientHome comparison.
Independent geometry and materials; does not modify the first three styles.
"""
import bpy,math,random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=ROOT/'FBX';OUT.mkdir(exist_ok=True)
palette={'Walnut':(.19,.085,.038,1),'Oak':(.38,.21,.085,1),'Ivory':(.78,.69,.50,1),'Linen':(.65,.53,.34,1),'Sage':(.18,.29,.21,1),'DeepSage':(.08,.17,.14,1),'Clay':(.48,.20,.105,1),'Honey':(.57,.34,.09,1),'Ink':(.035,.065,.075,1),'Brass':(.52,.31,.08,1),'Art':(.8,.8,.8,1),'Glass':(.20,.38,.40,1)}
mats={};parts=[]
for n,c in palette.items():
 m=bpy.data.materials.new('M_CH_Story_'+n);m.diffuse_color=c;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=c;bs.inputs['Roughness'].default_value=.78 if n!='Brass' else .42;mats[n]=m
def assign(o,m):o.data.materials.append(mats[m]);parts.append(o);return o
def box(p,s,m='Walnut',b=1,seg=2):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Soft cut edges','BEVEL');mod.width=min(b,min(s)*.42);mod.segments=seg;bpy.ops.object.modifier_apply(modifier=mod.name)
 return assign(o,m)
def cyl(p,r,h,m='Brass',n=12,r2=None):
 bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r,radius2=r if r2 is None else r2,depth=h,location=p);return assign(bpy.context.object,m)
def orb(p,s,m='Sage',sub=1):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return assign(o,m)
def legs(w,d,h):
 for x in [-w,w]:
  for y in [-d,d]:cyl((x,y,h*.5),3.8,h,'Walnut',6,r2=5.1)
def armchair():
 legs(32,28,27);box((0,0,30),(80,74,13),'Walnut',3)
 box((0,-3,44),(69,66,18),'Honey',7,3)
 for x in [-40,40]:
  box((x,0,52),(16,77,43),'Honey',7,3);box((x,-1,73),(18,75,10),'Honey',4,3)
 back=box((0,31,77),(83,17,71),'Honey',7,3);back.rotation_euler.x=math.radians(-7)
 # inset cushion, piping and two subtle upholstery buttons
 pad=box((0,18,81),(67,9,46),'Linen',4,3);pad.rotation_euler.x=math.radians(-7)
 for x in [-17,17]:orb((x,11,83),(1.8,1,1.8),'Honey')
 pillow=box((-13,-2,59),(27,12,23),'DeepSage',4,3);pillow.rotation_euler.y=math.radians(-12)
def chair():
 legs(26,24,49);box((0,0,51),(65,62,8),'Walnut',3)
 box((0,-2,57),(58,55,9),'Sage',4,3)
 for x in [-26,26]:box((x,25,80),(6,7,60),'Walnut',2)
 box((0,25,105),(63,9,22),'Walnut',5,3);box((0,19,105),(51,3,12),'Sage',3)
 for x in [-10,10]:box((x,25,83),(5,6,26),'Oak',1)
def desk():
 legs(43,27,18);box((0,0,23),(100,63,9),'Walnut',2);box((0,0,75),(108,69,9),'Oak',3)
 for x in [-32,32]:
  box((x,0,48),(35,60,45),'Walnut',2)
  for z in [34,52,68]:
   box((x,-32,z),(31,4,13),'Oak',1);box((x,-35,z),(10,3,2),'Brass',.7)
 box((0,26,50),(28,5,40),'Walnut')
def shelf():
 box((0,17,100),(100,5,200),'Walnut')
 for x in [-48,48]:box((x,0,100),(7,42,200),'Oak',1.3)
 for z in [4,45,95,145,197]:box((0,0,z),(101,43,6),'Oak',1)
 box((0,0,203),(108,48,7),'Walnut',2);box((0,-21,200),(105,4,4),'Brass',.7)
 for x in [-24,24]:
  box((x,-23,24),(43,4,33),'Oak',1);box((x,-26,24),(34,2,23),'Walnut',1)
  orb((x+12,-29,29),(2,2,2),'Brass')
def cabinet(upper=False):
 box((0,0,45),(100,59,90),'DeepSage',1);box((0,0,93),(104,65,7),'Ivory',2)
 for x in [-25,25]:
  box((x,-31,46),(47,4,81),'Sage' if not upper else 'Ivory',1.5)
  box((x,-33.5,46),(36,1.5,67),'DeepSage' if not upper else 'Linen',1)
  box((x,-35,46),(31,1,62),'Sage' if not upper else 'Ivory',.5)
  box((x+16,-37,57),(3,4,16),'Brass',1)
def table():
 legs(40,26,64);box((0,0,59),(94,61,13),'Walnut',2);box((0,0,70),(109,76,9),'Oak',4,3)
 # understated inset tabletop border
 box((0,0,75),(99,66,1),'Walnut',1);box((0,0,75.6),(96,63,.5),'Oak',.5)
def fridge():
 box((0,0,99),(88,72,198),'DeepSage',5,3)
 for z,h in [(153,86),(52,105)]:
  box((0,-37,z),(86,9,h),'Ivory',4,3);box((30,-45,z),(4,8,25),'Brass',1.5)
 cyl((-25,-43,164),3,2,'Clay',8).rotation_euler.x=math.pi/2
def television():
 legs(29,16,22);box((0,0,54),(87,48,65),'Walnut',5,3)
 box((-8,-25,55),(62,4,49),'Brass',5,3);box((-8,-28,55),(56,3,43),'Ink',5,3);box((-8,-30,55),(47,1,34),'Glass',4,3)
 for z in [41,66]:cyl((33,-27,z),5,4,'Ivory',12).rotation_euler.x=math.pi/2
 for z in [48,52,56]:box((33,-28,z),(10,2,1),'Oak',0)
def pendant():
 cyl((0,0,106),14,6,'Walnut');cyl((0,0,75),1.5,59,'Ink',8)
 cyl((0,0,42),9,9,'Brass');cyl((0,0,21),33,35,'Ivory',12,r2=12)
 cyl((0,0,2.5),33,4,'Brass',12);cyl((0,0,1),27,1,'Linen',12)
def frame():
 box((0,0,40),(100,6,80),'Walnut',1.4);box((0,-4,40),(94,2,74),'Brass',.6);box((0,-5.5,40),(89,1,69),'Ivory',.3)
 # Dedicated UV canvas, front -Y, independent of the frame wood UVs.
 verts=[(-41,-6.2,9),(41,-6.2,9),(41,-6.2,71),(-41,-6.2,71)]
 me=bpy.data.meshes.new('Canvas');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('Canvas',me);bpy.context.collection.objects.link(o);assign(o,'Art')
 uv=me.uv_layers.new(name='UVMap')
 for i,v in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=v
def roundrug():
 for r,z,m in [(50,.5,'DeepSage'),(47,1.1,'Linen'),(45,1.5,'Honey'),(43,1.9,'Sage')]:cyl((0,0,z),r,.8,m,48)
 for i in range(32):
  t=i*math.tau/32;ob=box((math.cos(t)*46,math.sin(t)*46,2.1),(1,2,.2),'Walnut',0);ob.rotation_euler.z=t
def rug():
 for s,z,m in [((100,70,1),.5,'DeepSage'),((95,65,.5),1.1,'Linen'),((91,61,.4),1.5,'Clay'),((83,53,.3),1.9,'Sage')]:box((0,0,z),s,m,.2)
 for y in [-29,29]:
  for x in range(-40,45,5):box((x,y,2.1),(1.4,2,.2),'Linen',0)
def radiator():
 for x in range(-36,40,12):box((x,0,34),(9,18,68),'Ivory',3,3)
 for z in [10,55]:box((0,0,z),(85,10,7),'Brass',1)
def teapot():
 orb((0,0,16),(21,20,18),'Ivory',2);cyl((0,0,31),14,4,'Brass');orb((0,0,36),(4,4,3),'Walnut')
 o=cyl((-26,0,25),5,24,'Ivory',10,r2=8);o.rotation_euler.y=math.radians(-48)
 for z in [8,27]:box((26,0,z),(16,5,5),'Brass',2)
 box((34,0,17),(5,5,23),'Brass',2)
def export(name,fn):
 global parts
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[];fn()
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_CH_Story_'+name
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',object_types={'MESH'})
for n,fn in {'Armchair':armchair,'Chair':chair,'Desk':desk,'Bookshelf':shelf,'Cabinet':cabinet,'UpperCabinet':lambda:cabinet(True),'Table':table,'Fridge':fridge,'Television':television,'Pendant':pendant,'Frame':frame,'RoundRug':roundrug,'Rug':rug,'Radiator':radiator,'Teapot':teapot}.items():export(n,fn)
