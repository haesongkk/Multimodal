# 탐정 캐릭터 리토폴로지 v2

`Detective_Retopology_v2.blend`가 새 편집용 파일입니다. 2K 색상 텍스처가 파일 안에 포함돼 있습니다.

- 01_Structured_Retopology: 눈 루프가 있는 얼굴, 연결된 코트/어깨/소매/다리, 모자 둘레 루프, 리본 2개, 두께가 있는 옷깃 2개. 총 7개 파트, 2,316 쿼드입니다.
- 00_Original_Source_ARCHIVE: 원본 보관. 기본 숨김.
- 02_Previous_Subdivision_ARCHIVE: 기존 3,180 쿼드 버전. 기본 숨김.

각 파트는 닫힌 메시지만 파트 사이 경계는 의상과 모자 접합부에서 겹치도록 구성했습니다. 하나로 용접된 애니메이션용 몸체는 아니며 관절/표정 변형은 검증하지 않았습니다.

원본에 맞춘 구조적인 패치와 눈/소매/모자 루프를 새로 만들었습니다. 단순 삼각형 세분화 방식이 아닙니다. 실루엣은 투영으로 근사했습니다. 옷깃은 별도 패치로 재구성했고 원본 코트의 파란색을 옮겼으므로 원본과 모양/색이 조금 다릅니다.

GLB는 내보낼 때 삼각형으로 변환됩니다. 실제 쿼드 편집은 .blend 파일에서 하세요.

재현 순서: rebuild_structured.py → bake_structured.py → transfer_nearest_texture.py → validate_retopo_v2.py. Blender 4.5의 --background --python 옵션으로 실행할 수 있습니다. 원본 경로와 파라미터는 스크립트에서 관리합니다.

검사 결과: retopo_v2_validation.json. 와이어 이미지: structured_wire_*.png. 색상 미리보기: retopo_v2_*.png.
