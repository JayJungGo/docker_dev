"""
마우스 오버 시 말풍선(툴팁)을 표시하는 위젯 헬퍼.

커서를 올리면 설명이 나타나고, 내리면 사라진다(Qt 기본 ToolTip 동작).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget


def apply_tooltip(widget: QWidget, text: str) -> None:
    """위젯에 풍선 도움말을 연결한다."""
    widget.setToolTip(text)
    widget.setToolTipDuration(15000)


def labeled_field(text: str, tooltip: str) -> QLabel:
    """툴팁이 포함된 입력 라벨을 생성한다."""
    label = QLabel(text)
    label.setToolTip(tooltip)
    label.setToolTipDuration(15000)
    label.setAlignment(
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    return label
