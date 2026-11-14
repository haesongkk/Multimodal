# 프로젝트 정리 기록

최종 전체 구조 재구성: 2026-11-13 (KST). 사용자 요청은 기존 콘텐츠까지 역할별로 전면 재분류하고 동작을 유지하는 것이다. 최초 11월 11일 작업에서 기존 경로 보존 예외를 적용한 범위는 아래 전체 재구성으로 대체했다. 현재 규칙은 [PROJECT_RULES.md](../PROJECT_RULES.md)에 있다.

## 2026-11-13 전체 재구성

`Content`의 일반 콘텐츠 최상위는 자체 콘텐츠 `Multimodal`, 외부 콘텐츠 `ExternalAssets`다. `__ExternalActors__`, `__ExternalObjects__`, `Collections`, `Developers`는 엔진 관리 폴더로 유지하며 비어 있어도 에디터가 다시 생성할 수 있다. 기존 `Characters`, `CocoDetective`, `Cursor`, `LevelPrototyping`, `TopDown`은 남기지 않았다.

- 기존 자체 콘텐츠 126개를 맵·Blueprint·그래픽·입력·이펙트·실험 분류로 이동했다. 기본 게임 맵은 `Multimodal/01_Maps/Town/LV_CocoDetective_Town`, 보관용 맵은 `90_Sandbox/Maps/CocoDetective`다.
- 마네킹 128개는 `ExternalAssets/UnrealMannequins`, 프로토타이핑 리소스 29개는 `ExternalAssets/UnrealLevelPrototyping`으로 공급자 내부 구조를 유지해 이동했다.
- 기존 ClientHome과 StylizedKitchen도 포함해 전체 맵을 검증했다. FBX/TGA 원본 149개를 추가로 `SourceAssets/ExternalAssets/StylizedKitchen`에 정리하고 해당 임포트 경로 149개를 갱신했다.
- 기본 맵·GameMode 설정과 도구의 문자열 경로를 갱신했다. GameMode 동작은 유지했다. 기본 게임에서 참조하는 `SM_TwoHeadScaleGuide`는 실험 에셋으로 남기지 않고 캐릭터 그래픽으로 분류했다.
- Unreal API로 에셋과 맵을 이동했으며 외부 액터/오브젝트 패키지 재배치는 엔진에 맡겼다. 남은 복사본 9개는 새 에셋으로 참조를 통합하고 Redirector를 엔진 명령으로 정리했다. 셸에서는 비어 있는 폴더만 제거했다.
- 작업 전 Content·설정·도구 등을 [백업 ZIP](../Outputs/Organization20261113/BeforeReorganization.zip)에 보존했다. [283개 이동 경로](../Outputs/Organization20261113/AssetMoves.json), [이동 결과](../Outputs/Organization20261113/Migration.json), [최종 구조 검사](../Outputs/Organization20261113/Verification.json)를 남겼다.

구조 검사: Blueprint 계열 18개 컴파일 및 저장, 7개 맵 2,350개 액터의 이름·클래스·배치·메시·머티리얼·애니메이션 연결이 이동 전과 일치했다. 의존성 1,336개에서 누락·이전 경로 참조·제품 맵의 Sandbox 참조가 모두 0개다. 기존 폴더 에셋과 Redirector도 0개다.

최종 빌드·실행 검사:

- Town 전체 레벨 및 월드 파티션 HLOD 빌드 완료. 맵 체크 오류·경고 0개. HLOD 명령 종료 코드 0.
- ClientHome 전체 레벨 빌드 완료. 맵 체크 오류 0개, 기존 빈 메시 섹션 경고 5개. 동적 조명 설정을 유지했다.
- Town에서 이동된 GameMode·Controller·Character가 실행되고 빙의·메시·이동 컴포넌트가 정상이며, 이동 입력으로 약 235cm 이동했다. 시작점의 +X 방향은 약 9.7cm에서 막혀 -X 방향으로 재검사했다. 전체 충돌 동선을 재검사한 것은 아니다.
- ClientHome 실제 PIE에서 pot_first 33개와 snack_first 35개, 총 68개 검사 통과. 단서 5개, 문 개방, 퇴장 위치에서 완료 플래그를 확인했다. 검사는 상호작용 위치로 이동시키는 기능 검사다.
- 빌드·플레이 후 구조 검사를 반복해 맵 구성 일치와 참조 누락 0개를 재확인했다. Python 36개 및 PowerShell 실행기 구문 검사, git diff --check 통과.
- 에디터의 콘텐츠 브라우저는 `/Game/Multimodal`, 실행 중인 새 PIE는 ClientHome 초기 상태다.

근거: [빌드 로그](../Outputs/Organization20261113/BuildVerification.log), [Town 플레이 검사](../Outputs/Organization20261113/TownPlay.json), [퇴장 검사](../Outputs/Organization20261113/ExitVerification.json), [단서 순서 1](../Outputs/ClientHome/cozy-pot_first-test.json), [단서 순서 2](../Outputs/ClientHome/cozy-snack_first-test.json).

Blueprint 프로젝트이므로 재빌드는 Blueprint 컴파일과 에디터 레벨 빌드다. 배포 실행 파일 패키징은 하지 않았다. Redirector 정리 commandlet은 기존 GameFeatureData Asset Manager 설정 누락으로 종료 코드 1을 반환했으나, 실제 정리 후 에디터에서 독립 검증하여 Redirector 0개와 참조 정상 상태를 확인했다. 기존 플러그인 설정은 동작 보존을 위해 임의 변경하지 않았다.

아래 내용은 11월 11일 첫 단계 작업 이력이다. 당시 예외와 수치는 전체 재구성 후의 현재 상태를 뜻하지 않는다.

## 2026-11-11 변경 경로

- `Content/ClientHome_Haeso`의 자체 제작 콘텐츠 → `Content/Multimodal`의 맵·Blueprint·그래픽·UI 분류. 블록아웃 맵은 `90_Sandbox/Maps/ClientHome`.
- `Content/StylizedKitchen` → `Content/ExternalAssets/StylizedKitchen`. 공급자 내부 구조와 이름을 유지하며 Git 제외 경로도 갱신.
- 맵 접두사 `Lvl_` → `LV_`, 폰트 `F_Jua` → `FNT_Jua`, 폰트 페이스 `Jua` → `FF_Jua`, 자체 가림 머티리얼에 `M_`/`MI_` 접두사 적용.
- `Development/ClientHome`의 Python·DSL·실행기 → `Build/Tools/ClientHome`.
- 구현 문서 → `Docs/ClientHome`, 제작 원본·라이선스 → `SourceAssets/ClientHome/UIArt`, 영상 → `Outputs/ClientHome/Media`.
- 화장실 도구의 필수 가구 입력 JSON을 `Saved`에서 `SourceAssets/Data/ClientHome`로 보존하고 도구 참조 갱신. 현재 도구의 검사 결과는 `Outputs/ClientHome`에 기록.
- 규칙 진입 문서 `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`는 단일 규칙 문서로 연결.

에셋별 이전·이후 경로는 [AssetMoves.json](../Outputs/Organization/AssetMoves.json)에 있다. 에셋 이동은 Unreal AssetTools API로 수행했다. `.uasset`·`.umap`을 셸로 이동하거나 Redirector 파일을 직접 삭제하지 않았다.

## 적용한 예외와 문서 충돌

- 규칙 3.2에 명시된 기존 `Characters`, `CocoDetective`, `Cursor`, `LevelPrototyping`, `TopDown`과 엔진 관리 폴더는 유지했다. 플러그인 설치 경로와 프로젝트 기본 시작 맵·게임 모드도 유지했다.
- 예전 구현 README의 `ClientHome_Haeso`, `Development/ClientHome` 전용 배치 제한은 새 규칙과 충돌하므로 규칙 링크와 새 경로로 대체했다.
- C++ 모듈이 없는 Blueprint 프로젝트다. 이번 재빌드는 Blueprint 컴파일 및 에디터 맵 빌드·플레이 검증을 의미하며 패키징된 배포 실행 파일을 만드는 작업과 구분한다.
- 이동 전 저장되지 않은 자체 에셋 5개도 먼저 저장해 보존했다. 그중 미사용 폰트는 `FNT_Jua_Imported`로 구분했다.
- 에디터가 대량 이동 후 이전 에셋 정리 단계에서 멈췄다. 새 에셋 669개와 작업 전 변경의 디스크 저장을 확인하고 에디터를 재시작했다. 이후 Unreal 명령/API로 정리를 이어갔다.
- 최초 Redirector 명령은 작업 결과 0을 반환했지만 기존 GameFeatures 플러그인의 `GameFeatureData` Asset Manager 설정 누락 오류가 로그에 있었다. 폴더 정리와 별개인 공용 기능 설정은 임의 변경하지 않았다.

## 검증

- 최종 에셋 검사 성공: 자체 제작 104개, 외부 팩 565개. 이전 위치의 패키지와 Redirector 0개.
- Blueprint 8개 재컴파일 및 저장, 블록아웃·플레이 맵 2개 로드 성공.
- 플레이 맵 의존성 770개: 누락 0개, 이전 경로 참조 0개, Sandbox 참조 0개.
- 에디터의 모든 레벨 빌드 완료. 맵 체크 오류 0개, 빈 삼각형 섹션 경고 5개. 동적 조명 설정에 따라 정적 라이팅 빌드는 생략됨.
- PIE 검사: pot_first 33개 + snack_first 35개 = 68개 통과. 단서 5개, 문 개방, 퇴장 영역에서 조사 완료 플래그 확인. 이 검사는 조사 좌표로 이동시키는 기능 검사이며 전체 충돌 동선 재검사는 아니다.
- Python 29개 구문 검사, 실행기 PowerShell 구문 검사, 문서 링크 검사 및 git diff --check 통과.
- 첨부 규칙과 루트 PROJECT_RULES.md의 SHA-256 동일.
- 검증 후 새 PIE 세션을 시작 화면으로 실행해 두었다.

외부 FBX/TGA 원본 28개는 `SourceAssets/ExternalAssets/StylizedKitchen`으로 보존하고 라이선스 에셋과 동일하게 Git에서 제외했다. 현재 같은 이름으로 대응되는 임포트 에셋 15개의 원본 경로 메타데이터와 자체 UI 텍스처·폰트 원본 경로를 갱신했다. 나머지 원본도 삭제하지 않고 보존했다.

빈 삼각형 섹션 경고 대상: `SM_CH_Bath_Access_House_Walls_SM`, `SM_CH_House_Floor`, `SM_CH_CH_Minimal_Cutaway_House_Walls_SM`, `SM_CH_CH_Minimal_Cutaway_Bathroom_Walls_Trim_SM`, `SM_CH_Right_House_Walls_SM`. 폴더 정리 과정에서 형상을 임의 변경하지 않았다. 배포 패키징 및 전체 프로젝트의 기존 GameFeatures 설정 오류 해결은 이번 검증에 포함하지 않는다.

상세 근거: [에셋 검증](../Outputs/Organization/Verification.json), [퇴장 상태 확인](../Outputs/Organization/ExitVerification.json), [빌드 로그 발췌](../Outputs/Organization/BuildVerification.log), [플레이 검사 1](../Outputs/ClientHome/cozy-pot_first-test.json), [플레이 검사 2](../Outputs/ClientHome/cozy-snack_first-test.json).
