import cuquantum, cupy as cp
from cuquantum.bindings import custatevec as sv

print("cuQuantum:", cuquantum.__version__)
h = sv.create()
n = 3
state = cp.zeros(2**n, dtype=cp.complex64); state[0] = 1.0
sv.apply_pauli_rotation(h, n, state.data.ptr, cp.float32(0.1), 0, sv.PAULI_Z)
sv.destroy(h)
print("custatevec OK")

