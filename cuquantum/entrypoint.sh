#!/usr/bin/env bash
set -euo pipefail

echo "[cuquantum] self-test start"
if python3 /opt/check_cuq.py; then
  echo "[cuquantum] self-test OK"
else
  echo "[WARN] cuquantum self-test failed, continuing to Jupyter for debugging..."
fi

exec jupyter lab --ip=0.0.0.0 --no-browser --NotebookApp.token='' --allow-root

