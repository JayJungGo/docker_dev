"""
메인 윈도우: INPUT / OUTPUT 분리 및 액션 버튼.

Nielsen:
  - Visibility of system status: 상태바 + 진행 표시
  - User control and freedom: 초기화 / 미리보기 / 실행 분리
  - Help and documentation: 도움말 메뉴
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..controllers.experiment_controller import (
    ExperimentController,
    RunPresentation,
)
from .input_panel import InputPanel
from .output_panel import OutputPanel


class _Worker(QObject):
    """백그라운드에서 미리보기/실험을 실행하는 워커."""

    finished_preview = Signal(object)
    finished_run = Signal(object)
    failed = Signal(object)

    def __init__(
        self,
        controller: ExperimentController,
        values: dict,
        mode: str,
    ):
        super().__init__()
        self._controller = controller
        self._values = values
        self._mode = mode

    @Slot()
    def run(self) -> None:
        try:
            if self._mode == "preview":
                result = self._controller.preview_circuit(self._values)
                self.finished_preview.emit(result)
            else:
                result = self._controller.run_experiment(self._values)
                self.finished_run.emit(result)
        except Exception as exc:  # noqa: BLE001 — GUI 경계에서 사용자 메시지로 변환
            self.failed.emit(exc)


class MainWindow(QMainWindow):
    """QEC Simulator 메인 창."""

    def __init__(
        self,
        controller: ExperimentController | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._controller = controller or ExperimentController()
        self._thread: QThread | None = None
        self._worker: _Worker | None = None

        self.setWindowTitle("QEC Quantum Simulator")
        self.resize(1280, 840)

        self._input = InputPanel()
        self._output = OutputPanel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._input)
        splitter.addWidget(self._output)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        self._btn_preview = QPushButton("회로 미리보기")
        self._btn_preview.setToolTip(
            "실험 조건으로 양자 회로만 생성하여 다이어그램을 표시합니다."
        )
        self._btn_run = QPushButton("실험 실행")
        self._btn_run.setToolTip(
            "회로 생성 → 샘플링 → 디코딩 → 결과 저장까지 전체 파이프라인을 실행합니다."
        )
        self._btn_reset = QPushButton("입력 초기화")
        self._btn_reset.setToolTip("모든 입력값을 기본값으로 되돌립니다.")

        self._btn_preview.clicked.connect(self._on_preview)
        self._btn_run.clicked.connect(self._on_run)
        self._btn_reset.clicked.connect(self._input.reset_defaults)

        buttons = QHBoxLayout()
        buttons.addWidget(self._btn_reset)
        buttons.addStretch(1)
        buttons.addWidget(self._btn_preview)
        buttons.addWidget(self._btn_run)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)

        central = QWidget()
        root = QVBoxLayout(central)
        root.addWidget(splitter, stretch=1)
        root.addLayout(buttons)
        root.addWidget(self._progress)
        self.setCentralWidget(central)

        status = QStatusBar()
        status.showMessage(
            "준비됨 — 실험 조건을 입력한 뒤 회로 미리보기 또는 실험 실행을 선택하세요."
        )
        self.setStatusBar(status)

        help_action = self.menuBar().addAction("도움말")
        help_action.triggered.connect(self._show_help)

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "사용 안내",
            (
                "1) 왼쪽 INPUT에서 ExperimentConfig 실험 조건을 입력합니다.\n"
                "2) 각 항목에 마우스를 올리면 설명이 나타납니다.\n"
                "3) '찾아보기'로 결과 저장 폴더를 지정합니다.\n"
                "4) '회로 미리보기'로 양자 회로 그림을 확인합니다.\n"
                "5) '실험 실행'으로 데이터셋을 생성합니다.\n"
                "6) 오른쪽 OUTPUT에서 회로와 결과 요약을 확인합니다.\n\n"
                "권장 시작값: distance=3, shots=1000"
            ),
        )

    def _on_preview(self) -> None:
        self._start_worker("preview", "회로를 생성하는 중…")

    def _on_run(self) -> None:
        reply = QMessageBox.question(
            self,
            "실험 실행 확인",
            (
                "현재 입력 조건으로 시뮬레이션을 실행할까요?\n"
                "shots가 크면 시간이 오래 걸릴 수 있습니다."
            ),
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._start_worker("run", "실험을 실행하는 중… (잠시만 기다려 주세요)")

    def _start_worker(self, mode: str, status_message: str) -> None:
        if self._thread is not None:
            QMessageBox.warning(
                self,
                "작업 진행 중",
                "이미 작업이 실행 중입니다. 완료될 때까지 기다려 주세요.",
            )
            return

        values = dict(self._input.values())
        self._set_busy(True, status_message)

        thread = QThread(self)
        worker = _Worker(self._controller, values, mode)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished_preview.connect(self._on_preview_done)
        worker.finished_run.connect(self._on_run_done)
        worker.failed.connect(self._on_failed)
        worker.finished_preview.connect(thread.quit)
        worker.finished_run.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(self._clear_thread)

        self._thread = thread
        self._worker = worker
        thread.start()

    @Slot(object)
    def _on_preview_done(self, preview: object) -> None:
        self._output.show_preview(preview)  # type: ignore[arg-type]
        self._set_busy(False, "회로 미리보기 완료")

    @Slot(object)
    def _on_run_done(self, presentation: object) -> None:
        assert isinstance(presentation, RunPresentation)
        self._output.show_summary(
            presentation.summary_text,
            presentation.preview,
        )
        self._set_busy(
            False,
            f"실험 완료 — 저장 위치: {presentation.output_dir}",
        )
        QMessageBox.information(
            self,
            "실험 완료",
            (
                f"결과가 저장되었습니다.\n\n"
                f"{presentation.output_dir}\n\n"
                "OUTPUT 영역에서 회로와 요약을 확인하세요."
            ),
        )

    @Slot(object)
    def _on_failed(self, exc: object) -> None:
        assert isinstance(exc, BaseException)
        err = self._controller.present_error(exc)
        self._set_busy(False, f"오류: {err.title}")
        QMessageBox.critical(
            self,
            err.title,
            f"{err.message}\n\n{err.recovery}",
        )

    def _clear_thread(self) -> None:
        self._thread = None
        self._worker = None

    def _set_busy(self, busy: bool, message: str) -> None:
        self._input.set_busy(busy)
        self._btn_preview.setEnabled(not busy)
        self._btn_run.setEnabled(not busy)
        self._btn_reset.setEnabled(not busy)
        self._progress.setVisible(busy)
        self.statusBar().showMessage(message)
        if busy:
            self._output.show_status(message)
