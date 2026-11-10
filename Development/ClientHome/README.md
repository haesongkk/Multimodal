# 의뢰인 집 전용 작업

## 소유 범위

- 기존 파일은 모두 팀원 작업물이다. 수정·복제·참조하지 않는다.
- 에셋은 `/Game/ClientHome_Haeso/`, 소스·문서는 `Development/ClientHome/`에만 만든다.
- 공용 Character, Controller, GameInstance 및 골목 연결은 담당자 합의 후 진행한다.
- Save All 대신 전용 패키지만 저장한다. 프로젝트 시작 맵과 기본 게임 모드는 바꾸지 않는다.

## 현재 구현 (2026-11-04)

`/Game/ClientHome_Haeso/Maps/Lvl_ClientHome_Blockout`에서 독립 플레이가 가능하다.

1. 집 입장 안내 → Enter로 닫기.
2. WASD로 이동하고 단서 근처에서 E로 조사.
3. 화분·털·창문 조사 시 진행도 0/3 → 3/3. 재조사는 숫자를 늘리지 않는다.
4. 마지막 단서 설명을 확인하면 종합 추리 표시. Enter로 확인한다.
5. 현관 근처에서 E를 누르면 문이 바깥쪽으로 90도 열린다.
6. 현관 밖으로 걸어나가면 집 조사 완료 화면 표시. 테스트 종료는 Esc.

조사 전 현관은 물리적으로 닫혀 있다. 팝업 중 이동은 막는다.
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
build_gameplay.py는 전용 맵을 열고 PIE를 종료한 상태에서 실행한다.
전용 Blueprint와 맵을 재구성하므로 수동 편집을 추가한 뒤에는 내용을 검토하고 실행한다.
외부 폴더에 저장하지 않은 패키지가 있으면 중단한다.

에디터 Cmd 입력창:

```text
py "D:/Multimodal/Development/ClientHome/build_gameplay.py"
```

노드 이름 호환을 위해 생성 중 표시 언어를 일시적으로 영어로 전환하고 복원한다.
생성 로직은 BP_CH_HUD.dsl, BP_CH_Interact.dsl, BP_CH_Confirm.dsl에 남긴다.

PIE에서 통합 검사:

```text
py "D:/Multimodal/Development/ClientHome/test_gameplay.py"
```

검사는 테스트 캐릭터를 이동시킨다. 이후 PIE를 다시 시작해야 처음부터 플레이할 수 있다.
audit_gameplay.py는 전용 에셋 의존성과 카메라·본체 메시 중복 여부를 읽기 전용으로 검사한다.

## 남은 작업과 팀 연결

- 현재 기능 검증용 블록아웃이다. 캐릭터·가구·단서 외형과 조명은 최종 아트가 아니다.
- 긴 팝업의 반응형 줄바꿈, 다양한 화면 비율, 패키징 빌드는 아직 검증하지 않았다.
- 상태는 현재 HUD 세션에 저장된다. PIE 재시작 시 초기화된다.
- 공용 GameInstance 전달 계약: Home_Pot, Home_Fur, Home_Window, 집 조사 완료 여부.
- 코코는 창문으로 탈출하고 플레이어는 현관으로 나간다.
- 골목 맵과 공용 상태 계약 미확정으로 현재는 완료 화면에서 종료한다.
- 팀원 맵·기존 GameMode·공용 입력·프로젝트 플러그인 설정은 변경하지 않았다.
