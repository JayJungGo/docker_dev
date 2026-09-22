"""
실험 조건 입력 패널 (INPUT 영역).

Nielsen:
  - Error prevention: SpinBox/ComboBox로 잘못된 형식 입력 차단
  - Recognition over recall: 라벨 + 툴팁
  - Match between system and real world: 한국어 설명
"""
from __future__ import annotations

from pathlib import Path
from typing import Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from ..services.config_form_mapper import FIELD_SPECS, FieldSpec
from ..widgets.tooltip import apply_tooltip, labeled_field


class InputPanel(QGroupBox):
    """ExperimentConfig 필드를 개별 위젯으로 입력받는 패널."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__("입력 (INPUT) — 실험 조건", parent)
        self._widgets: dict[str, QWidget] = {}
        self._path_edit: QLineEdit | None = None

        layout = QFormLayout(self)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        for spec in FIELD_SPECS:
            field = self._build_field(spec)
            self._widgets[spec.key] = field
            label = labeled_field(spec.label, spec.tooltip)
            layout.addRow(label, field)

        hint = QLabel(
            "각 항목에 마우스를 올리면 설명이 표시됩니다. "
            "rounds는 비워 두면 distance와 동일합니다."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #555;")
        layout.addRow(hint)

    def values(self) -> Mapping[str, object]:
        """현재 입력값을 dict로 반환한다."""
        result: dict[str, object] = {}
        for spec in FIELD_SPECS:
            widget = self._widgets[spec.key]
            if isinstance(widget, QComboBox):
                result[spec.key] = widget.currentText()
            elif isinstance(widget, QSpinBox):
                result[spec.key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                result[spec.key] = widget.value()
            else:
                result[spec.key] = self._read_composite(spec, widget)
        return result

    def reset_defaults(self) -> None:
        """모든 필드를 기본값으로 되돌린다."""
        for spec in FIELD_SPECS:
            widget = self._widgets[spec.key]
            if isinstance(widget, QComboBox):
                widget.setCurrentText(str(spec.default))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(spec.default))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(spec.default))
            elif spec.widget == "optional_int":
                line = widget.findChild(QLineEdit)
                if line is not None:
                    line.setText(
                        "" if spec.default is None else str(spec.default)
                    )
            elif spec.widget == "path" and self._path_edit is not None:
                self._path_edit.setText(str(spec.default))

    def set_busy(self, busy: bool) -> None:
        """실행 중 입력 변경을 막는다."""
        self.setEnabled(not busy)

    def _build_field(self, spec: FieldSpec) -> QWidget:
        if spec.widget == "combo":
            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(list(spec.choices))
            combo.setCurrentText(str(spec.default))
            apply_tooltip(combo, spec.tooltip)
            return combo

        if spec.widget == "int":
            spin = QSpinBox()
            spin.setRange(int(spec.minimum or 0), int(spec.maximum or 10**9))
            spin.setValue(int(spec.default))
            apply_tooltip(spin, spec.tooltip)
            return spin

        if spec.widget == "float":
            spin = QDoubleSpinBox()
            spin.setDecimals(6)
            spin.setSingleStep(0.0001)
            spin.setRange(
                float(spec.minimum or 0.0),
                float(spec.maximum or 1.0),
            )
            spin.setValue(float(spec.default))
            apply_tooltip(spin, spec.tooltip)
            return spin

        if spec.widget == "optional_int":
            line = QLineEdit()
            line.setPlaceholderText("비우면 distance와 동일 (auto)")
            if spec.default is not None:
                line.setText(str(spec.default))
            apply_tooltip(line, spec.tooltip)
            wrapper = QWidget()
            layout = QHBoxLayout(wrapper)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(line)
            wrapper.setProperty("field_kind", "optional_int")
            return wrapper

        if spec.widget == "path":
            return self._build_path_field(spec)

        raise ValueError(f"지원하지 않는 위젯 유형: {spec.widget}")

    def _build_path_field(self, spec: FieldSpec) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        edit = QLineEdit(str(spec.default))
        apply_tooltip(edit, spec.tooltip)
        self._path_edit = edit

        browse = QPushButton("찾아보기…")
        browse.setToolTip("데이터셋이 저장될 폴더를 선택합니다.")
        browse.clicked.connect(self._choose_directory)

        layout.addWidget(edit, stretch=1)
        layout.addWidget(browse)
        container.setProperty("field_kind", "path")
        return container

    def _choose_directory(self) -> None:
        assert self._path_edit is not None
        start = self._path_edit.text().strip() or str(Path.home())
        selected = QFileDialog.getExistingDirectory(
            self,
            "결과 저장 디렉터리 선택",
            start,
        )
        if selected:
            self._path_edit.setText(selected)

    def _read_composite(self, spec: FieldSpec, widget: QWidget) -> object:
        kind = widget.property("field_kind")
        if kind == "optional_int":
            line = widget.findChild(QLineEdit)
            return "" if line is None else line.text()
        if kind == "path":
            assert self._path_edit is not None
            return self._path_edit.text()
        raise ValueError(f"알 수 없는 필드: {spec.key}")
