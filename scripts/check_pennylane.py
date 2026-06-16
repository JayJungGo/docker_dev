# scripts/check_pennylane.py
import pennylane as qml
from pennylane import numpy as pnp

print("[pennylane] self-test start")
print("PennyLane:", qml.__version__)
ok = False
for backend in ("lightning.gpu", "default.qubit"):
    try:
        dev = qml.device(backend, wires=2)
        @qml.qnode(dev, interface="autograd")
        def circuit(theta):
            qml.RX(theta[0], 0); qml.RY(theta[1], 1); qml.CNOT([0,1])
            return qml.expval(qml.PauliZ(1))
        theta = pnp.array([0.1, -0.2], requires_grad=True)
        val = circuit(theta)
        grad = qml.grad(circuit)(theta)
        print(f"[{backend}] val:", float(val), "grad:", grad)
        ok = True
        if backend == "lightning.gpu":
            break
    except Exception as e:
        print(f"[{backend}] WARN:", e)

if not ok:
    raise SystemExit("[pennylane] self-test failed")
print("[pennylane] OK")

