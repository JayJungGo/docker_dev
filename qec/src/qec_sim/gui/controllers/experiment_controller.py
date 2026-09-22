"""
GUI와 도메인 계층 사이의 유스케이스 컨트롤러.

SOLID:
  - S: UI 이벤트 → 도메인 호출 조율만 담당한다.
  - D: ExperimentRunner / CircuitRenderer 추상에 의존한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ...domain import ExperimentConfig, RunSummary
from ...factory import build_runner
from ...runner import ExperimentRunner
from ..services.circuit_renderer import CircuitPreview, StimCircuitRenderer
from ..services.config_form_mapper import ConfigFormMapper
from ..services.error_presenter import ErrorPresenter, UserFacingError


@dataclass(frozen=True)
class RunPresentation:
    """출력 영역에 표시할 실행 결과 요약."""

    summary_text: str
    output_dir: Path
    preview: CircuitPreview | None


class ExperimentController:
    """입력 폼 값을 검증하고 미리보기/실험을 실행한다."""

    def __init__(
        self,
        mapper: ConfigFormMapper | None = None,
        renderer: StimCircuitRenderer | None = None,
        error_presenter: ErrorPresenter | None = None,
        runner: ExperimentRunner | None = None,
    ):
        self._mapper = mapper or ConfigFormMapper()
        self._renderer = renderer or StimCircuitRenderer()
        self._error_presenter = error_presenter or ErrorPresenter()
        self._runner = runner or build_runner()

    def parse_config(
        self,
        values: Mapping[str, object],
    ) -> ExperimentConfig:
        """폼 값을 ExperimentConfig로 변환한다."""
        return self._mapper.to_config(values)

    def preview_circuit(
        self,
        values: Mapping[str, object],
    ) -> CircuitPreview:
        """회로만 생성하여 다이어그램 미리보기를 반환한다."""
        config = self.parse_config(values)
        return self._renderer.build_preview(config)

    def run_experiment(
        self,
        values: Mapping[str, object],
    ) -> RunPresentation:
        """전체 QEC 파이프라인을 실행하고 요약 결과를 반환한다."""
        config = self.parse_config(values)
        # 저장 경로가 없으면 생성 시도(오류 방지/복구 지원)
        config.output_dir.mkdir(parents=True, exist_ok=True)

        preview = self._renderer.build_preview(config)
        summary = self._runner.run(config)
        return RunPresentation(
            summary_text=self._format_summary(config, summary, preview),
            output_dir=summary.output_dir,
            preview=preview,
        )

    def present_error(self, exc: BaseException) -> UserFacingError:
        """예외를 사용자용 메시지로 변환한다."""
        return self._error_presenter.present(exc)

    @staticmethod
    def _format_summary(
        config: ExperimentConfig,
        summary: RunSummary,
        preview: CircuitPreview,
    ) -> str:
        evaluation = summary.evaluation
        lines = [
            "=== 데이터 생성 결과 요약 ===",
            f"저장 위치: {summary.output_dir}",
            "",
            "[실험 조건]",
            f"  task             : {config.task}",
            f"  distance         : {config.distance}",
            f"  rounds           : {config.effective_rounds}",
            f"  depolarizing_p   : {config.depolarizing_p}",
            f"  measurement_p    : {config.measurement_p}",
            f"  shots            : {config.shots}",
            f"  seed             : {config.seed}",
            "",
            "[회로 규모]",
            f"  qubits           : {preview.num_qubits}",
            f"  detectors        : {preview.num_detectors}",
            f"  observables      : {preview.num_observables}",
            "",
            "[디코더 평가]",
            f"  logical_errors          : {evaluation.logical_errors}",
            f"  logical_error_rate      : {evaluation.logical_error_rate:.6g}",
            f"  detection_event_density : "
            f"{evaluation.detection_event_density:.6g}",
            "",
            "[생성 파일]",
            "  detection_events.npy",
            "  observables.npy",
            "  mwpm_predictions.npy",
            "  circuit.stim",
            "  detector_error_model.dem",
            "  detector_coordinates.json",
            "  metadata.json",
        ]
        return "\n".join(lines)
