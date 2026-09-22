"""
Stim 회로를 GUI 표시용 이미지(SVG→PNG/바이트)로 변환한다.

SOLID:
  - S: 회로 렌더링만 담당한다.
  - D: 상위 계층은 이 서비스 인터페이스에만 의존한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import QByteArray, QRectF
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

from ...domain import ExperimentConfig
from ...stim_backend import StimCircuitBuilder


class CircuitRenderer(Protocol):
    """회로 미리보기 렌더러 계약."""

    def render_svg(self, config: ExperimentConfig) -> str:
        ...

    def render_image(
        self,
        config: ExperimentConfig,
        max_width: int = 1600,
    ) -> QImage:
        ...


@dataclass(frozen=True)
class CircuitPreview:
    """회로 미리보기 결과."""

    svg_text: str
    image: QImage
    num_qubits: int
    num_detectors: int
    num_observables: int
    circuit_text_preview: str


class StimCircuitRenderer:
    """Stim timeline-svg 다이어그램을 Qt 이미지로 변환한다."""

    def __init__(
        self,
        circuit_builder: StimCircuitBuilder | None = None,
        diagram_type: str = "timeline-svg",
    ):
        self._circuit_builder = circuit_builder or StimCircuitBuilder()
        self._diagram_type = diagram_type

    def build_preview(
        self,
        config: ExperimentConfig,
        max_width: int = 1600,
    ) -> CircuitPreview:
        """설정을 검증한 뒤 회로를 생성하고 미리보기를 반환한다."""
        config.validate()
        circuit = self._circuit_builder.build(config)
        svg_text = str(circuit.diagram(self._diagram_type))
        image = self._svg_to_image(svg_text, max_width=max_width)
        preview_text = str(circuit)
        if len(preview_text) > 4000:
            preview_text = preview_text[:4000] + "\n... (truncated)"

        return CircuitPreview(
            svg_text=svg_text,
            image=image,
            num_qubits=circuit.num_qubits,
            num_detectors=circuit.num_detectors,
            num_observables=circuit.num_observables,
            circuit_text_preview=preview_text,
        )

    @staticmethod
    def _svg_to_image(svg_text: str, max_width: int) -> QImage:
        renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
        if not renderer.isValid():
            raise ValueError(
                "회로 SVG 다이어그램을 렌더링할 수 없습니다. "
                "distance/rounds를 줄인 뒤 다시 시도하세요."
            )

        size = renderer.defaultSize()
        if size.width() <= 0 or size.height() <= 0:
            raise ValueError("회로 다이어그램 크기가 유효하지 않습니다.")

        scale = min(1.0, max_width / float(size.width()))
        width = max(1, int(size.width() * scale))
        height = max(1, int(size.height() * scale))

        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(0xFFFFFFFF)
        painter = QPainter(image)
        renderer.render(painter, QRectF(0, 0, width, height))
        painter.end()
        return image
