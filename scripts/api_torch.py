from fastapi import FastAPI
import os
import json
import time
import torch

app = FastAPI()

@app.get("/health")
def health():
    return {
        "service": "pytorch",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
    }

@app.get("/write-artifact")
def write_artifact():
    os.makedirs("/workspace/shared", exist_ok=True)
    out = {
        "service": "pytorch",
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "timestamp": int(time.time()),
    }
    path = "/workspace/shared/pytorch_artifact.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return {"ok": True, "path": path}

@app.get("/matmul")
def matmul():
    x = torch.randn(1024, 1024, device="cuda" if torch.cuda.is_available() else "cpu")
    y = x @ x
    return {
        "service": "pytorch",
        "device": str(y.device),
        "shape": list(y.shape),
        "sum": float(y.sum().item()),
    }
