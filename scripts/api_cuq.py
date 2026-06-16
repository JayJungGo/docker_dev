from fastapi import FastAPI
import os
import json
import time
import cupy as cp

app = FastAPI()

@app.get("/health")
def health():
    return {
        "service": "cuquantum",
        "cupy_version": cp.__version__,
        "cuda_device_count": cp.cuda.runtime.getDeviceCount(),
    }

@app.get("/write-artifact")
def write_artifact():
    os.makedirs("/workspace/shared", exist_ok=True)
    out = {
        "service": "cuquantum",
        "cupy_version": cp.__version__,
        "cuda_device_count": cp.cuda.runtime.getDeviceCount(),
        "timestamp": int(time.time()),
    }
    path = "/workspace/shared/cuquantum_artifact.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return {"ok": True, "path": path}

@app.get("/sum")
def gpu_sum():
    x = cp.ones((2048, 2048))
    return {
        "service": "cuquantum",
        "sum": float(x.sum().get()),
    }
