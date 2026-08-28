# QEC 시뮬레이션 실험에서 사용할 데이터구조 정의 객체
# 연구 파이프라인에서 데이터가 이동할 때 사용하는 표준 용기(container)
## QEC 시뮬레이션 실험의 입력, 중간 결과, 평가 결과, 최종 결과를 표현하는 데이터 객체를 정의한다.

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import numpy as np

@dataclass(frozen=True)

# QEC 실험 조건 정의 클래스
"""
하나의 surface-code QEC simulation experiment를 정의하는 설정 객체.
회로 종류, code distance, stabilizer measurement round,
physical/measurement noise rate, Monte Carlo shots 및 seed 등을 관리한다.
frozen=True를 사용하여 실험 시작 후 설정이 변경되는 것을 방지하고
experiment reproducibility를 유지한다.
"""
class ExperimentConfig:
    # Stim에서 생성할 QEC 회로 종류
    task: str = "surface_code:rotated_memory_x"

    # Surface code의 code distance
    distance: int = 3

    # Stabilizer measurement 반복 횟수
    # None이면 effective_rounds에서 distance와 동일한 값 사용
    rounds: int | None = None

    # Clifford gate 수행 후 적용할 depolarizing noise 확률
    depolarizing_p: float = 0.001

    # Stabilizer 측정 과정에서 발생하는 measurement flip 확률
    measurement_p: float = 0.001

    # 동일한 QEC circuit을 반복 simulation할 횟수
    # Monte Carlo simulation 반복 횟수 = 생성 syndrome sample 수
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
    잘못된 설정이 존재하면 simulation 실행 전에 문제를 차단한다.
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
detections: 각 shot에서 발생한 detection event 배열.
observables:  각 shot의 실제 logical observable flip 정보.
"""
class SampleBatch:
    detections: np.ndarray
    observables: np.ndarray


@dataclass(frozen=True)
"""
생성된 QEC circuit의 구조적 규모를 나타내는 통계정보.
code distance 증가에 따른 circuit 규모와 decoder scalability를 분석하기 위한 metadata로 사용한다.
"""
class CircuitStats:
    num_qubits: int
    num_detectors: int
    num_observables: int

@dataclass(frozen=True)
# QEC decoder의 성능 평가 결과.
class EvaluationResult:
    logical_errors: int
    logical_error_rate: float
    detection_event_density: float

@dataclass(frozen=True)
"""
하나의 QEC simulation/decoding experiment에서 생성된 전체 결과를 하나의 객체로 묶어 표현한다.
ResultWriter가 이 객체를 받아 raw dataset, circuit, DEM, decoder prediction, metadata 등을 저장한다.
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
