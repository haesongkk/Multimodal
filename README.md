# Multimodal

Unreal Engine 5.8 기반 Blueprint 프로젝트입니다.

- [폴더·파일·에셋 규칙](PROJECT_RULES.md)
- [의뢰인 집 구현 및 플레이 안내](Docs/ClientHome/README.md)
- [프로젝트 정리·검증 기록](Docs/ProjectOrganization.md)

의뢰인 집 실행: `Build/Tools/ClientHome/Launch-ClientHomeEditor.ps1`.
현재 맵: `/Game/Multimodal/01_Maps/ClientHome/LV_ClientHome_Minimal`.
기본 Town 맵: `/Game/Multimodal/01_Maps/Town/LV_CocoDetective_Town`.
자체 콘텐츠는 `Content/Multimodal`의 역할별 분류에, 외부 리소스는 `Content/ExternalAssets`의 제품별 폴더에 있습니다.
외부 Fab 팩은 각자의 라이브러리에서 확보하고 `Content/ExternalAssets/StylizedKitchen`에 배치합니다. 공급자 설치 경로에서 옮길 때는 Unreal Editor로 참조를 보존하세요.
