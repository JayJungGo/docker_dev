# qec/src/qec_sim/stim_backend.py
"""
Stim 기반 QEC simulation 기능을 구현하는 Adapter 모듈. 모든 Stim 기반 구현체를 작성한다.
이 모듈은 ports.py에서 정의한 추상적인 역할을 Stim 라이브러리를 이용하여 실제로 구현함
상위 applicaton layer(ExperimentRunner 등)는 ports.py에 정의된 인터페이스를 통해 본 모듈을 사용한다.
ㅁ 주요 책임:
  1. Stim surface-code circuit 생성
  2. Circuit으로부터 Detector Error Model(DEM) 생성
  3. Circuit에서 detection event / logical observable 샘플링
  4. Circuit의 구조 정보 조회
ㅁ 구현 클래스:
  - StimCircuitBuilder : surface-code circuit 생성
  - StimDetectorErrorModelBuilder : circuit으로부터 Detector Error Model 생성 
  - StimSyndromeSampler: circuit 실행 결과인 detection event 및 logical 데이터 생성
  - StimCircuitInspector: circuit의 큐비트/디텍터/관찰값 수 및 디텍터 coordinate 조회
ㅁ 설계 원칙:
  - Stim과 직접 관련된 코드는 이 모듈에 격리한다.
  - 각 클래스는 하나의 책임만 갖도록 유지한다.
  - decoding, 성능평가, 결과 파일 저장은 담당하지 않는다.
  - 향후 다른 simulator(Qiskit 등)를 지원할 경우:
    이 파일을 수정하는 대신 별도의 backend 모듈을 추가한다.
    예: qiskit_backend.py
"""
from __future__ import annotations
from typing import Any, Mapping, Sequence
import stim
from .domain import (
    CircuitStats,
    ExperimentConfig,
    SampleBatch,
)

class StimCircuitBuilder:
"""
ExperimentConfig를 기반으로 Stim QEC circuit을 생성한다.
현재는 Stim에서 제공하는 generated surface-code circuit을 사용한다.
ㅁ 주요 입력:
  - task
  - distance
  - rounds
  - depolarizing noise probability
  - measurement noise probability
ㅁ 책임 범위:
 - ExperimentConfig -> stim.Circuit
 - '회로 생성'에 한정한다. 
ㅁ 이 클래스에서 하지 않는 것:
  - syndrome sampling
  - Detector Error Model decoding
  - PyMatching 호출
  - logical error rate 계산
  - 결과 파일 저장
ㅁ 유지보수 원칙:
 - 회로를 생성하는 데 필요한 Stim parameter만 이 클래스에서 관리한다.
 - 새로운 simulator(qiskit 등)를 지원하기 위해 이 클래스를 복잡하게 수정하지 말고 별도의 Builder를 구현한다.
 - 다른 Stim 기반 surface-code task 또는 noise parameter를 적용할 경우, 우선적으로 이 클래스를 수정한다.
"""
    def build(
        self,
        config: ExperimentConfig,
    ) -> stim.Circuit:
     """
     실험 설정에 따라 Stim surface-code circuit을 생성한다.
     Args:
       config:
         QEC 실험 설정.
         주요 필드:
             config.task
             config.distance
             config.effective_rounds
             config.depolarizing_p
             config.measurement_p
      Returns:
        stim.Circuit:
          Stim으로 생성된 QEC circuit.
        Notes:
          rounds가 명시되지 않은 경우 ExperimentConfig의 effective_rounds 규칙을 사용한다.
          현재 noise model은:
            - after_clifford_depolarization
            - before_measure_flip_probability
          두 종류를 사용한다.
        """
        return stim.Circuit.generated(
            config.task,
            distance=config.distance,         # Surface code의 code distance.
            rounds=config.effective_rounds,   # 반복 syndrome measurement 횟수.
            after_clifford_depolarization=    # Clifford gate 이후 발생하는 depolarizing noise.
                config.depolarizing_p,
            before_measure_flip_probability=  # measurement 직전에 measurement result가 flip되는 확률.
                config.measurement_p,
        )


class StimDetectorErrorModelBuilder:
"""
Stim Circuit으로부터 Detector Error Model(DEM)을 생성한다.
DEM은 이후 PyMatching과 같은 classical decoder가 syndrome의 오류 구조를 해석하는 데 사용된다.
(physical error에 따른 detection event 및 logical observable의 변화를 표현함)
클래스를 StimCircuitBuilder와 분리한 이유:
  회로 생성과 error model 생성은 서로 다른 책임이기 때문이다.
  향후 DEM 생성 옵션을 변경하더라도 circuit 생성 코드는 수정하지 않아도 된다.
"""
    def __init__(
        self,
        decompose_errors: bool = True,
    ):
    """
    Args:
      decompose_errors:
        복합 오류를 PyMatching 등이 처리하기 쉬운 형태로 분해할지 여부.
                    (graph-like error component)
        현재 baseline에서는 True를 기본값으로 사용한다.
    """
        self._decompose_errors = decompose_errors

    def build(
        self,
        circuit: stim.Circuit,
    ) -> stim.DetectorErrorModel:
        """
        Stim circuit으로부터 Detector Error Model을 생성한다.
        Args:
          circuit:
            Stim으로 생성된 QEC circuit.
        Returns:
          stim.DetectorErrorModel:
            Decoder가 사용할 Detector Error Model.
        """

        return circuit.detector_error_model(
            decompose_errors=self._decompose_errors
        )

class StimSyndromeSampler:
"""
Stim circuit으로부터 syndrome 관련 데이터를 샘플링한다.
ㅁ 현재 생성하는 데이터:
- detection events(raw stabilizer measurement 자체가 아니라 Stim의 DETECTOR 정의에 따라 계산된 데이터)
- logical observables(각 shot에서 logical observable이 뒤집혔는지를 나타내며 decoder 성능 평가 시 ground-truth 역할을 한다.)
ㅁ 이 클래스에서 하지 않는 것:
- decoding
- logical error 판정
- logical error rate 계산
- 파일 저장
ㅁ 중요한 원칙:
SyndromeSampler는 '데이터 생성기'일 뿐 생성된 데이터의 의미를 평가하거나 판단하지 않는다.
"""
    def sample(
        self,
        circuit: stim.Circuit,
        shots: int,
        seed: int,
    ) -> SampleBatch:
    """
	지정된 shots만큼 batch 단위로  detection event를 생성한다.

    Args:
      circuit:
        sampling에 사용할 Stim circuit.
      shots:
        Monte Carlo 시뮬레이션 반복 회수 = sample 개수.
      seed:
        random sampling seed.
        실험 재현성을 위해 metadata에도 함께 기록한다.
    Returns:
      SampleBatch:
        detections:
          각 shot에서 발생한 detection event 배열.
          일반적인 shape:
             (shots, num_detectors)
        observables:
          각 shot에서의 logical observable flip.
          일반적인 shape:
             (shots, num_observables)
    """
        sampler = circuit.compile_detector_sampler(
            seed=seed
        )
        # Stim circuit을 빠르게 반복 sampling할 수 있는 detector sampler를 컴파일한다.

        detections, observables = sampler.sample(
            shots=shots,
            separate_observables=True,  # True를 사용하면 detections와 observables를 분리된 배열로 얻음
        )
        # detection events와 logical observables를 서로 분리하여 반환받는다.

        return SampleBatch(
            detections=detections,
            observables=observables,
        )
        # Stim에서 받은 배열을 domain layer의 SampleBatch 객체로 감싸 반환한다.

class StimCircuitInspector:
"""
Stim circuit의 구조적 정보를 조회하는 read-only 객체.
Circuit을 변경하지 않고 실험 metadata와 향후 graph representation에 필요한 정보를 추출한다.
"""
    def get_stats(
        self,
        circuit: stim.Circuit,
    ) -> CircuitStats:
        """
        QEC circuit의 기본 규모 정보를 반환한다.
        Returns
        -------
        CircuitStats
          num_qubits:
            circuit에서 사용하는 전체 qubit 수.
          num_detectors:
            정의된 detector 수.
          num_observables:
            logical observable 수.        
        """
        return CircuitStats(
            num_qubits=circuit.num_qubits,
            num_detectors=circuit.num_detectors,
            num_observables=circuit.num_observables,
        )

    def get_detector_coordinates(
        self,
        circuit: stim.Circuit,
    ) -> Mapping[int, Sequence[float]]:
        """
        Stim detector의 공간·시간 좌표를 반환한다.
        이 정보는 향후 syndrome을 graph 데이터로 변환할 때
        매우 중요한 입력 정보가 된다.
        Returns
        -------
        Mapping[int, Sequence[float]]
          detector ID를 key로 하고 detector coordinate를 value로 하는 mapping 객체.
        """
        return circuit.get_detector_coordinates()
py
