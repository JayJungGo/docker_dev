# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Linux/Windows 공통.

numpy 2.x는 구현이 numpy._core 로 이동했고,
stim/pymatching 등은 여전히 numpy.core.multiarray 를 import 한다.
따라서 numpy 전체(호환 패키지 numpy.core 포함)를 명시적으로 수집해야 한다.
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

SPECDIR = Path(SPECPATH).resolve()
ROOT = SPECDIR.parent
ENTRY = str(ROOT / "gui_entry.py")
SRC = str(ROOT / "src")

block_cipher = None

excludes = [
    "torch",
    "torchvision",
    "torchaudio",
    "tensorflow",
    "tensorboard",
    "jax",
    "jaxlib",
    "IPython",
    "jupyter",
    "notebook",
]

datas = []
binaries = []
hiddenimports = [
    "qec_sim",
    "qec_sim.gui",
    "qec_sim.gui.app",
    "qec_sim.gui.views.main_window",
    "qec_sim.gui.controllers.experiment_controller",
    "PySide6.QtSvg",
    # numpy 2.x 호환 경로 (stim/pymatching C 확장이 참조)
    "numpy.core",
    "numpy.core.multiarray",
    "numpy.core._multiarray_umath",
    "numpy._core",
    "numpy._core.multiarray",
    "numpy._core._multiarray_umath",
]

for pkg in ("numpy", "stim", "pymatching", "PySide6", "shiboken6"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    [ENTRY],
    pathex=[SRC],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="QEC_Quantum_Simulator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
