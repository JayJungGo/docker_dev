# qec/src/qec_sim/stim_backend.py
"""
Stim 기반 QEC simulation 기능을 구현하는 Adapter 모듈.
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
    """ExperimentConfig를 기반으로 Stim QEC circuit을 생성한다."""

    def build(
        self,
        config: ExperimentConfig,
    ) -> stim.Circuit:
        """
        실험 설정에 따라 Stim surface-code circuit을 생성한다.
        Returns:
          stim.Circuit: Stim으로 생성된 QEC circuit.
        """
        return stim.Circuit.generated(
            config.task,
            distance=config.distance,
            rounds=config.effective_rounds,
            after_clifford_depolarization=
                config.depolarizing_p,
            before_measure_flip_probability=
                config.measurement_p,
        )


class StimDetectorErrorModelBuilder:
    """Stim Circuit으로부터 Detector Error Model(DEM)을 생성한다."""

    def __init__(
        self,
        decompose_errors: bool = True,
    ):
        """
        Args:
          decompose_errors:
            복합 오류를 PyMatching 등이 처리하기 쉬운 형태로 분해할지 여부.
        """
        self._decompose_errors = decompose_errors

    def build(
        self,
        circuit: stim.Circuit,
    ) -> stim.DetectorErrorModel:
        """
        Stim circuit으로부터 Detector Error Model을 생성한다.
        Returns:
          stim.DetectorErrorModel: Decoder가 사용할 Detector Error Model.
        """
        return circuit.detector_error_model(
            decompose_errors=self._decompose_errors
        )


class StimSyndromeSampler:
    """Stim circuit으로부터 syndrome 관련 데이터를 샘플링한다."""

    def sample(
        self,
        circuit: stim.Circuit,
        shots: int,
        seed: int,
    ) -> SampleBatch:
        """
        지정된 shots만큼 batch 단위로 detection event를 생성한다.
        Returns:
          SampleBatch: detections와 observables를 포함한 sampling 결과.
        """
        sampler = circuit.compile_detector_sampler(
            seed=seed
        )
        detections, observables = sampler.sample(
            shots=shots,
            separate_observables=True,
        )
        return SampleBatch(
            detections=detections,
            observables=observables,
        )


class StimCircuitInspector:
    """Stim circuit의 구조적 정보를 조회하는 read-only 객체."""

    def get_stats(
        self,
        circuit: stim.Circuit,
    ) -> CircuitStats:
        """QEC circuit의 기본 규모 정보를 반환한다."""
        return CircuitStats(
            num_qubits=circuit.num_qubits,
            num_detectors=circuit.num_detectors,
            num_observables=circuit.num_observables,
        )

    def get_detector_coordinates(
        self,
        circuit: stim.Circuit,
    ) -> Mapping[int, Sequence[float]]:
        """Stim detector의 공간·시간 좌표를 반환한다."""
        return circuit.get_detector_coordinates()
