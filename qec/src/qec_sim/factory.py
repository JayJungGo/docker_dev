"""
ExperimentRunner 조립(Composition Root)을 담당하는 팩토리 모듈.

SOLID:
  - S: CLI/GUI가 각자 의존성 조립을 중복하지 않도록 단일 생성 책임을 둔다.
  - D: 호출자는 구체 어댑터 대신 ExperimentRunner에만 의존한다.
"""
from __future__ import annotations

from .evaluation import LogicalErrorEvaluator
from .metadata import (
    PackageRuntimeInfoProvider,
    ReproducibilityMetadataBuilder,
)
from .pymatching_backend import PyMatchingDecoder
from .runner import ExperimentRunner
from .stim_backend import (
    StimCircuitBuilder,
    StimCircuitInspector,
    StimDetectorErrorModelBuilder,
    StimSyndromeSampler,
)
from .storage import FileSystemResultWriter, RunNameGenerator


def build_runner() -> ExperimentRunner:
    """
    기본 Stim + PyMatching 파이프라인으로 ExperimentRunner를 생성한다.

    Returns:
        주입이 완료된 ExperimentRunner 인스턴스.
    """
    runtime_info = PackageRuntimeInfoProvider()
    metadata_builder = ReproducibilityMetadataBuilder(runtime_info)
    writer = FileSystemResultWriter(RunNameGenerator())

    return ExperimentRunner(
        circuit_builder=StimCircuitBuilder(),
        error_model_builder=StimDetectorErrorModelBuilder(),
        sampler=StimSyndromeSampler(),
        decoder=PyMatchingDecoder(),
        evaluator=LogicalErrorEvaluator(),
        circuit_inspector=StimCircuitInspector(),
        metadata_factory=metadata_builder,
        result_writer=writer,
    )
