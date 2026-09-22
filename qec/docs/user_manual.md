# QEC Quantum Simulator 사용 설명서

편집 가능 원본: 이 Markdown 파일  
Word 버전: `user_manual.docx` (동일 폴더)

---

## 1. 프로그램 소개

**QEC Quantum Simulator**는 surface-code 양자 오류 정정(QEC) 실험을
그래픽 화면에서 설정하고, 회로를 확인한 뒤, syndrome 데이터셋을 생성하는 프로그램입니다.

- 지원 OS: **Windows**, **Linux**
- 사용 방식: **GUI** (명령줄 불필요)
- 실행 파일: Windows `QEC_Quantum_Simulator.exe` / Linux `QEC_Quantum_Simulator`

---

## 2. 설치 및 실행

### 2.1 실행 파일로 실행 (일반 사용자 권장)

**Windows**

1. `QEC_Quantum_Simulator.exe`를 원하는 폴더에 둡니다.
2. 더블클릭하여 실행합니다.
3. 백신 프로그램이 차단하면 “허용”합니다.

**Linux**

```bash
chmod +x QEC_Quantum_Simulator
./QEC_Quantum_Simulator
```

### 2.2 소스에서 실행 (개발자)

```bash
cd qec
pip install -r requirements.txt
export PYTHONPATH="$PWD/src"   # Windows: set PYTHONPATH=%CD%\src
python -m qec_sim.gui
```

### 2.3 실행 파일 직접 빌드

- Linux: `scripts/build_gui_linux.sh`
- Windows: `scripts/build_gui_windows.bat`

---

## 3. 화면 구성

화면은 좌우로 나뉩니다.

| 영역 | 이름 | 역할 |
|------|------|------|
| 왼쪽 | **입력 (INPUT)** | 실험 조건 입력 |
| 오른쪽 | **출력 (OUTPUT)** | 회로 그림 + 결과 요약 |

하단 버튼:

- **입력 초기화**: 기본값으로 복원
- **회로 미리보기**: 회로만 생성하여 그림 표시 (데이터 저장 없음)
- **실험 실행**: 전체 시뮬레이션 + 파일 저장

---

## 4. 입력 항목 설명

각 항목에 **마우스를 올리면** 말풍선(툴팁)으로 짧은 설명이 나타납니다.
커서를 옮기면 말풍선은 사라집니다.

| 항목 | 권장 시작값 | 설명 |
|------|-------------|------|
| task | `surface_code:rotated_memory_x` | 생성할 회로 종류 |
| distance | `3` | 코드 거리 (2 이상) |
| rounds | (비움) | 측정 라운드. 비우면 distance와 동일 |
| depolarizing_p | `0.001` | 탈분극 잡음 확률 (0~1) |
| measurement_p | `0.001` | 측정 잡음 확률 (0~1) |
| shots | `1000` (처음) / `10000` (본실험) | 샘플 수. 클수록 시간↑ |
| seed | `20260819` | 재현용 난수 시드 |
| output_dir | 홈/`qec_sim_output` | 결과 저장 폴더 |

### 4.1 저장 폴더 지정

1. `output_dir` 옆 **찾아보기…** 클릭
2. 파일 탐색기에서 폴더 선택
3. 선택한 경로가 입력란에 표시됨

---

## 5. 기본 사용 절차

1. 프로그램을 실행합니다.
2. 왼쪽에서 실험 조건을 입력합니다.
3. **찾아보기**로 결과 저장 폴더를 지정합니다.
4. **회로 미리보기**를 눌러 오른쪽에서 양자 회로 그림을 확인합니다.
5. 문제가 없으면 **실험 실행**을 누릅니다.
6. 확인 대화상자에서 **Yes**를 선택합니다.
7. 완료 메시지와 함께 OUTPUT에 요약이 표시됩니다.
8. 안내된 폴더에서 생성된 파일을 확인합니다.

---

## 6. 출력 결과 읽는 법

### 6.1 양자 회로 다이어그램

OUTPUT 상단에 Stim `timeline-svg` 기반 회로 그림이 표시됩니다.
distance가 크면 그림이 매우 커질 수 있으니 스크롤로 확인하세요.

### 6.2 데이터 생성 결과 요약

다음 정보가 표시됩니다.

- 저장 위치
- 실험 조건 재확인
- 회로 규모 (qubits / detectors / observables)
- 디코더 평가 (logical_errors, logical_error_rate, detection_event_density)
- 생성 파일 목록

### 6.3 저장 파일

`output_dir / <run_name> /` 아래에 생성됩니다.

| 파일 | 내용 |
|------|------|
| `detection_events.npy` | detection event 배열 |
| `observables.npy` | logical observable |
| `mwpm_predictions.npy` | 디코더 예측 |
| `circuit.stim` | 회로 텍스트 |
| `detector_error_model.dem` | DEM |
| `detector_coordinates.json` | detector 좌표 |
| `metadata.json` | 재현성 메타데이터 |

---

## 7. 오류가 났을 때

프로그램은 오류 메시지와 함께 **해결 방법**을 함께 보여줍니다.

| 증상 | 조치 |
|------|------|
| distance 오류 | 2 이상 정수로 변경 (예: 3) |
| 잡음률 오류 | 0.0~1.0 사이 소수로 변경 (예: 0.001) |
| shots 오류 | 1 이상 정수, 처음엔 1000 권장 |
| 저장 경로/권한 오류 | 홈 아래 다른 폴더 선택 |
| 작업 중 재클릭 | 진행이 끝날 때까지 대기 |

---

## 8. 성능 팁

- 첫 실행은 `distance=3`, `shots=1000`으로 테스트하세요.
- `distance≥7` 또는 `shots≥100000`은 시간이 크게 늘어납니다.
- 회로 미리보기만으로도 설정이 맞는지 확인할 수 있습니다.

---

## 9. 문의 / 추가 문서

- 개발 구조: `docs/development_guide.md`
- 소스 루트: `qec/src/qec_sim`
