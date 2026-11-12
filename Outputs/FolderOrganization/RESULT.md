# 폴더 정리 결과

2026-11-11 사용자 승인 범위의 에셋 329개와 관련 외부 Actor·Object 패키지를 Unreal Editor에서 이동·저장했다.

## 결과 구조

```text
Content/
├─ ExternalAssets/
│  ├─ NYCStreetProps/             # Fab 콘텐츠 26개
│  └─ UnrealTemplates/            # 기본 템플릿 콘텐츠 175개
└─ Multimodal/                    # 자체 제작·맵·실험 콘텐츠 128개
   ├─ 01_Maps/
   ├─ 02_Blueprints/
   ├─ 03_Graphics/
   ├─ 07_Settings/
   └─ 90_Sandbox/
```

`__ExternalActors__`, `__ExternalObjects__`, `Collections`, `Developers`는 엔진 관리 폴더로 유지했다.

- 기존 루트 `Characters`, `CocoDetective`, `Cursor`, `Level`, `LevelPrototyping`, `TopDown`은 비어 있음을 확인한 후 에디터 API로 제거했다.
- 기본 캐릭터 에셋 22개의 이전 경로 중복본은 별도 사용자 승인 후 새 경로 에셋으로 통합했다. 이전 파일이 백업과 동일함을 확인한 목록은 `repair_candidates_verified.json`에 기록했다.
- Unreal의 Update Redirector References에서 참조 갱신 성공을 확인한 뒤 참조 없는 리다이렉터를 정리했다. 최종 리다이렉터는 0개다.
- 기본 맵과 GameMode 경로를 Config 파일 및 실행 중인 에디터 설정 양쪽에 반영했다.

## 검증

- 이동 목록 329개 목적지 존재 확인.
- Blueprint 9개 컴파일: 모두 `BS_UP_TO_DATE`.
- 레벨 4개를 새 경로에서 다시 열어 Actor 수·이름이 이동 전과 일치함을 확인.
- Actor 수: 골목 263개, 플레이 설정 전 백업 87개, 소품 분리 전 백업 32개, TopDown 170개.
- 네 레벨 모두 메시가 없는 StaticMeshComponent 0개.
- 최종 검증 시 미저장 맵·콘텐츠 패키지 0개.
- PIE 실행 상태를 조회해 실행 중임을 확인하고 정상 종료했다. 최신 실행 로그에서 `BP_CocoDetectiveGameMode_C` 로드를 확인했으며 이전 경로 GameMode 누락은 해결했다.
- StartPIE 도구는 실행 성공 로그 및 실행 상태와 달리 `PIE ended before warmup completed`를 반환했다. 도구 응답만으로 성공 판정하지 않고 실제 상태와 로그를 함께 확인했다.
- 패키징 빌드는 실행하지 않았다.

## 기록·복구

- 전체 이동 목록: [move_manifest.json](move_manifest.json)
- 레벨 검증·컴파일 결과: [validation_final.json](validation_final.json)
- 최신 이동 전 백업: `Saved/FolderOrganizationBackup_Approved_73c256c6`
- 최초 백업: `Saved/FolderOrganizationBackup_20261111`
- 기존 `Outputs/VarcoCat`, `Outputs/VarcoDetective` 작업 묶음과 루트 참고 이미지는 이번 에셋 정리 범위 밖으로 유지했다.
