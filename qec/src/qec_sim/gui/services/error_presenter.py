"""
사용자 친화적 오류 메시지 생성기.

Nielsen Heuristic #9: Help users recognize, diagnose, and recover from errors.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserFacingError:
    """GUI에 표시할 오류 제목/본문/복구 안내."""

    title: str
    message: str
    recovery: str


class ErrorPresenter:
    """예외를 복구 가능한 안내 문구로 변환한다."""

    def present(self, exc: BaseException) -> UserFacingError:
        text = str(exc).strip() or exc.__class__.__name__
        lower = text.lower()

        if "distance" in lower:
            return UserFacingError(
                title="코드 거리 입력 오류",
                message=text,
                recovery=(
                    "해결 방법: distance를 2 이상의 홀수/정수로 다시 입력하세요. "
                    "예: 3, 5, 7. 큰 값은 실행 시간이 급격히 늘어납니다."
                ),
            )

        if "rounds" in lower:
            return UserFacingError(
                title="측정 라운드 입력 오류",
                message=text,
                recovery=(
                    "해결 방법: rounds를 비워 두거나(distance와 동일), "
                    "1 이상의 정수로 입력하세요."
                ),
            )

        if "depolarizing" in lower or "measurement_p" in lower:
            return UserFacingError(
                title="잡음률 입력 오류",
                message=text,
                recovery=(
                    "해결 방법: depolarizing_p와 measurement_p를 "
                    "0.0 이상 1.0 이하의 소수로 입력하세요. 예: 0.001"
                ),
            )

        if "shots" in lower:
            return UserFacingError(
                title="샷 수 입력 오류",
                message=text,
                recovery=(
                    "해결 방법: shots를 1 이상의 정수로 입력하세요. "
                    "처음에는 1000처럼 작은 값으로 시험 실행을 권장합니다."
                ),
            )

        if "output" in lower or "directory" in lower or "dir" in lower:
            return UserFacingError(
                title="저장 경로 오류",
                message=text,
                recovery=(
                    "해결 방법: '찾아보기' 버튼으로 쓰기 권한이 있는 "
                    "폴더를 선택하세요. 존재하지 않으면 자동 생성됩니다."
                ),
            )

        if "permission" in lower or "errno 13" in lower:
            return UserFacingError(
                title="파일 권한 오류",
                message=text,
                recovery=(
                    "해결 방법: 저장 폴더의 쓰기 권한을 확인하거나 "
                    "홈 디렉터리 아래 다른 경로를 선택하세요."
                ),
            )

        if "unknown circuit" in lower or "task" in lower:
            return UserFacingError(
                title="회로 종류(task) 오류",
                message=text,
                recovery=(
                    "해결 방법: 드롭다운에서 지원되는 task를 선택하세요. "
                    "직접 입력 시 Stim 문서의 generated circuit 이름을 사용하세요."
                ),
            )

        if "numpy" in lower and ("multiarray" in lower or "core" in lower):
            return UserFacingError(
                title="NumPy 패키징/환경 오류",
                message=text,
                recovery=(
                    "해결 방법:\n"
                    "1) 실행 파일(QEC_Quantum_Simulator)을 쓰는 경우: "
                    "최신 빌드로 다시 패키징하세요 "
                    "(./scripts/build_gui_linux.sh).\n"
                    "2) 소스로 실행하는 경우: "
                    "pip3 install -U --user 'numpy>=1.26' 후 "
                    "PYTHONPATH=qec/src python3 -m qec_sim.gui 로 실행하세요.\n"
                    "3) 여러 NumPy가 섞여 있으면 "
                    "python3 -c \"import numpy; print(numpy.__file__)\" "
                    "로 경로를 확인하세요."
                ),
            )

        return UserFacingError(
            title="실행 중 오류가 발생했습니다",
            message=text,
            recovery=(
                "해결 방법: 입력값을 기본값으로 초기화한 뒤 "
                "distance=3, shots=1000으로 다시 실행해 보세요. "
                "문제가 반복되면 metadata/로그와 함께 개발자에게 문의하세요."
            ),
        )
