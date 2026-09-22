# QEC Simulator (GUI)

Surface-code QEC 시뮬레이션 GUI 및 실행 파일 패키징.

## 빠른 실행

```bash
cd qec
pip install -r requirements.txt
export PYTHONPATH="$PWD/src"
python -m qec_sim.gui
```

## 실행 파일 빌드

- Linux: `./scripts/build_gui_linux.sh` → `dist/QEC_Quantum_Simulator`
- Windows: `scripts\build_gui_windows.bat` → `dist\QEC_Quantum_Simulator.exe`

## 문서

- 사용 설명서: `docs/user_manual.md`, `docs/user_manual.docx`
- 개발 설명서(UML 포함): `docs/development_guide.md`
