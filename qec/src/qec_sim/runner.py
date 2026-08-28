# qec/src/qec_sim/runner.py

from __future__ import annotations

from .domain import (
    ExperimentConfig,
    ExperimentOutput,
    RunSummary,
)
from .ports import (
    CircuitBuilder,
    CircuitInspector,
    Decoder,
    DetectorErrorModelBuilder,
    Evaluator,
    MetadataFactory,
    ResultWriter,
    SyndromeSampler,
)


class ExperimentRunner:

    def __init__(
        self,
        circuit_builder: CircuitBuilder,
        error_model_builder:
            DetectorErrorModelBuilder,
        sampler: SyndromeSampler,
        decoder: Decoder,
        evaluator: Evaluator,
        circuit_inspector: CircuitInspector,
        metadata_factory: MetadataFactory,
        result_writer: ResultWriter,
    ):
        self._circuit_builder = (
            circuit_builder
        )

        self._error_model_builder = (
            error_model_builder
        )

        self._sampler = sampler
        self._decoder = decoder
        self._evaluator = evaluator

        self._circuit_inspector = (
            circuit_inspector
        )

        self._metadata_factory = (
            metadata_factory
        )

        self._result_writer = (
            result_writer
        )

    def run(
        self,
        config: ExperimentConfig,
    ) -> RunSummary:

        config.validate()

        # 1. Circuit 생성
        circuit = (
            self._circuit_builder.build(
                config
            )
        )

        # 2. Detector Error Model 생성
        detector_error_model = (
            self._error_model_builder.build(
                circuit
            )
        )

        # 3. Syndrome sampling
        batch = self._sampler.sample(
            circuit=circuit,
            shots=config.shots,
            seed=config.seed,
        )

        # 4. Decoding
        predictions = self._decoder.decode(
            detector_error_model,
            batch.detections,
        )

        # 5. 성능 평가
        evaluation = (
            self._evaluator.evaluate(
                predictions,
                batch,
            )
        )

        # 6. Circuit 정보
        stats = (
            self._circuit_inspector.get_stats(
                circuit
            )
        )

        coordinates = (
            self._circuit_inspector
            .get_detector_coordinates(
                circuit
            )
        )

        # 7. Metadata
        metadata = (
            self._metadata_factory.build(
                config=config,
                stats=stats,
                evaluation=evaluation,
                circuit_text=str(circuit),
            )
        )

        # 8. 저장할 결과 객체 생성
        output = ExperimentOutput(
            config=config,
            circuit=circuit,
            detector_error_model=
                detector_error_model,
            detector_coordinates=
                coordinates,
            batch=batch,
            predictions=predictions,
            evaluation=evaluation,
            metadata=metadata,
        )

        # 9. 파일 저장
        output_dir = (
            self._result_writer.write(
                output
            )
        )

        return RunSummary(
            output_dir=output_dir,
            evaluation=evaluation,
            metadata=metadata,
        )
