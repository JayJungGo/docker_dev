"""
QEC Simulator GUI 애플리케이션 진입점.

Windows / Linux 모두에서 `python -m qec_sim.gui` 또는 패키징된 실행 파일로 기동한다.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    """개발 실행 시 src 경로를 sys.path에 추가한다."""
    here = Path(__file__).resolve()
    src_root = here.parents[2]  # .../qec/src
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def main(argv: list[str] | None = None) -> int:
    """Qt 애플리케이션을 기동한다."""
    _ensure_src_on_path()

    from PySide6.QtWidgets import QApplication

    from .controllers.experiment_controller import ExperimentController
    from .views.main_window import MainWindow

    app = QApplication(argv or sys.argv)
    app.setApplicationName("QEC Quantum Simulator")
    app.setOrganizationName("ai-stack")

    window = MainWindow(ExperimentController())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
