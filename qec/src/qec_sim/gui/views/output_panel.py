"""
실험 결과 출력 패널 (OUTPUT 영역).

- 양자 회로 다이어그램 이미지
- 데이터 생성 결과 요약 텍스트
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGroupBox,
    QLabel,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..services.circuit_renderer import CircuitPreview


class OutputPanel(QGroupBox):
    """회로 그림과 실행 요약을 표시하는 출력 패널."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__("출력 (OUTPUT) — 회로 및 결과 요약", parent)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # 회로 다이어그램
        circuit_box = QGroupBox("양자 회로 다이어그램")
        circuit_layout = QVBoxLayout(circuit_box)
        self._circuit_label = QLabel(
            "회로 미리보기 또는 실험 실행 후 여기에 표시됩니다."
        )
        self._circuit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._circuit_label.setMinimumHeight(220)
        self._circuit_label.setStyleSheet(
            "background: #fafafa; border: 1px solid #ddd;"
        )
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._circuit_label)
        circuit_layout.addWidget(scroll)

        # 요약
        summary_box = QGroupBox("데이터 생성 결과 요약")
        summary_layout = QVBoxLayout(summary_box)
        self._summary = QTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setPlaceholderText(
            "실험 실행 후 logical error rate, 저장 경로 등이 표시됩니다."
        )
        summary_layout.addWidget(self._summary)

        splitter.addWidget(circuit_box)
        splitter.addWidget(summary_box)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root = QVBoxLayout(self)
        root.addWidget(splitter)

    def show_preview(self, preview: CircuitPreview) -> None:
        """회로 미리보기를 출력한다."""
        pixmap = QPixmap.fromImage(preview.image)
        self._circuit_label.setPixmap(pixmap)
        self._circuit_label.setMinimumSize(pixmap.size())
        self._summary.setPlainText(
            "=== 회로 미리보기 ===\n"
            f"qubits      : {preview.num_qubits}\n"
            f"detectors   : {preview.num_detectors}\n"
            f"observables : {preview.num_observables}\n\n"
            "전체 실험은 '실험 실행' 버튼을 눌러 주세요.\n\n"
            "--- circuit.stim (일부) ---\n"
            f"{preview.circuit_text_preview}"
        )

    def show_summary(self, text: str, preview: CircuitPreview | None) -> None:
        """실행 요약과 회로 그림을 함께 표시한다."""
        if preview is not None:
            pixmap = QPixmap.fromImage(preview.image)
            self._circuit_label.setPixmap(pixmap)
            self._circuit_label.setMinimumSize(pixmap.size())
        self._summary.setPlainText(text)

    def show_status(self, message: str) -> None:
        """진행 상태를 요약 영역에 표시한다."""
        self._summary.setPlainText(message)
