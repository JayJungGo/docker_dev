from fastapi import FastAPI
import os
import json
import time
import pennylane as qml

app = FastAPI()
dev = qml.device("default.qubit", wires=1)

@qml.qnode(dev)
def circuit(x: float):
    qml.RX(x, wires=0)
    return qml.expval(qml.PauliZ(0))

@app.get("/health")
def health():
    return {
        "service": "pennylane",
        "qml_version": qml.version(),
    }

@app.get("/write-artifact")
def write_artifact():
    os.makedirs("/workspace/shared", exist_ok=True)
    out = {
        "service": "pennylane",
        "qml_version": qml.version(),
        "timestamp": int(time.time()),
    }
    path = "/workspace/shared/pennylane_artifact.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return {"ok": True, "path": path}

@app.get("/eval")
def eval_qnode(x: float = 0.3):
    return {
        "service": "pennylane",
        "x": x,
        "value": float(circuit(x)),
    }
