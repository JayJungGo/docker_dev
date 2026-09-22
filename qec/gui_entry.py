#!/usr/bin/env python3
"""PyInstaller용 GUI 진입 스크립트 (크로스 플랫폼)."""
from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap() -> None:
    # 소스 트리에서 직접 실행할 때 대비
    src = Path(__file__).resolve().parents[1] / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    _bootstrap()
    from qec_sim.gui.app import main as gui_main

    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
