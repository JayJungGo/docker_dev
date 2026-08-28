# QEC 시뮬레이션 실험에서 사용할 데이터구조 정의 객체
# 연구 파이프라인에서 데이터가 이동할 때 사용하는 표준 용기(container)
## QEC 시뮬레이션 실험의 입력, 중간 결과, 평가 결과, 최종 결과를 표현하는 데이터 객체를 정의한다.

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import numpy as np

# 실험 도중 값이 임의로 변경되는 것을 방지하기 위해 immutable 객체로 정의
@dataclass(frozen=True)

# QEC 실험 조건 정의 클래스
class ExperimentConfig:
    # Stim에서 생성할 QEC 회로 종류
    # 기본값: rotated surface code의 logical X memory 실험
    task: str = "surface_code:rotated_memory_x"

    # Surface code의 code distance
    # code distance 증가에 따른 decoder 성능 및 확장성 분석에 사용
    distance: int = 3

    # Stabilizer measurement 반복 횟수
    # None이면 effective_rounds에서 distance와 동일한 값 사용
    rounds: int | None = None

    # Clifford gate 수행 후 적용할 depolarizing noise 확률
    # physical noise rate 변화에 따른 decoder 성능 분석에 사용
    depolarizing_p: float = 0.001

    # Stabilizer 측정 과정에서 발생하는 measurement flip 확률
    # measurement noise 설정
    measurement_p: float = 0.001

    # 동일한 QEC circuit을 반복 simulation할 횟수
    # 생성되는 syndrome sample의 개수와 동일
    shots: int = 10_000

    # Monte Carlo syndrome sampling의 재현성을 위한 random seed
    seed: int = 20260819

    # QEC simulation 결과의 원본 데이터와 metadata를 저장할 기본 경로
    output_dir: Path = Path("/workspace/data/qec/raw")

    @property
    def effective_rounds(self) -> int:
    """
    실제 simulation에서 사용할 stabilizer measurement round를 반환한다.
    rounds가 명시되어 있으면 해당 값을 사용하고,
    지정되지 않은 경우 code distance를 기본 round 수로 사용한다.
    """
        return self.rounds if self.rounds is not None else self.distance

    def validate(self) -> None:
    """
    QEC simulation 실행 전에 experiment parameter의 유효성을 검사한다.
    - code distance가 유효한지 검사
    - stabilizer measurement round가 1 이상인지 검사
    - noise probability가 0~1 범위인지 검사
    - simulation shots가 양수인지 검사
    잘못된 설정이 존재하면 ValueError를 발생시켜
    simulation 실행 전에 문제를 차단한다.
    """
        if self.distance < 2:
            raise ValueError("distance must be >= 2")

        if self.effective_rounds < 1:
            raise ValueError("rounds must be >= 1")

        if not 0.0 <= self.depolarizing_p <= 1.0:
            raise ValueError(
                "depolarizing_p must be between 0 and 1"
            )

        if not 0.0 <= self.measurement_p <= 1.0:
            raise ValueError(
                "measurement_p must be between 0 and 1"
            )

        if self.shots <= 0:
            raise ValueError("shots must be > 0")


@dataclass(frozen=True)
"""
Stim simulation에서 생성된 syndrome batch를 표현한다.
detections:
  각 shot에서 발생한 detection event 배열.
  향후 classical/neural decoder의 입력 데이터로 사용된다.
observables:
  각 shot의 실제 logical observable flip 정보.
  decoder prediction의 정답(label)으로 사용된다.
"""
class SampleBatch:
    detections: np.ndarray
    observables: np.ndarray


@dataclass(frozen=True)
"""
생성된 QEC circuit의 구조적 규모를 나타내는 통계정보.
code distance 증가에 따른 circuit 규모와
decoder scalability를 분석하기 위한 metadata로 사용한다.
"""
class CircuitStats:
    num_qubits: int
    num_detectors: int
    num_observables: int


@dataclass(frozen=True)
 """
 QEC decoder의 성능 평가 결과.
 logical_errors:
    decoder가 logical observable을 잘못 예측한 shot의 수.
 logical_error_rate:
    전체 shots 대비 logical decoding failure의 비율. Decoder의 핵심 성능지표.
 detection_event_density:
    전체 detector 데이터에서 detection event가 발생한 비율.
    향후 neural predecoder의 syndrome density 감소 효과 분석에 사용.
 """
class EvaluationResult:
    logical_errors: int
    logical_error_rate: float
    detection_event_density: float


@dataclass(frozen=True)
 """
 하나의 QEC simulation/decoding experiment에서 생성된
 전체 결과를 하나의 객체로 묶어 표현한다.
 ResultWriter가 이 객체를 받아 raw dataset,
 circuit, DEM, decoder prediction, metadata 등을 저장한다.
 """
class ExperimentOutput:
    # 사용한 실험 조건 저장
    config: ExperimentConfig
    
    # 생성된 quantum circuit과 detector error model.
    # domain layer가 특정 simulator에 의존하지 않도록 Any로 정의.
    circuit: Any
    detector_error_model: Any

    # detector ID별 공간/시간 좌표(각 detector의 위치)
    # 향후 syndrome graph 생성 시 node 위치 정보로 사용.
    detector_coordinates: Mapping[int, Sequence[float]]

    # simulation에서 생성된 detection events 및 logical observables
    batch: SampleBatch

    # decoder가 예측한 logical observable
    predictions: np.ndarray

    # decoder 평가 결과
    evaluation: EvaluationResult

    # 실험 재현성과 분석을 위한 metadata
    metadata: Mapping[str, object]


@dataclass(frozen=True)
class RunSummary:
"""
QEC experiment 완료 후 호출자에게 반환하는 경량 실행 결과.
대용량 syndrome 배열이나 circuit 객체는 제외하고,
결과 저장 위치와 핵심 평가/metadata만 제공한다.
"""
    output_dir: Path
    evaluation: EvaluationResult
    metadata: Mapping[str, object]
