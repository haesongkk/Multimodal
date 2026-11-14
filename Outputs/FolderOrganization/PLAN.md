# 폴더 정리 실행 계획

상태: 2026-11-11 사용자 승인 후 정리 완료. 결과와 검증은 [RESULT.md](RESULT.md)를 참고한다.

## 대상

- 총 329개 일반 에셋·맵을 재배치한다. 엔진 관리용 외부 Actor·Object 패키지는 이 수에 포함하지 않는다.
- 실제 전체 목록: [move_manifest.json](move_manifest.json). 각 항목의 `path`는 현재 위치, `destination`은 이동 후 위치다.
- Fab의 NYCStreetProps는 `Content/ExternalAssets/NYCStreetProps`로 모은다. 내부 구조와 이름을 유지한다.
- 기본 템플릿의 Characters·LevelPrototyping·Cursor와 TopDown의 맵 외 콘텐츠는 `Content/ExternalAssets/UnrealTemplates` 아래로 옮긴다.
- 자체 제작 Blueprint는 `Content/Multimodal/02_Blueprints`, 그래픽은 `03_Graphics`, 입력은 `07_Settings/Input`으로 정리한다.
- Probe·ScaleGuide와 백업 맵은 `Content/Multimodal/90_Sandbox`로 정리한다. 삭제하지 않는다.

## 레벨 이름과 위치

| 현재 | 변경 후 |
|---|---|
| `CocoDetective/Maps/Lvl_Alley_Proto` | `Multimodal/01_Maps/Alley/LV_Alley_Proto` |
| `CocoDetective/Backups/Lvl_BeforePlaySetup` | `Multimodal/90_Sandbox/Maps/Backups/LV_BeforePlaySetup` |
| `CocoDetective/Backups/Lvl_BeforePropSeparation` | `Multimodal/90_Sandbox/Maps/Backups/LV_BeforePropSeparation` |
| `TopDown/Lvl_TopDown` | `Multimodal/01_Maps/TopDown/LV_TopDown` |

`LV_TopDown`의 원본은 World Partition·외부 Actor를 사용한다. 이 맵 이동은 외부 패키지 경로에도 영향을 주므로 별도 확인이 필요하다. 외부 Actor·Object 파일을 셸에서 직접 옮기지 않는다.

## 실행·검증

1. 실행 전에 현재 디스크 상태와 에디터 상태를 다시 확인한다.
2. Unreal Editor의 참조 보존 이동 API로 에셋을 옮긴다.
3. 레벨 이동·이름 변경을 적용하고 외부 Actor·Object 데이터가 보존되는지 확인한다.
4. 기본 맵·GameMode 등 Config의 문자열 경로를 변경 후 경로로 갱신한다.
5. 에디터에서 Redirector를 정리하고 관련 패키지를 저장한다.
6. 관련 Blueprint 컴파일, 맵 재열기, Actor 수·메시·머티리얼 참조와 PIE 시작을 확인한다.
7. 비어 있는 이전 폴더만 정리하고 결과를 기록한다.

## 복구 지점과 유지 대상

- 이동 전 에디터의 미저장 에셋 저장 성공을 확인했다.
- 디스크 사본: `Saved/FolderOrganizationBackup_20261111/Content`, `Config`, `Multimodal.uproject`.
- 기존 Git 변경과 추적되지 않은 에셋도 사본에 포함했다. Git reset이나 임의 삭제를 하지 않는다.
- `Saved`, `Intermediate`, `DerivedDataCache` 및 엔진 관리 폴더는 일반 폴더처럼 이동하지 않는다.
- 기존 `Outputs/VarcoCat`, `Outputs/VarcoDetective`의 작업 묶음은 스크립트·문서의 경로 의존성을 유지하기 위해 이번 에셋 이동 범위에서 제외한다.
- 레벨 접두사 `LV_`는 `PROJECT_RULES.md`와 레벨 4개에 반영했다.
