#!/usr/bin/env bash
# Linux용 GUI 실행 파일 빌드
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="${ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --distpath "${ROOT}/dist" \
  --workpath "${ROOT}/build/pyinstaller" \
  "${ROOT}/packaging/qec_sim_gui.spec"

echo "빌드 완료: ${ROOT}/dist/QEC_Quantum_Simulator"
