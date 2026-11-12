import bpy,bmesh,math,json,time
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Imported.blend'))
src=next(o for o in bpy.context.scene.objects if o.type=='MESH');src.name='00_SOURCE_BakeReference'
bm=bmesh.new();bm.from_mesh(src.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bm.to_mesh(src.data);bm.free()
verts=[v.co.copy() for v in src.data.vertices];polys=[list(p.vertices) for p in src.data.polygons]
tree=BVHTree.FromPolygons(verts,polys,all_triangles=True)
def subset(pred):
    ps=[p for p in polys if pred(sum((verts[i] for i in p),Vector())/len(p))]
    return BVHTree.FromPolygons(verts,ps,all_triangles=True)
headtree=subset(lambda c:.012<c.z<.245)
bodies=subset(lambda c:c.z<.085)
hatree=subset(lambda c:.218<c.z<.437)
bowtrees={s:subset(lambda c,s=s:c.z>.416 and c.x*s>-.012) for s in (-1,1)}
def rayfit(p,center,bvh=tree,far=False):
    p=Vector(p);center=Vector(center);d=p-center
    reach=2 if far else d.length*1.4+.008
    hit=bvh.ray_cast(center+d.normalized()*reach,-d.normalized(),reach+.02) if d.length>1e-8 else (None,None,None,None)
    if hit[0] is not None and (far or (hit[0]-p).length<.065):return hit[0]
    near=bvh.find_nearest(p)
    return near[0] if near[0] is not None else p
def make(name,vs,fs):
    m=bpy.data.meshes.new(name+'_Mesh');m.from_pydata(vs,[],fs);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    return o
def cuboid_boundary(nx,ny,nz,fn,skip_front=None):
    vs=[];fs=[];ids={}
    def get(i,j,k):
        key=(i,j,k)
        if key not in ids:ids[key]=len(vs);vs.append(fn(i/nx,j/ny,k/nz))
        return ids[key]
    # Grid patches; normals are recalculated afterwards.
    for i in range(nx):
        for k in range(nz):
            if not skip_front or not skip_front(i,k):fs.append([get(i,0,k),get(i+1,0,k),get(i+1,0,k+1),get(i,0,k+1)])
            fs.append([get(i,ny,k),get(i,ny,k+1),get(i+1,ny,k+1),get(i+1,ny,k)])
    for j in range(ny):
        for k in range(nz):
            fs.append([get(0,j,k),get(0,j,k+1),get(0,j+1,k+1),get(0,j+1,k)])
            fs.append([get(nx,j,k),get(nx,j+1,k),get(nx,j+1,k+1),get(nx,j,k+1)])
    for i in range(nx):
        for j in range(ny):
            fs.append([get(i,j,0),get(i,j+1,0),get(i+1,j+1,0),get(i+1,j,0)])
            fs.append([get(i,j,nz),get(i+1,j,nz),get(i+1,j+1,nz),get(i,j+1,nz)])
    return vs,fs,ids,get
# Head: regular face patches with two concentric eye loops (16 edges each).
xs=[-.15,-.125,-.105,-.085,-.065,-.045,-.025,0,.025,.045,.065,.085,.105,.125,.15]
zs=[.025,.045,.065,.085,.105,.125,.145,.165,.185,.205,.225]
holes=[(2,3), (8,3)]
def headpoint(u,v,w):
    x=xs[round(u*14)];z=zs[round(w*10)];y=-.15+.30*v
    center=Vector((0,.015,.128))
    q=rayfit((x,y,z),center,tree,far=True)
    if q.z>.230:q=center+(q-center)*((.230-center.z)/(q.z-center.z))
    if q.z<.035:q=center+(q-center)*((.035-center.z)/(q.z-center.z))
    return q
vs,fs,ids,get=cuboid_boundary(14,6,10,headpoint,lambda i,k:any(a<=i<a+4 and b<=k<b+4 for a,b in holes))
for a,b in holes:
    keys=[(a+i,0,b) for i in range(4)]+[(a+4,0,b+i) for i in range(4)]+[(a+4-i,0,b+4) for i in range(4)]+[(a,0,b+4-i) for i in range(4)]
    outer=[get(*k) for k in keys]
    cx=(xs[a]+xs[a+4])/2;cz=(zs[b]+zs[b+4])/2
    prev=outer
    for rx,rz in [(.032,.035),(.021,.024)]:
        ring=[]
        for n in range(16):
            theta=-3*math.pi/4+n*math.pi/8
            # Traversal follows square boundary: lower left -> right -> top -> left.
            p=(cx+rx*math.cos(theta),-.15,cz+rz*math.sin(theta))
            ring.append(len(vs));vs.append(rayfit(p,(0,.015,.128),headtree))
        for n in range(16):fs.append([prev[n],prev[(n+1)%16],ring[(n+1)%16],ring[n]])
        prev=ring
    # Cap eye disk with a 4x4 quad patch, not a triangle fan.
    disk={}
    boundary=[(i,0) for i in range(4)]+[(4,j) for j in range(4)]+[(4-i,4) for i in range(4)]+[(0,4-j) for j in range(4)]
    for n,key in enumerate(boundary):disk[key]=prev[n]
    for i in range(1,4):
        for j in range(1,4):
            u=(i-2)/2;w=(j-2)/2
            x=cx+.021*u*math.sqrt(1-w*w/2);z=cz+.024*w*math.sqrt(1-u*u/2)
            disk[(i,j)]=len(vs);vs.append(rayfit((x,-.15,z),(0,.015,.128),headtree))
    for i in range(4):
        for j in range(4):fs.append([disk[(i,j)],disk[(i+1,j)],disk[(i+1,j+1)],disk[(i,j+1)]])
head=make('01_Head_EyeLoop_Patches',vs,fs)
# Coat, arms, hands, neck and legs: surface of a deliberately laid out block grid.
# Shared grid edges form actual connected shoulder/hip branches.
X=[-.414,-.390,-.365,-.330,-.290,-.250,-.210,-.170,-.135,-.110,-.075,-.045,-.0225,0,.0225,.045,.075,.110,.135,.170,.210,.250,.290,.330,.365,.390,.414]
Y=[-.12,-.09,-.06,-.03,0,.03,.06,.09,.12]
Z=[-.492,-.472,-.447,-.420,-.395,-.370,-.350,-.320,-.285,-.250,-.215,-.180,-.145,-.110,-.075,-.050,-.025,0,.025,.050,.073]
def occupied(x,y,z):
    if -.350<z<.025 and abs(x)<.135:return True
    if abs(x)<.365 and abs(y)<.06 and -.075<z<.025:return True
    if .365<abs(x)<.414 and abs(y)<.03 and -.050<z<0:return True
    if .025<z<.073 and abs(x)<.045 and abs(y)<.06:return True
    if z<-.350 and .0225<abs(x)<.110 and abs(y)<.06:return True
    return False
cells={(i,j,k) for i in range(len(X)-1) for j in range(len(Y)-1) for k in range(len(Z)-1) if occupied((X[i]+X[i+1])/2,(Y[j]+Y[j+1])/2,(Z[k]+Z[k+1])/2)}
vs=[];fs=[];vid={}
def bodypoint(i,j,k):
    x,y,z=X[i],Y[j],Z[k]
    if z<=-.350 and .0224<abs(x)<.111 and abs(y)<=.0601:
        # Legs have circumferential loops; toe loops continue into the shoes.
        cx=math.copysign(.069,x)
        pp=Vector((x,y,z))
        if y<0 and z<-.42:pp.y-=.06*min(1,(-z-.42)/.05)*(-y/.06)
        if abs(z+.350)<1e-5:return pp
        if z<-.472:center=(cx,-.015,-.450)
        else:center=(cx,-.005,z)
    elif abs(x)>=.135 and -.0751<=z<=.0251:
        pp=Vector((x,y,z))
        # Endpoint ray directions include X to keep cap vertices distinct.
        center=(math.copysign(min(abs(x)-(.008 if abs(x)>.33 else 0),.375),x),0,-.026)
        if abs(x)>.365: pp.y*=.75
    else:
        width=.145+(.035*max(0,min(1,(-z-.13)/.22)))
        pp=Vector((x*width/.135,y*(1.13 if y<0 else 1.05),z))
        center=(0,0,z)
        if z>=.025:center=(0,0,.015)
    if abs(z+.350)<1e-5:
        q=rayfit(pp,(0,0,z),bodies)
        radius=max(abs(x)/.135,abs(y)/.12)
        return Vector((q.x*radius,q.y*radius,z))
    q=rayfit(pp,center,bodies)
    if z>=.025 and abs(x)<.136:q.z=z
    if z==-.350 and not (.0224<abs(x)<.111 and abs(y)<=.0601):q.z=-.350
    return q
def bi(p):
    if p not in vid:vid[p]=len(vs);vs.append(bodypoint(*p))
    return vid[p]
sides=[((-1,0,0),[(0,0,0),(0,0,1),(0,1,1),(0,1,0)]),((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),((0,0,-1),[(0,0,0),(0,1,0),(1,1,0),(1,0,0)]),((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)])]
for i,j,k in sorted(cells):
    for d,corner in sides:
        if (i+d[0],j+d[1],k+d[2]) not in cells:fs.append([bi((i+a,j+b,k+c)) for a,b,c in corner])
body=make('02_Coat_Shoulder_Sleeve_Hip_Loops',vs,fs)
# Hat: concentric brim support loops and meridian rings on the crown.
boundary=[(i,0) for i in range(8)]+[(8,j) for j in range(8)]+[(8-i,8) for i in range(8)]+[(0,8-j) for j in range(8)]
dirs=[]
for i,j in boundary:
    q=Vector(((i-4)/4,(j-4)/4));q.normalize();dirs.append(q)
vs=[];fs=[];rings=[]
for z in [.224,.236,.246,.256,.267,.278,.300,.326,.352,.375,.395,.412,.425]:
    ring=[]
    for d in dirs:
        ring.append(len(vs));vs.append(rayfit((d.x*.24,d.y*.24,z),(0,.01,z),hatree,far=True))
    if rings:
        for n in range(32):fs.append([rings[-1][n],rings[-1][(n+1)%32],ring[(n+1)%32],ring[n]])
    rings.append(ring)
def diskcap(ring,top):
    dd={key:ring[n] for n,key in enumerate(boundary)}
    center=sum((vs[n] for n in ring),Vector())/32
    for i in range(1,8):
        for j in range(1,8):
            u=(i-4)/4;v=(j-4)/4
            # Bilinear radial cap stays under the bow, and under the head for the lower cap.
            radii=[(vs[n]-center).length for n in ring]
            rr=sum(radii)/len(radii)
            pp=Vector((center.x+rr*u*math.sqrt(1-v*v/2),center.y+rr*v*math.sqrt(1-u*u/2),center.z))
            dd[(i,j)]=len(vs);vs.append(pp)
    for i in range(8):
        for j in range(8):fs.append([dd[(i,j)],dd[(i+1,j)],dd[(i+1,j+1)],dd[(i,j+1)]])
diskcap(rings[0],False);diskcap(rings[-1],True)
hat=make('03_Hat_Brim_Crown_Rings',vs,fs)
bow=[]
for sign in (-1,1):
    center=Vector((sign*.062,.025,.456))
    def bp(u,v,w):
        p=(sign*.062+(u-.5)*.087,.025+(v-.5)*.155,.456+(w-.5)*.066)
        return rayfit(p,center,bowtrees[sign],far=True)
    vs,fs,_,_=cuboid_boundary(3,5,2,bp)
    bow.append(make('04_Bow_'+('L' if sign<0 else 'R')+'_Patches',vs,fs))
# Separate clean lapel strips: longitudinal seam edges follow the fold.
lapels=[]
for sign in (-1,1):
    rows=[((-.145,.045),(-.085,.065)),((-.115,-.015),(-.045,-.005)),((-.060,-.065),(.025,-.035))]
    vs=[];fs=[]
    for ri,row in enumerate(rows):
        a,b=row
        for t in (0,.5,1):
            x=(a[0]*(1-t)+b[0]*t)*sign;z=a[1]*(1-t)+b[1]*t
            depths=[(-.053,-.082),(-.078,-.122),(-.134,-.150)]
            yy=depths[ri][0]*(1-t)+depths[ri][1]*t
            vs.append(Vector((x,yy,z)))
    for k in range(2):
        for j in range(2):fs.append([k*3+j,k*3+j+1,(k+1)*3+j+1,(k+1)*3+j])
    flap=make('05_Lapel_'+('L' if sign<0 else 'R')+'_Fold_Patch',vs,fs)
    bpy.context.view_layer.objects.active=flap
    sm=flap.modifiers.new('Fold_Thickness','SOLIDIFY');sm.thickness=.002;sm.offset=0
    bpy.ops.object.modifier_apply(modifier=sm.name)
    flap['cloth_patch']=True;lapels.append(flap)
parts=[head,body,hat]+bow+lapels
# Remove unused grid vertices, but do not collapse any planned edge loops.
for o in parts:
    bm=bmesh.new();bm.from_mesh(o.data)
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    # At stepped cuff/hidden closure transitions a projection can land two
    # adjacent control points on one source edge. Relax only that local patch.
    for iteration in range(12):
        bad={v for e in bm.edges if e.calc_length()<1e-5 for v in e.verts}
        bad.update(v for f in bm.faces if f.calc_area()<1e-11 for v in f.verts)
        if not bad:break
        new={v:v.co.lerp(sum((e.other_vert(v).co for e in v.link_edges),Vector())/len(v.link_edges),.35) for v in bad}
        for v,p in new.items():v.co=p
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['method']='Structured anatomical quad patches projected onto the source; NOT triangle subdivision.'
    for f in o.data.polygons:f.use_smooth=False
def stats(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    st={'vertices':len(bm.verts),'faces':len(bm.faces),'quads':sum(len(f.verts)==4 for f in bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'min_edge_length':min(e.calc_length() for e in bm.edges)}
    bm.free();return st
report={o.name:stats(o) for o in parts};print(json.dumps(report,indent=2));(R/'structured_report.json').write_text(json.dumps(report,indent=2))
# Inspection save before UV baking.
src.hide_render=True;src.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Detective_Structured_Working.blend'))
# Neutral wire previews, saved before choosing final delivery geometry.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
grey=bpy.data.materials.new('InspectionBlue');grey.diffuse_color=(.42,.60,.72,1)
black=bpy.data.materials.new('WireBlack');black.diffuse_color=(.008,.008,.008,1)
for o in parts:
    o.data.materials.append(grey)
    w=o.copy();w.data=o.data.copy();scene.collection.objects.link(w);w.name=o.name+'_WIRE_PREVIEW';w.data.materials.clear();w.data.materials.append(black)
    m=w.modifiers.new('VisibleQuadEdges','WIREFRAME');m.thickness=.00055;m.use_replace=True;m.use_even_offset=False;m.use_relative_offset=False
camdata=bpy.data.cameras.new('Inspect');cam=bpy.data.objects.new('Inspect',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=1.18
for label,direction in [('front',(0,-3,0)),('quarter',(1.5,-3,.7)),('back',(0,3,0))]:
    cam.location=Vector(direction);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(R/('structured_wire_'+label+'.png'));bpy.ops.render.render(write_still=True)
