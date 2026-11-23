# ClientHome 맵 비교

현재 비교 대상은 기존 스타일과 Storybook 스타일 두 가지다. 제품 맵을 교체한 상태가 아니므로 비교 맵과 전용 에셋은 `Content/Multimodal/90_Sandbox`에 둔다.

| 키 | 동작 |
|---|---|
| F1 | 기존 스타일 `LV_ClientHome_Original` |
| F2 | 새 스타일 `LV_ClientHome_Storybook` |
| F6 / F7 | 기존 카메라 각도 프리셋 조절 |

맵을 전환하면 플레이어 위치와 단서 조사 진행이 초기화된다. 기존 제품 맵 `Content/Multimodal/01_Maps/ClientHome/LV_ClientHome_Linear.umap`은 유지한다.

## 파일 배치

- 비교 맵: `Content/Multimodal/90_Sandbox/Maps/ClientHome`
- 비교용 GameMode·Player: `Content/Multimodal/90_Sandbox/Experiments/ClientHome/Framework`
- 새 스타일 리소스: 같은 실험 폴더의 `Storybook`
- 공용 소품: 같은 실험 폴더의 `Papercraft` (새 맵이 실제 참조하는 22개 에셋)
- Blender 제작 코드·FBX·그림 원본: `SourceAssets/ClientHome/Papercraft`, `SourceAssets/ClientHome/Storybook`
- 작업 스크립트·스크린샷·검증 보고서: `Outputs/ClientHomeStyles`, `Outputs/ClientHomeStorybook`

Papercraft 비교 맵과 Kenney 비교 맵은 삭제했다. 남아 있는 Papercraft 폴더는 독립 시안이 아니라 Storybook에 필요한 공용 소품이다. 제작 스크립트는 사용 중인 소품의 원본이므로 보존한다. 기존 에셋 경로를 불필요하게 변경하지 않는다.

## 미리보기

에디터의 `Outputs/ClientHomeLinear/editor_bridge.py`가 실행 중인 환경에서는 `Outputs/ClientHomeStyles/PreviewOriginal.ps1` 또는 `PreviewStorybook.ps1`로 실행한다. 일반 에디터에서는 위 비교 맵을 열어 Play하면 된다.

제공된 탐정 이미지는 아트 방향 참고이며, 플레이어 모델은 변경하지 않았다. 새 스타일은 원목·세이지·아이보리를 중심으로 가구, 패널 벽, 패브릭, 액자를 통일했다.

## 검증과 범위

두 맵의 F1/F2 전환 및 새 맵의 단서 5개 조사를 확인했다. 에셋 이름·외부 참조 검사는 `Outputs/ClientHomeStorybook/project_rules_audit.json`, 의존성 검사는 같은 폴더의 `asset_audit.json`을 참고한다.

제품 콘텐츠에서 이번 실험 에셋을 참조하지 않는다. 현재 설정에는 이 비교 맵 전용 Cooking 제외 규칙이 없으며, Sandbox 경로 자체가 빌드 제외를 보장하지 않는다. 패키징 빌드는 이번 검증 범위에 포함하지 않았다. 정식 제품 맵으로 채택할 때는 `PROJECT_RULES.md`에 따라 제품 경로로 옮기고 참조와 Cooking 대상을 갱신한다.
