# /workspace/scripts/check_cuq_expect.py
import numpy as np
import cupy as cp
from cuquantum.bindings import custatevec as sv

print("[cuquantum] expectation test start")

# 1) 상태 준비: |000> (complex64)
n = 3
state = cp.zeros(2**n, dtype=cp.complex64)
state[0] = 1.0 + 0.0j

# 2) cuStateVec 핸들 및 dtype 코드
handle = sv.create()

# CUDA_C_32F / CUDA_C_64F 코드값 (py 바인딩에서 enum 노출이 없어 정수 직접 사용)
# 4 -> complex64, 5 -> complex128
sv_dtype = 4 if state.dtype == cp.complex64 else 5

# 3) 기대값을 저장할 host 버퍼 준비 (float64)
exp = np.zeros(1, dtype=np.float64)

# 4) 연산자/비트 설정
#   - pauli_ops: 파울리 문자열들의 "배열(목록)들" (여기선 문자열 1개만 가진 배열 1개)
#   - basis_bits: 각 문자열에서 작용할 비트 인덱스 배열(들)
pauli_ops = [[sv.Pauli.Z]]   # Z on qubit 0
basis_bits = [[0]]
n_pauli_op_arrays = 1
n_basis_bits = [1]

# 5) 호출 (인자 9개 정확히)
sv.compute_expectations_on_pauli_basis(
    handle,
    int(state.data.ptr),        # device pointer to state vector
    sv_dtype,                   # 4 for complex64
    n,                          # number of index bits
    int(exp.ctypes.data),       # host pointer to output buffer (float64)
    pauli_ops,                  # nested Pauli lists
    n_pauli_op_arrays,          # number of Pauli arrays
    basis_bits,                 # nested basis bits
    n_basis_bits,               # lengths for each basis_bits entry
)

print("Expectation <Z_0>:", float(exp[0]))
# 이론값: |000>에서 Z_0의 기대값은 +1
print("PASS" if abs(exp[0] - 1.0) < 1e-6 else "FAIL")

sv.destroy(handle)

