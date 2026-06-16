#!/usr/bin/env python3
import os
import cupy as cp
import cuquantum
from cuquantum.bindings import custatevec as sv

print("[cuquantum] self-test start")
print("cuQuantum:", cuquantum.__version__)
print("CUPY_NVRTC_OPTIONS:", os.environ.get("CUPY_NVRTC_OPTIONS"))
print("CUPY_COMPILE_WITH_PTX:", os.environ.get("CUPY_COMPILE_WITH_PTX"))
print("CUPY_CACHE_DIR:", os.environ.get("CUPY_CACHE_DIR", "~/.cupy/kernel_cache"))

# ---- Pauli Z 안전 획득 ----
Pauli = getattr(sv, "Pauli", None)
if Pauli is None:
    raise RuntimeError("sv.Pauli enum not found")
try:
    Z = getattr(Pauli, "Z")
except Exception:
    # 일부 버전은 Enum("Z") 생성 지원
    Z = Pauli("Z")

# ---- 상태 준비 ----
h = sv.create()
try:
    n = 3
    state = cp.zeros(2**n, dtype=cp.complex64)
    state[0] = 1.0
    theta = 0.1
    target = 0

    fn = sv.apply_pauli_rotation
    attempts = []
    ok = False
    variant_used = None

    def try_call(tag, *args):
        try:
            fn(*args)
            return True, None
        except TypeError as e:
            return False, f"{tag}:TypeError:{e}"
        except Exception as e:
            return False, f"{tag}:{type(e).__name__}:{e}"

    # Variant A: 간단형 (6 인자) — 일부 릴리즈
    # (handle, nIndexBits, sv, theta, target, pauli)
    done, msg = try_call("A:simple-6", h, n, state.data.ptr, cp.float32(theta), target, Z)
    if done:
        ok, variant_used = True, "A:simple-6"
    else:
        attempts.append(msg)

    # Variant B: 확장형 (목표/제어/상태 등 리스트로 전달). dtype/computeType 없이.
    # 흔한 패턴: (h, n, sv, theta, paulis[], targets[], controls[], controlBitValues[], nPaulis, adjoint)
    if not ok:
        done, msg = try_call("B:extended-10",
                             h, n, state.data.ptr, theta,
                             [Z], [target], [], [], 1, 0)
        if done:
            ok, variant_used = True, "B:extended-10"
        else:
            attempts.append(msg)

    # Variant C: 확장형에서 마지막 플래그/카운트 순서가 바뀐 경우 시도
    if not ok:
        done, msg = try_call("C:extended-alt",
                             h, n, state.data.ptr, theta,
                             [Z], [target], [], [], 0, 1)
        if done:
            ok, variant_used = True, "C:extended-alt"
        else:
            attempts.append(msg)

    # Variant D: 확장형에서 adjoint 생략/기본값 케이스 (일부 바인딩에서 허용될 수 있음)
    if not ok:
        try:
            done, msg = try_call("D:extended-9",
                                 h, n, state.data.ptr, theta,
                                 [Z], [target], [], [], 1)
            if done:
                ok, variant_used = True, "D:extended-9"
            else:
                attempts.append(msg)
        except Exception as e:
            attempts.append(f"D:{type(e).__name__}:{e}")

    if not ok:
        raise TypeError("apply_pauli_rotation: no matching signature. Tried -> "
                        + " | ".join([m for m in attempts if m]))

    # 노름 체크
    norm = float(cp.linalg.norm(state).item())
    if abs(norm - 1.0) > 1e-3:
        raise RuntimeError(f"State norm deviates: {norm}")

    print(f"[cuquantum] custatevec rotation OK (variant={variant_used})")

    # (선택) 기대값 평가 — 시그니처 차이 많아 best-effort
    try:
        exp = sv.compute_expectations_on_pauli_basis(h, n, state.data.ptr, [target], [Z])
        val = float(exp[0]) if hasattr(exp, "__len__") else float(exp)
        print("⟨Z⟩ on qubit 0 ≈", val)
    except Exception:
        print("[note] compute_expectations_on_pauli_basis skipped (signature mismatch)")

finally:
    sv.destroy(h)

