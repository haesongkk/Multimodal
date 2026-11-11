# 의뢰인 집 전용 작업

## 소유 범위

- 팀원 작업물과 공용 설정은 수정하지 않는다. 사용자 요청에 따라 기본 Manny/TopDown 에셋과 Fab 에셋은 참조한다.
- 에셋은 `/Game/ClientHome_Haeso/`, 소스·문서는 `Development/ClientHome/`에만 만든다.
- 공용 Character, Controller, GameInstance 및 골목 연결은 담당자 합의 후 진행한다.
- Save All 대신 전용 패키지만 저장한다. 프로젝트 시작 맵과 기본 게임 모드는 바꾸지 않는다.

## 현재 실행 기준 (2026-11-11)

현재 맵은 `/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal`이다. 맵을 열고 Play로 실행한다.
기본 Manny 캐릭터, 각도 고정(-30도) 추적 카메라, 탐정 삽화가 있는 천 수첩 UI와 동등한 단서 5개를 사용한다.
화분·털·창문·간식·발자국 5개를 모두 모으면 추리와 현관 해금이 가능하다. 중앙 공간을 줄이고 주방–현관 벽과 화장실을 제거했다.

Fab의 [Stylized House Interior](https://www.fab.com/listings/ab92e5d3-6db6-4cf3-bff5-c2c98ae8db5b) 원본은 Git에 포함하지 않는다.
다른 PC에서는 각자의 Fab 라이브러리에서 해당 에셋을 설치해 `/Game/StylizedKitchen/` 참조를 충족해야 한다.
기본 Manny 및 TopDown 소스 에셋은 변경하지 않았다.

이전 구조 검증: 핵심 조사 흐름 16개 검사, 화장실 제거 경계·충돌, 실제 이동 동선, 8개 위치의 카메라 검사 통과.
결과 JSON은 로컬 `Saved/ClientHome/`에 있으며 Git에는 포함하지 않는다.

아래 문서와 생성 스크립트에는 이전 단계의 작업 기록이 포함된다. 이전 빌더를 현재 맵에 실행하면 배치를 덮어쓸 수 있다.
일부 중간 단계 스크립트는 Git에 없는 Saved 백업·매니페스트를 요구하므로 새 복제본에서 전체 재생성을 보장하지 않는다.
현재 저장된 맵의 플레이에는 Python 재생성이 필요 없다. 최종 구조 수정은 `remove_bathroom.py`, 캐릭터 설정은 `configure_manny.py`에 기록되어 있다.

## 이전 블록아웃 구현 (2026-11-10 탐색 개선)

`/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Blockout`에서 독립 플레이가 가능하다.

1. 집 입장 안내 → Enter로 닫기.
2. WASD로 이동하고 단서 근처에서 E로 조사.
3. 화분·털·창문 조사 시 진행도 0/3 → 3/3. 재조사는 숫자를 늘리지 않는다.
4. 마지막 단서 설명을 확인하면 종합 추리 표시. Enter로 확인한다.
5. 현관 근처에서 E를 누르면 문이 바깥쪽으로 90도 열린다.
6. 현관 밖으로 걸어나가면 집 조사 완료 화면 표시. 테스트 종료는 Esc.

조사 전 현관은 물리적으로 닫혀 있다. 팝업 중 이동은 막는다.
입장 안내는 단서 이름을 나열하지 않고 탈출 경로를 찾도록 안내한다.
입구 쪽 화분에서 흩어진 흙을 따라 창가의 털과 열린 창문으로 탐색한다.
조사 범위가 겹치면 수평 거리가 가장 가까운 대상을 선택하며, 조사한 단서는 '다시 확인'으로 표시한다.
단서 자유 순서 조사와 세 단서 완료 후 현관 해금은 현재 테스트 설계이며 팀 확정 조건은 아니다.
키 입력은 영문 WASD/E. 전용 게임 모드는 이 맵의 World Settings에만 지정한다.

## 구성

| 에셋 | 역할 |
|---|---|
| BP_CH_Player | 임시 원통형 캐릭터, 충돌·이동 컴포넌트, 고정 카메라 |
| BP_CH_HUD | 거리 검사, 단서 기록, E/Enter 입력, 한글 팝업·진행도·추리·완료 |
| BP_CH_GameMode | 전용 Player/HUD 지정 |
| BP_CH_Door | 힌지에서 오프셋된 문 메시와 충돌. HUD가 런타임 회전 제어 |

로직은 저장된 Blueprint에서 실행된다. 플레이에 Python 실행은 필요 없다.
Python은 에디터에서 에셋을 만들고 검사하는 용도다.

## 검증

2026-11-10: 단서 조사 순서 6가지를 각각 새 PIE 세션에서 실행하여 순서당 14개, 총 84개 검사 통과.
기존 13개 항목에 조사 범위가 겹칠 때 가장 가까운 단서 선택 검사를 추가했다.
Blueprint 재컴파일 및 저장, 전용 에셋 14개 의존성 검사도 통과했다.
전체 동선을 키보드로 연속 플레이하는 수동 검사와 다양한 화면 비율의 UI 검사는 아직 별도다.
최신 결과는 Saved/ClientHome/gameplay-test-report.json과 순서별 JSON에서 확인한다.
아래는 최초 프로토타입에서 확보한 검증 범위다.

- UE 5.8.4 및 Codex 기본 Unreal MCP로 빌드·PIE 확인. Blueprint 컴파일 검사 통과.
- PIE 13개 검사 통과: 세션 초기화, 팝업 닫기, 이동 입력, 벽 충돌, 닫힌 문 통과 방지,
  출구 잠금, 각 단서 기록, 중복 조사, 종합 추리, 정확한 90도 회전, 열린 문 퇴장 완료.
- E 키로 화분 팝업과 1/3 증가 확인. Enter로 팝업 닫기 확인.
- 자동 검사는 PIE 월드에서 위치를 옮기고 실제 Interact/Confirm Blueprint 함수를 호출한다.
  전체 경로를 사람이 WASD로 연속 플레이한 검사는 별도다.
- 전용 에셋 14개에 다른 /Game/ 폴더 의존성 없음. 카메라·본체 메시 각각 1개 확인.
- 기존 추적 파일 637개 SHA256 대조: 변경 0개.
- 결과: Saved/ClientHome/gameplay-test-report.json, gameplay-asset-audit.json.

## 실행과 재생성

에디터가 닫혀 있을 때 Launch-ClientHomeEditor.ps1로 UE 5.8 및 MCP를 실행한다.
열려 있다면 전용 맵을 열고 Play를 누른다. 기존 팀원 맵과 혼동하지 않도록 맵 이름을 확인한다.

build_blockout.py는 최초 공간 생성 전용이며 이미 존재하는 맵을 덮어쓰지 않는다.
refine_layout.py는 전용 맵에서 화분·흙·털 위치를 조정하고 흙 흔적과 열린 창틀을 추가한다.
같은 라벨을 재사용하므로 반복 실행해도 소품을 중복 생성하지 않는다. 수동 배치 이후 실행 시 해당 소품 위치는 다시 설정된다.
최초 블록아웃 재생성 시 build_blockout.py → refine_layout.py → build_popup.py → build_gameplay.py 순서로 실행한다.
build_gameplay.py는 전용 맵을 열고 PIE를 종료한 상태에서 실행한다.
전용 Blueprint와 맵을 재구성하므로 수동 편집을 추가한 뒤에는 내용을 검토하고 실행한다.
외부 폴더에 저장하지 않은 패키지가 있으면 중단한다.

에디터 Cmd 입력창:

```text
py "D:/Multimodal/Development/ClientHome/build_popup.py"
py "D:/Multimodal/Development/ClientHome/build_gameplay.py"
```

노드 이름 호환을 위해 생성 중 표시 언어를 일시적으로 영어로 전환하고 복원한다.
생성 로직은 BP_CH_HUD.dsl, BP_CH_Interact.dsl, BP_CH_Confirm.dsl에 남긴다.

PIE에서 통합 검사:

```text
py "D:/Multimodal/Development/ClientHome/test_gameplay.py"
```

검사는 테스트 캐릭터를 이동시킨다. 이후 PIE를 다시 시작해야 처음부터 플레이할 수 있다.
순서별 검사는 매번 새 PIE 세션에서 실행한다. 에디터 Cmd에서 실행하는 창문 우선 조사 예:

```text
py CLUE_ORDER=('window','pot','fur'); exec(compile(open('D:/Multimodal/Development/ClientHome/test_gameplay.py',encoding='utf-8').read(),'test_gameplay.py','exec'))
```

순서별 결과는 Saved/ClientHome/gameplay-test-<순서>.json에도 보관된다.
audit_gameplay.py는 전용 에셋 의존성과 카메라·본체 메시 중복 여부를 읽기 전용으로 검사한다.

## 팝업 UI 개선

- 고정 좌표 Canvas 팝업을 전용 WBP_CH_Popup UMG 위젯으로 교체했다.
- 화면 하단 비율 앵커, 자동 높이, 한글 문자 단위 줄바꿈을 적용했다.
- 어두운 둥근 배경 위에 제목·본문·키 안내를 분리했다. 완료 시 Esc 안내를 표시한다.
- 기존 Enter 확인과 이동 잠금 흐름을 유지하며, 내용 또는 표시 상태가 바뀔 때만 갱신한다.
- 1280×720(16:9), 800×600(4:3) PIE 창에서 165자 한글 본문과 안내가 잘리지 않는 것을 화면으로 확인했다.
- UI 동기화·숨김·완료 안내를 포함한 PIE 통합 검사 22개 통과(화분→털→창문 순서).
- test_popup.py는 긴 문장의 시각 검사용이다. PIE에서 실행 후 직접 화면을 확인하고 세션을 재시작한다.
- 재생성: build_popup.py → build_gameplay.py. 위젯 그래프는 WBP_CH_Popup.dsl에 저장된다.
- 상단 상태 HUD는 기존 Canvas 방식을 유지한다. 임의 길이 본문용 스크롤/페이지 전환은 아직 없다.

## 거실·창가 아트 1차 배치

- style_home.py는 전용 맵에 원목 바닥, 벽 하단 패널, 커튼과 화분 잎을 추가한다.
- CocoDetective의 기존 소파·러그·테이블·책장·식물·고양이 용품을 읽기 전용으로 참조한다. 원본 에셋은 수정하지 않는다.
- 청록 소파, 세이지 러그, 원목 가구, 따뜻한 조명으로 거실 색감을 맞췄다.
- 기존 단서 위치와 가구 충돌은 유지했다. 교체된 가구의 기존 메시를 숨겨 충돌 프록시로 사용하며, 장식 에셋은 충돌을 끈다. 최종 가구 충돌은 추후 정밀 조정할 수 있다.
- 실행 순서: refine_layout.py → style_home.py. 반복 실행 시 같은 라벨을 재사용한다.
- audit_gameplay.py는 명시한 공용 장식 메시 11개만 허용하고 다른 팀 콘텐츠 의존성은 계속 검사한다.
- 현재 부엌과 플레이어 외형은 블록아웃이다. 거실·창가를 기준으로 다음 아트 패스를 확장한다.

## 남은 작업과 팀 연결

### 현재 작업 기준: 예제 배치 최소 수정

- 최신 플레이 맵: /Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Minimal. Launcher 스크립트도 이 맵을 우선 연다.
- 예제의 원래 가구·장식·벽지·조명을 유지한다. 이전 Interior 아트 패스는 비교용으로만 남긴다.
- 원래 창가 화분과 식물만 바닥에 넘어뜨리고, 원래 창문을 바깥으로 열었다. 흙 4개·털 조각 5개를 추가했다.
- 기존 문 메시를 그대로 회전시킨다. 예제 문 뒤의 벽 구조는 유지하며, 문이 90도 열린 후 문 앞 마커에서 출구 전환을 완료한다.
- 이동 시작 위치와 눈에 보이지 않는 문 통과 마커를 조정했다. 원본 Fab 에셋과 블록아웃 Blueprint는 수정하지 않는다.
- 조작: 기존 고정 사선 탑다운 시점, WASD 이동, E 조사, Enter 팝업 확인, Esc PIE 종료.
- 전용 *_Minimal Blueprint 사본에 기존 팝업·단서·추리·문 열기를 연결했다. 골목 연결 전까지 출구 전환 지점에서 완료 팝업을 표시한다.
- 재생성 순서: build_minimal_home.py → build_minimal_gameplay.py. 실행 중 PIE는 종료해야 한다.
- 검사: 새 PIE에서 test_minimal_home.py; PIE 종료 후 audit_minimal_layout.py. 각각 Saved/ClientHome/minimal-play-test.json, minimal-layout-audit.json에 결과를 쓴다.
- 자동 검사는 위치를 옮겨 Blueprint 조사 함수와 문 충돌을 확인한다. 사람이 전체 경로를 걸어 보는 검사를 대체하지 않는다.
- 원본 배치 비교 결과: 기존 액터 733개 중 729개의 배치·메시·머티리얼을 유지했다. 천장은 고정 탑다운 시야 확보를 위해 플레이 중에만 숨긴다. 변경한 배치는 화분, 식물, 창문, 시작 위치 4개뿐이다. 기존 액터 삭제는 없다. 조명 값도 원본과 같다.
- 최소 수정 맵 PIE 통합 검사 16개 통과: 초기화, 팝업, 단서 접근/기록, 중복 조사, 추리, 문 잠금/회전, 회전 완료 후 출구 전환, 완료 안내.

### 탑다운 시야·동선·단서 가독성 보완

현재 카메라는 아래의 고정 탑다운에서 **고정 각도 추적 카메라**로 변경했다. 창가 벽(+X)을 바라보는 pitch -35°, yaw 0°, FOV 60°이며, 플레이어 뒤 850cm 위치를 부드럽게 추적한다(보간 속도 3.5). 현재 추적 범위는 아래의 집 전체 탐색 지원 항목을 따른다. 거실 전용 제한은 제거했다. 화면 비율은 16:9로 유지하며 다른 비율에서는 여백이 생긴다. WASD도 화면 방향에 맞춰 W=+X, S=-X, A=-Y, D=+Y로 변경했다. 구현은 minimal_follow_camera.py와 BP_CH_Minimal_Player.dsl, 검사는 test_minimal_camera.py에 있다.

- 고정 사선 시점을 유지하고 카메라를 (150, -830, 1700), pitch -68°, yaw 90°, FOV 65°로 조정했다. 창가와 현관을 함께 보여 주고 앞쪽 벽의 가림을 줄인다.
- 큰 좌측 상태창을 상단의 작은 두 패널로 나누고 조사 안내를 화면 하단으로 옮겼다.
- 단서에 350cm 이내로 접근하면 작은 표식, 실제 조사 대상에는 [E] 라벨을 표시한다. 확인한 단서는 민트색으로 구분한다. 팝업을 읽는 동안 표식은 숨긴다.
- 의자 밑에 가리던 추가 털 5조각만 의자 옆 바닥 (710, 80) 주변으로 옮기고 조금 키웠다. 예제 가구·벽·조명·충돌 크기는 변경하지 않았다.
- test_minimal_walk.py는 새 PIE에서 CharacterMovement 입력으로 화분 → TV 우회 → 털 → 창문 → 중앙 통로 → 현관을 이동한다. 순간이동 없이 충돌과 조사 접근을 확인하고 Saved/ClientHome/minimal-walk-test.json에 기록한다. 실제 키보드 입력 검사는 별도다.

### Fab 기반 의뢰인 집 아트 맵

- 작업 맵: /Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Interior.
- 재생성/업데이트: 에디터에서 build_interior_art.py 실행. 최초 실행은 Fab 예제 맵을 별도로 저장한 후 편집한다.
- 창가 TV 위치와 티테이블 구역을 정리하고, 커튼 폭을 줄여 열린 창문을 드러냈다.
- 과밀한 화분 군집을 줄이고 고양이 방석·스크래처·장난감, 넘어진 화분·흙 발자국·창가 털을 배치했다.
- 벽지와 바닥 머티리얼은 전용 사본을 사용한다. 색수차를 끄고 블룸을 낮췄다.
- Home_Pot / Home_Fur / Home_Window 태그 각 1개, 추가 아트 액터 71개. 반복 실행 후 중복 없는 것을 확인했다.
- 이 맵은 아트 검토용이다. 기존 블록아웃의 고정 카메라·조사 UI·문·퇴장 조건은 아직 이식하지 않았다.
- 원본 예제의 베이크 조명을 유지하고 있어 이동한 가구 주변의 잔존 그림자는 최종 라이트 빌드에서 정리해야 한다.
- Fab 원본은 Launcher 캐시와 동일하게 복원·확인했다. 기존 Lvl_ClientHome_Blockout은 이 작업에서 변경하지 않았다.
- audit_gameplay.py는 이 맵/머티리얼의 /Game/StylizedKitchen 의존성도 허용한다.

### 기획안 Fab 에셋 확보 (2026-11-10)

- 제품: Stylized House Interior / StylArts, Fab Standard License, 무료로 계정 라이브러리에 추가.
- 출처: https://www.fab.com/listings/ab92e5d3-6db6-4cf3-bff5-c2c98ae8db5b
- Epic Games Launcher에서 UE 5.8용 패키지를 Multimodal에 추가했다.
- 로컬 콘텐츠: /Game/StylizedKitchen. 예제 맵: /Game/StylizedKitchen/Levels/Stylized_Interior, 전시 맵: /Game/StylizedKitchen/Levels/AssetsOverview.
- 예제 맵의 실내 가구·벽지·바닥·조명 렌더링을 UE 5.8에서 확인했다. 원본 예제는 수정하지 않았다.
- 현재 조사 기능은 Lvl_ClientHome_Blockout에 있으며 예제 맵에는 아직 연결하지 않았다.
- Fab 원본 패키지는 공개 저장소에 원본 배포되지 않도록 .gitignore로 제외했다. 협업자는 Fab에서 제품을 확보하고 Launcher의 프로젝트에 추가 기능으로 같은 경로에 설치한다.

- 현재 기능 검증용 블록아웃이다. 캐릭터·가구·단서 외형과 조명은 최종 아트가 아니다.
- 위 두 해상도 외 화면 비율, 초장문, 패키징 빌드는 아직 검증하지 않았다.
- 상태는 현재 HUD 세션에 저장된다. PIE 재시작 시 초기화된다.
- 공용 GameInstance 전달 계약: Home_Pot, Home_Fur, Home_Window, 집 조사 완료 여부.
- 코코는 창문으로 탈출하고 플레이어는 현관으로 나간다.
- 골목 맵과 공용 상태 계약 미확정으로 현재는 완료 화면에서 종료한다.
- 팀원 맵·기존 GameMode·공용 입력·프로젝트 플러그인 설정은 변경하지 않았다.

### 집 전체 탐색 지원

- 거실만 추적하던 카메라 범위를 주방·현관 복도·욕실까지 확장했다. 이동을 제한하는 보이지 않는 벽은 추가하지 않았다.
- 기본 카메라는 X [-1450, 30], Y [-650, 350] 범위에서 추적한다. 주방에서는 측면 경계를 고려하고, 욕실에서는 같은 35도 각도로 거리를 줄여 작은 방을 화면 안에 담는다.
- build_house_cutaway.py는 원본 벽의 충돌과 그림자를 유지하고, 앞쪽 면을 제거한 전용 메시 5개를 별도 시각 액터로 표시한다. 예제 원본 파일과 가구 배치는 유지한다. 조명용 외곽 큐브와 앞쪽 주방 창 장식은 플레이 중 숨기되 그림자는 유지한다.
- 새 맵 생성 순서: build_minimal_home.py → build_minimal_gameplay.py → build_house_cutaway.py.
- test_whole_house_walk.py: 거실 → 주방 → 현관 복도 → 욕실 안쪽까지 순간이동 없이 CharacterMovement로 이동하는 검사. test_minimal_camera.py는 전체 방의 추적 범위·각도·플레이어 화면 포함 여부를 확인한다.

### 선택 보조 단서 2개

- 식탁 옆 (-520, 190)에 먹다 남은 간식 그릇과 부스러기를 추가했다. 예제의 나무 그릇 메시를 재사용한다.
- 복도 (180, -520)에서 거실 쪽으로 이어지는 작은 발자국 3개를 추가했다. 발자국 전체가 하나의 보조 단서다.
- Home_Snack / Home_Pawprints 태그로 조사한다. SnackSeen / PawprintsSeen / ExtraCount는 핵심 Count와 별개이며, 중복 조사로 증가하지 않는다.
- 핵심 단서 3개만으로 추리·현관 진행이 가능하다. 보조 단서는 먼저 조사하면 추리 완료 설명에 반영되고, 추리 후에 발견해도 경로를 보강하는 설명을 보여 준다.
- HUD에 핵심 0/3, 보조 0/2(선택)를 별도로 표시하고 기존 조사 표식을 재사용한다.
- 현재 맵에 추가할 때: refine_clue_layout.py → build_optional_gameplay.py. 전체 재생성 시에는 build_minimal_home.py 이후 refine_clue_layout.py로 보조 단서와 흙·털 배치를 적용한 뒤 build_minimal_gameplay.py를 실행한다.
- 검사: test_optional_walk.py(실제 이동), test_optional_clues.py의 run('before') / run('after')(수집 순서·중복·선택 진행), test_minimal_home.py(보조 단서를 건너뛴 기존 진행).

### 단서 배치 다듬기

- 식탁 가장자리로 간식을 당기고 부스러기는 통로 쪽으로 흩어 배치했다.
- 발자국은 좌우 간격과 방향을 달리해 복도에서 거실로 이어지도록 조정했다.
- 화분 흙은 창문 방향으로 점차 작아지는 모양, 털은 의자 옆의 밝은 작은 덩어리로 정리했다.
- refine_clue_layout.py는 기존 단서만 조정한다. 원본 가구·카메라·조사 반경은 유지한다.
### 현재 맵: 중간 공간 축소

- 현재 Minimal 맵은 책상 구역과 여분의 1인 소파 두 개가 있는 휴식 구역을 정리한 버전이다. 창가 거실의 소파 두 개와 핵심 단서는 유지했다.
- 주방/욕실 구역은 X축으로 +220cm 이동하고, 중앙 X=[0,400] 구간을 [220,400]으로 줄였다. 주방과 욕실의 가구 자체 크기는 유지한다.
- 원본 Fab 메시를 수정하지 않고, 벽·바닥·몰딩·차폐 메시 29개의 전용 복사본(CompactV2)을 만들었다. 충돌도 변경된 구조의 삼각형을 사용한다.
- 제거 대상 가구·소품은 되돌릴 수 있도록 숨김과 충돌 비활성화로 보존했다. 소파 러그, 외곽 보조 Plane, 시야를 가리는 주방 상부 선반도 플레이 중 숨긴다. 좁아진 욕실 입구의 수납장과 위 소품 6개는 통행 확보를 위해 함께 숨겼다.
- 작업 전 맵 파일 백업: Saved/ClientHome/Lvl_ClientHome_Minimal.precompact.umap. 원본 비교 데이터: precompact-actors.json.
- 현재 구조에 대한 검사: audit_compact_home.py, test_compact_walk.py, test_compact_camera.py, test_optional_clues.py, test_minimal_home.py.
- 이전 audit_minimal_layout.py와 초기 배치 빌더들은 축소 이전 배치를 기준으로 한다. 현재 맵에 재실행하지 않는다.
- 축소 작업 순서: 작업 전 맵 백업 → compact_home.py(1회) → refine_compact_visibility.py → update_compact_camera.py. compact_home.py는 이미 완료된 맵에 중복 적용하지 않는다.
### 주방–현관 칸막이 개방

- open_kitchen_partition.py는 X=-230~-190, Y=-526~-125 구간의 칸막이 면과 몰딩만 제거한 OpenKitchen 메시 복사본을 사용한다. 전체 벽 액터를 숨기거나 전체 벽 충돌을 해제하지 않는다.
- 욕실과 만나는 끝면, 욕실 경계 벽, 외벽, 현관문과 바닥은 유지한다. 기존에 숨긴 칸막이 장식은 그대로 숨겨 둔다.
- 작업 전 백업: Saved/ClientHome/Lvl_ClientHome_Minimal.before-partition.umap.
- 검증: test_open_partition_walk.py는 열린 구간 두 곳을 양방향으로 통과하고 욕실·현관으로 이동한다. test_open_partition_collision.py는 열린 곳의 충돌 제거와 욕실/외벽 충돌 보존을 검사한다.
### 개방 후 잔여물 정리

- polish_open_home.py는 원래 cutaway 메시의 모든 유효 정점을 순회해 축소 좌표를 다시 적용한다. 삭제된 폴리곤 ID가 연속적이라고 가정하던 문제 때문에 남은 주방의 비스듬한 면과 욕실 벽 틈을 수정했다. 시각 메시 5개는 Polished 경로를 사용한다.
- 없앤 가구가 남기던 숨김 그림자를 비활성화하고, 숨긴 주방 벽에 붙어 있던 액자 2개도 함께 숨겼다. 통로의 빗자루는 조리대 옆 (-360,-405)으로 옮겼다.
- 현재 최종 적용 순서는 open_kitchen_partition.py 다음 polish_open_home.py다. 이전 메시를 다시 적용한 경우 마지막 정리 스크립트를 재실행한다.
- 작업 전 백업: Saved/ClientHome/Lvl_ClientHome_Minimal.before-polish.umap.
### 플레이어 Manny 적용

- configure_manny.py는 기존 BP_CH_Player_Minimal의 원통을 숨기고 프로젝트 기본 SKM_Manny_Simple / ABP_Unarmed를 연결한다. 원본 TopDown 캐릭터와 공용 에셋은 수정하지 않는다.
- 기존 캡슐 반지름 34 / 반높이 88, 이동 속도 270, 카메라와 HUD 입력을 유지한다. 메시 위치는 캡슐 높이에 맞춰 Z=-87, 회전은 기본 Manny의 Yaw=-90이며 이동 방향을 바라본다.
- build_minimal_gameplay.py도 같은 설정 함수를 사용한다. 캐릭터만 갱신할 때는 configure_manny.py만 실행한다.
- test_manny_animation.py는 이동 검사와 함께 실행하여 실제 발 포즈 변화·방향 회전·카메라 고정 각도를 검사한다.
- 적용 전 백업: Saved/ClientHome/BP_CH_Player_Minimal.before-manny.uasset.
### 현재 구조: 욕실 제거 / 30도 카메라

- remove_bathroom.py는 욕실 확장부의 설비·장식·문틀을 숨기고 충돌을 끈다. 벽·바닥·몰딩·외곽 차폐 메시를 Y=-550 경계에서 잘라 NoBathroom 복사본으로 교체하고 현관 끝을 새 벽과 걸레받이로 닫는다.
- 욕실만 삭제한 빈 방을 남기지 않는다. 옛 욕실 내부에는 바닥과 벽 충돌이 없으며 새 경계 벽이 진입을 막는다. 현관문과 핵심/보조 단서는 유지한다.
- minimal_follow_camera.py: 고정 Pitch=-30, 높이 480, X=[-1230,30], Y=[-350,350](주방에서는 최소 -180), 거리 오프셋 850, 보간 3.5. 욕실 전용 줌/추적 분기는 제거했다.
- 현재 검사: test_no_bathroom_walk.py, test_no_bathroom_boundary.py, test_side_camera.py, test_minimal_home.py. 이전 욕실 방문 검사는 현재 구조에 적용하지 않는다.
- 현재 최종 메시 적용은 remove_bathroom.py이며, 이전 구조/시각 메시 빌더를 재적용하면 욕실이 다시 나타날 수 있다.
- 백업: Saved/ClientHome/Lvl_ClientHome_Minimal.before-no-bathroom.umap 및 BP_CH_Player_Minimal.before-side-camera.uasset.

### 조사 UI 리디자인 (2026-11-11)

- 크림색 종이와 청록색 글자를 사용한 조사 노트 스타일. 상단 사건 카드와 핵심 3칸 진행 표시, 보조 단서 수, 하단의 작은 조사 안내 카드를 사용한다.
- 팝업은 둥근 크림색 카드, 사건 라벨, 제목/본문/확인 안내의 세 단계 글자 크기로 구성한다. 한글 본문은 자동 줄바꿈한다.
- `build_popup.py`는 공유 조사 팝업의 스타일을 갱신한다. 이후 `refresh_ui.py`는 Minimal HUD의 DrawHUD 이벤트만 갱신한다. 두 스크립트는 PIE를 중지한 상태에서 별도로 실행한다.
- `refresh_ui.py`는 기존 BeginPlay/Tick과 Interact/Confirm을 보존하며 맵이나 플레이어를 저장하지 않는다.
- UI 수정 전 백업: `Saved/ClientHome/BP_CH_HUD_Minimal.before-ui.uasset`, `Saved/ClientHome/WBP_CH_Popup.before-ui.uasset`.
- 검증: 1280×720 플레이 화면에서 팝업과 HUD 표시 확인. 핵심 조사/중복 수집/추리/현관 진행 검사 16개 통과 (`Saved/ClientHome/minimal-play-test.json`).

### 현재 UI / 동등한 단서 5개 (2026-11-11)

- 사용자 제공 사람 탐정 디자인(체크모자, 청회색 코트, 금색 단추, 돋보기)을 참고한 임시 삽화. 바느질 천 패널, Jua 한글 서체, 발바닥 도장 5칸을 사용한다.
- `Count` 하나로 모든 단서를 집계한다. 각 Seen 플래그가 중복 집계를 막는다. 5개 모두 확인 후 추리와 현관 해금이 진행된다. ExtraCount는 이전 에셋 호환을 위해 남아 있으나 새 로직에서 읽거나 쓰지 않는다.
- UMG `UpdateJournal`이 진행도/안내/발바닥 도장을 갱신한다. `Present`는 개별 팝업 카드만 숨기며 상단 수첩은 항상 표시한다.
- 적용: PIE 중지 → `build_cozy_ui.py` → `build_cozy_gameplay.py`. 맵·플레이어·공용 에셋은 이 과정에서 저장하지 않는다.
- 런타임 검사: `test_cozy_gameplay.py`. 이전 `test_minimal_home.py`/`test_optional_clues.py`는 3+2 규칙용이므로 현재 규칙의 판정에 사용하지 않는다.
- 소스 아트·라이선스·생성 프롬프트: `UIArt/ASSETS.md`. 최종 캐릭터 수령 시 UI 삽화만 교체할 수 있다.
- 현재 규칙 검증 완료: 화분→털→창문→간식→발자국 33개 검사, 간식→발자국→창문→털→화분 35개 검사 통과. 실제 근접 대상 선택, 5개 동등 집계, 재조사 중복 방지, 3/4개에서 현관 잠금, 5개에서 추리·현관 회전·완료를 확인했다. 1280×720에서 초기/조사/긴 추리 카드와 5개 도장 표시를 확인했다.
