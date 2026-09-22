@echo off
REM Windows용 .exe 빌드 스크립트
REM 사전 조건: Python 3.10+, pip install -r requirements.txt
setlocal
cd /d %~dp0\..

set PYTHONPATH=%CD%\src;%PYTHONPATH%

python -m PyInstaller --noconfirm --clean --distpath dist --workpath build\pyinstaller packaging\qec_sim_gui.spec

echo.
echo Build complete: dist\QEC_Quantum_Simulator.exe
pause
