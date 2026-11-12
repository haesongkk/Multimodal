import bpy,bmesh,json,struct,math
from pathlib import Path
from mathutils import Quaternion,Vector
R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(R/'Detective_Retopology_v2.blend'))
parts=list(bpy.data.collections['01_Structured_Retopology'].objects)
report={'parts':{},'total_quads':0,'total_vertices':0,'previous_quads':3180,'textures_packed':True}
for o in parts:
    bm=bmesh.new();bm.from_mesh(o.data)
    s={'vertices':len(bm.verts),'quads':sum(len(f.verts)==4 for f in bm.faces),'other_faces':sum(len(f.verts)!=4 for f in bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'collapsed_edges':sum(e.calc_length()<1e-6 for e in bm.edges),'uv_layers':len(o.data.uv_layers)}
    assert s['other_faces']==s['boundary_edges']==s['nonmanifold_edges']==s['zero_area_faces']==s['collapsed_edges']==0,(o.name,s)
    assert s['uv_layers']==1
    report['parts'][o.name]=s;report['total_quads']+=s['quads'];report['total_vertices']+=s['vertices'];bm.free()
    o['source_url']='https://3d.varco.ai/studio/2cd4f90a-dfa0-442d-bb6b-fa506ebfcda7'
im=bpy.data.images['Detective_Retopo_BaseColor_2K'];assert im.packed_file and list(im.size)==[2048,2048]
report['quad_reduction_from_previous_percent']=round(100*(1-report['total_quads']/3180),2)
raw=(R/'Detective_Retopology_v2.glb').read_bytes();length,kind=struct.unpack_from('<II',raw,12);gltf=json.loads(raw[20:20+length])
report['glb_mesh_count']=len(gltf['meshes']);assert report['glb_mesh_count']==7
assert len(parts)==7 and report['total_quads']==2316
report['notes']=['7 closed parts overlap at clothing/hat boundaries; not welded into one deforming character.','Animation and facial deformation have not been validated.','Source projection approximates surface; original and previous mesh retained for comparison.','GLB triangulates quads; actual quad mesh is in the .blend.']
(R/'retopo_v2_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL'
            r=area.spaces.active.region_3d;r.view_rotation=Quaternion((1,0,0),math.pi/2);r.view_location=Vector((0,0,0));r.view_distance=1.6
bpy.data.texts['README_Retopology_v2'].write('\nValidated by reopening saved file: 2,316 quads, 7 closed manifold parts, no collapsed edges or zero-area faces, packed 2K atlas. GLB contains exactly 7 exported mesh parts.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Detective_Retopology_v2.blend'))
(R/'README_Retopology_v2.md').write_text('''# 탐정 캐릭터 리토폴로지 v2

`Detective_Retopology_v2.blend`가 새 편집용 파일입니다. 2K 색상 텍스처가 파일 안에 포함돼 있습니다.

- 01_Structured_Retopology: 눈 루프가 있는 얼굴, 연결된 코트/어깨/소매/다리, 모자 둘레 루프, 리본 2개, 두께가 있는 옷깃 2개. 총 7개 파트, 2,316 쿼드입니다.
- 00_Original_Source_ARCHIVE: 원본 보관. 기본 숨김.
- 02_Previous_Subdivision_ARCHIVE: 기존 3,180 쿼드 버전. 기본 숨김.

각 파트는 닫힌 메시지만 파트 사이 경계는 의상과 모자 접합부에서 겹치도록 구성했습니다. 하나로 용접된 애니메이션용 몸체는 아니며 관절/표정 변형은 검증하지 않았습니다.

원본에 맞춘 구조적인 패치와 눈/소매/모자 루프를 새로 만들었습니다. 단순 삼각형 세분화 방식이 아닙니다. 실루엣은 투영으로 근사했습니다. 옷깃은 별도 패치로 재구성했고 원본 코트의 파란색을 옮겼으므로 원본과 모양/색이 조금 다릅니다.

GLB는 내보낼 때 삼각형으로 변환됩니다. 실제 쿼드 편집은 .blend 파일에서 하세요.

재현 순서: rebuild_structured.py → bake_structured.py → transfer_nearest_texture.py → validate_retopo_v2.py. Blender 4.5의 --background --python 옵션으로 실행할 수 있습니다. 원본 경로와 파라미터는 스크립트에서 관리합니다.

검사 결과: retopo_v2_validation.json. 와이어 이미지: structured_wire_*.png. 색상 미리보기: retopo_v2_*.png.
''',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='parts'},indent=2))
