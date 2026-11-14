import bpy,bmesh,numpy as np,json,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Retopology_v2.blend'))
src=bpy.data.objects['00_SOURCE_BakeReference']
parts=sorted(list(bpy.data.collections['01_Structured_Retopology'].objects),key=lambda o:o.name)
source_mat=src.data.materials[0];pbs=next(n for n in source_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
im=pbs.inputs['Base Color'].links[0].from_node.image
sw,sh=im.size
pix=np.empty(sw*sh*4,dtype=np.float32);im.pixels.foreach_get(pix);pix=pix.reshape(sh,sw,4)
src.data.calc_loop_triangles();triangles=list(src.data.loop_triangles)
source_xyz=np.array([[src.data.vertices[i].co[:] for i in t.vertices] for t in triangles],dtype=np.float32)
source_uv=np.array([[src.data.uv_layers.active.data[i].uv[:] for i in t.loops] for t in triangles],dtype=np.float32)
tree=BVHTree.FromPolygons([v.co.copy() for v in src.data.vertices],[list(t.vertices) for t in triangles],all_triangles=True)
N=2048
atlas=np.zeros((N,N,4),dtype=np.float32);atlas[:,:,3]=1
mask=np.zeros((N,N),dtype=bool)
def sample(points,front_back=False):
    hits=[]
    for p in points:
        h=None
        if front_back and abs(p[1])>.015:
            yy=-1 if p[1]<0 else 1
            h=tree.ray_cast(Vector((p[0],yy,p[2])),Vector((0,-yy,0)))
        if h is None or h[0] is None:h=tree.find_nearest(Vector(p))
        hits.append(h)
    ix=np.array([h[2] for h in hits],dtype=np.int32)
    q=np.array([h[0][:] for h in hits],dtype=np.float32)
    a=source_xyz[ix,0];v0=source_xyz[ix,1]-a;v1=source_xyz[ix,2]-a;v2=q-a
    d00=(v0*v0).sum(1);d01=(v0*v1).sum(1);d11=(v1*v1).sum(1);d20=(v2*v0).sum(1);d21=(v2*v1).sum(1)
    den=d00*d11-d01*d01
    b=(d11*d20-d01*d21)/den;c=(d00*d21-d01*d20)/den
    uv=source_uv[ix,0]*(1-b-c)[:,None]+source_uv[ix,1]*b[:,None]+source_uv[ix,2]*c[:,None]
    xx=np.clip(uv[:,0]*sw-.5,0,sw-1);yy=np.clip(uv[:,1]*sh-.5,0,sh-1)
    x0=xx.astype(int);y0=yy.astype(int);x1=np.minimum(x0+1,sw-1);y1=np.minimum(y0+1,sh-1)
    wx=(xx-x0)[:,None];wy=(yy-y0)[:,None]
    return pix[y0,x0]*(1-wx)*(1-wy)+pix[y0,x1]*wx*(1-wy)+pix[y1,x0]*(1-wx)*wy+pix[y1,x1]*wx*wy
start=time.time();count=0
for ob in parts:
    me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active.data
    for t in me.loop_triangles:
        u=np.array([uv[i].uv[:] for i in t.loops],dtype=np.float32)*N-.5
        lo=np.maximum(np.floor(u.min(0)).astype(int),0);hi=np.minimum(np.ceil(u.max(0)).astype(int),N-1)
        if (hi<lo).any():continue
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
        v0=u[1]-u[0];v1=u[2]-u[0];den=v0[0]*v1[1]-v1[0]*v0[1]
        if abs(den)<1e-8:continue
        dx=xx-u[0,0];dy=yy-u[0,1]
        b=(dx*v1[1]-dy*v1[0])/den;c=(dy*v0[0]-dx*v0[1])/den
        inside=(b>=-1e-6)&(c>=-1e-6)&(b+c<=1.000001)
        if not inside.any():continue
        xp=xx[inside];yp=yy[inside];bb=b[inside];cc=c[inside]
        co=np.array([me.vertices[i].co[:] for i in t.vertices],dtype=np.float32)
        pts=co[0]+bb[:,None]*(co[1]-co[0])+cc[:,None]*(co[2]-co[0])
        query=pts.copy()
        if ob.name.startswith('05_Lapel'):
            query[:,0]=np.where(query[:,0]<0,-.09,.09);query[:,1]=-.12;query[:,2]=-.20+query[:,2]*.2
        elif ob.name.startswith('04_Bow'):
            query[:,2]=np.maximum(query[:,2],.459)
        color=sample(query,front_back=ob.name.startswith('02_Coat'))
        if ob.name.startswith('02_Coat'):
            pants=pts[:,2]<-.35001
            if pants.any():
                q=pts[pants].copy();q[:,2]=np.minimum(q[:,2],-.395)
                color[pants]=sample(q,front_back=True)
        atlas[yp,xp]=color;mask[yp,xp]=True;count+=len(xp)
    print('TRANSFERRED',ob.name,count,'pixels',round(time.time()-start,1),'s',flush=True)
# Extend island borders by 12 pixels, without changing filled UV texels.
for step in range(12):
    newmask=mask.copy();newatlas=atlas.copy()
    for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
        rolled=np.roll(mask,(dy,dx),(0,1));todo=rolled&~newmask
        newatlas[todo]=np.roll(atlas,(dy,dx),(0,1))[todo];newmask[todo]=True
    atlas,mask=newatlas,newmask
target=bpy.data.images['Detective_Retopo_BaseColor_2K']
target.pixels.foreach_set(atlas.ravel());target.update();target.filepath_raw=str(R/'Detective_Retopo_BaseColor_2K.png');target.file_format='PNG';target.save();target.pack()
notes=bpy.data.texts['README_Retopology_v2'];notes.write('\nColor transfer uses nearest source-triangle UV sampling per destination texel, followed by 12px island dilation. This avoids ray-bake misses around the collar and brim.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Detective_Retopology_v2.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(R/'Detective_Retopology_v2.glb'),use_selection=True)
# Color previews
mat=parts[0].data.materials[0];nt=mat.node_tree;tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8
scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='Standard'
if scene.world is None:scene.world=bpy.data.worlds.new('InspectionWorld')
scene.world.color=(.16,.16,.16)
cd=bpy.data.cameras.new('InspectionCamera');cam=bpy.data.objects.new('InspectionCamera',cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';cd.ortho_scale=1.18
for label,direction in [('front',(0,-3,0)),('quarter',(1.5,-3,.7)),('back',(0,3,0))]:
    cam.location=Vector(direction);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(R/('retopo_v2_'+label+'.png'));bpy.ops.render.render(write_still=True)
