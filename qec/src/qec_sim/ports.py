# qec/src/qec_sim/ports.py
"""
QEC simulation pipeline의 인터페이스(Port)를 정의하는 모듈.
ㅁ 목적: Application layer(ExperimentRunner)가 특정 라이브러리에 직접 의존하지 않도록 각 기능의 계약(interface)을 정의한다.
ㅁ 유지보수 원칙
 1. 각 Protocol은 하나의 책임만 가진다.
 2. 이 모듈에는 Stim, PyMatching, PyTorch 등의 구체적인 구현 코드를 작성하지 않는다.
 3. 구현체가 아니라 추상 인터페이스에 의존한다.
 4. 새로운 simulator, decoder, storage backend를 추가하더라도 ExperimentRunner의 변경을 최소화한다.
 5. 이 파일에서는 실제 계산, 파일 저장, simulation 등의 비즈니스 로직을 구현하지 않는다.
 6. 기존 Port로 표현할 수 있는 기능인지 확인한다.
 7. 가능하면 새로운 구현체(Adapter)를 추가한다.
 8. 기존 Port를 수정하는 것은 마지막 수단으로 한다.
 9. Protocol의 method signature를 변경하면 모든 구현체에 영향을 주므로 신중하게 변경한다.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
import numpy as np
from .domain import (
    CircuitStats,
    EvaluationResult,
    ExperimentConfig,
    ExperimentOutput,
    SampleBatch,
)

class CircuitBuilder(Protocol):
"""
QEC circuit을 생성하는 객체의 인터페이스.
ExperimentConfig에 정의된 code distance, rounds, noise parameter 등의 조건을 이용하여 circuit 객체를 생성한다.
유지보수 규칙:
 - CircuitBuilder의 구현체는 회로 생성만 담당해야 한다.
 - syndrome sampling이나 decoding 기능을 이 객체에 추가하지 않는다.
"""
    def build(
        self,
        config: ExperimentConfig,
    ) -> Any:
        ...
        """
        실험 설정을 기반으로 QEC circuit을 생성한다.
        Returns:
          Simulator가 사용하는 circuit 객체.
          현재 Stim backend에서는 stim.Circuit이 반환된다.
          향후 다른 simulator를 지원하기 위해 반환 타입은 Any로 정의한다.
        """

class DetectorErrorModelBuilder(Protocol):
"""
Circuit으로부터 decoder가 사용할 error model을 생성한다.
이 기능을 CircuitBuilder와 분리한 이유는 회로 생성과 오류 모델 생성의 책임을 독립적으로 관리하기 위함이다.
"""
    def build(
        self,
        circuit: Any,
    ) -> Any:
        ...
        """
        Circuit에서 detector error model을 생성한다.
        Args:
          circuit:
            simulator에서 생성된 QEC circuit.
        Returns:
          Decoder가 사용할 detector error model.
        """

class SyndromeSampler(Protocol):
"""
QEC circuit을 반복 실행하여 syndrome 데이터를 생성한다.
현재 pipeline에서 syndrome 데이터는 주로 detection event와 logical observable로 구성한다.
이 객체는 decoding 및 성능 평가는 수행하지 않는다.
데이터 생성만 담당한다.
"""
    def sample(
        self,
        circuit: Any,
        shots: int,
        seed: int,
    ) -> SampleBatch:
        ...
        """
        Circuit에서 syndrome sample을 생성한다.
        Args:
          circuit:
    	    샘플링할 QEC circuit.
          shots:
            생성할 Monte Carlo sample 개수.
          seed:
            random sampling 재현성을 위한 seed.
        Returns:
          SampleBatch:
            detections:
              detector event 배열.
            observables:
              logical observable flip 배열.
        """

class Decoder(Protocol):
"""
Syndrome 데이터를 decoding하는 객체의 공통 인터페이스.
ExperimentRunner는 구체적인 decoder 종류를 알 필요가 없으며, 이 인터페이스의 decode()만 호출한다.
따라서 새로운 decoder를 추가하더라도 ExperimentRunner를 수정하지 않는 것이 원칙이다.
Decoder Protocol을 구현한 새로운 Adapter를 추가한다.
"""
    def decode(
        self,
        detector_error_model: Any,
        detections: np.ndarray,
    ) -> np.ndarray:
        ...
        """
        Detection event로부터 logical correction을 예측한다.
        Args:
          detector_error_model:
            decoding에 필요한 error model.
          detections:
            shape 예:
              (shots, num_detectors)
            각 shot에서 발생한 detection event 정보.
        Returns:
          np.ndarray:
            shape 예:
              (shots, num_observables)
            decoder가 예측한 logical observable correction.
        """

class Evaluator(Protocol):
"""
Decoder prediction과 실제 logical observable을 비교하여 decoding 성능을 평가한다.
현재 주요 평가 항목:
 - logical error count
 - logical error rate
 - detection event density
향후 별도의 evaluator를 통해 latency, throughput 등의 metric을 추가할 수 있다.
"""
    def evaluate(
        self,
        predictions: np.ndarray,
        batch: SampleBatch,
    ) -> EvaluationResult:
        ...
        """
        Decoder의 예측 결과를 평가한다.
        Args:
          predictions:
            decoder가 예측한 logical correction.
          batch:
            실제 logical observable과 detection event가 포함된 sampling 결과.
        Returns:
          EvaluationResult:
            실험 성능 지표.
        """

class CircuitInspector(Protocol):
"""
Circuit을 변경하지 않고 구조적 정보를 조회하는 인터페이스.
Circuit 생성과 분석을 분리하여 CircuitBuilder가 지나치게 많은 책임을 갖지 않도록 한다.
특히 detector coordinate는 이후 syndrome을 graph 데이터로 변환할 때 사용될 수 있다.
"""
    def get_stats(
        self,
        circuit: Any,
    ) -> CircuitStats:
        ...
        """
        Circuit의 기본 통계 정보를 반환한다.
        Returns:
          CircuitStats:
            - num_qubits
            - num_detectors
            - num_observables
        """

    def get_detector_coordinates(
        self,
        circuit: Any,
    ) -> Mapping[int, Sequence[float]]:
        ...
        """
        Detector의 공간/시간 좌표를 반환한다.
              이 정보는 향후 GNN dataset 생성 시 detector를 graph node로 변환하는 데 활용할 수 있다.
        """

class RuntimeInfoProvider(Protocol):
"""
연구/실험 재현성에 필요한 실행환경 정보를 제공한다.
Python version, Stim version, PyMatching version, NumPy version 등 시스템 환경을 metadata 생성 로직과 분리하기 위한 인터페이스다.
"""
    def get_info(
        self,
    ) -> Mapping[str, str]:
        ...
        """
        현재 실행환경 정보를 key-value 형태로 반환한다.
        """

class MetadataFactory(Protocol):
"""
실험 결과와 설정을 이용하여 metadata를 생성한다.
Metadata는 실험 재현성을 확보하기 위한 목적으로 사용한다.
"""
    def build(
        self,
        config: ExperimentConfig,
        stats: CircuitStats,
        evaluation: EvaluationResult,
        circuit_text: str,
    ) -> Mapping[str, object]:
        ...
        """
        하나의 실험에 대한 metadata를 생성한다.
        이 메서드는 metadata만 생성하며 실제 파일 저장은 담당하지 않는다.
        """

class ResultWriter(Protocol):
"""
ExperimentOutput을 외부 저장소에 저장하는 인터페이스.
현재 구현:
 - FileSystemResultWriter
저장 방식이 바뀌더라도 simulation pipeline은 영향을 받지 않도록 하기 위한 인터페이스다.
"""
    def write(
        self,
        output: ExperimentOutput,
    ) -> Path:
        ...
        """
        실험 결과를 저장한다.
        Args:
          output:
            circuit, syndrome, prediction, metadata 등이 포함된 전체 실험 결과.
        Returns:
          Path:
            결과가 저장된 위치.
        """
