"""
GUI 폼 값을 ExperimentConfig로 변환하는 매퍼.

SOLID:
  - S: 폼 파싱/검증만 담당하고 실험 실행은 하지 않는다.
  - O: 새 필드가 생기면 이 클래스와 폼 메타데이터만 확장하면 된다.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ...domain import ExperimentConfig


@dataclass(frozen=True)
class FieldSpec:
    """단일 입력 필드의 표시/검증 메타데이터."""

    key: str
    label: str
    tooltip: str
    widget: str  # combo | int | float | path | optional_int
    default: object
    choices: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None


# ExperimentConfig 필드와 1:1로 대응하는 GUI 입력 명세
FIELD_SPECS: tuple[FieldSpec, ...] = (
    FieldSpec(
        key="task",
        label="회로 종류 (task)",
        tooltip=(
            "Stim이 생성할 surface-code 회로 종류입니다. "
            "예: rotated_memory_x는 logical X memory 실험입니다."
        ),
        widget="combo",
        default="surface_code:rotated_memory_x",
        choices=(
            "surface_code:rotated_memory_x",
            "surface_code:rotated_memory_z",
            "surface_code:unrotated_memory_x",
            "surface_code:unrotated_memory_z",
        ),
    ),
    FieldSpec(
        key="distance",
        label="코드 거리 (distance)",
        tooltip=(
            "Surface code의 code distance입니다. "
            "값이 커질수록 오류 정정 능력과 회로 규모가 함께 증가합니다. "
            "2 이상의 정수만 허용됩니다."
        ),
        widget="int",
        default=3,
        minimum=2,
        maximum=21,
    ),
    FieldSpec(
        key="rounds",
        label="측정 라운드 (rounds)",
        tooltip=(
            "Stabilizer measurement 반복 횟수입니다. "
            "비워 두면 distance와 동일한 값을 사용합니다. "
            "1 이상의 정수여야 합니다."
        ),
        widget="optional_int",
        default=None,
        minimum=1,
        maximum=100,
    ),
    FieldSpec(
        key="depolarizing_p",
        label="탈분극 잡음률 (depolarizing_p)",
        tooltip=(
            "Clifford gate 이후 적용되는 depolarizing noise 확률입니다. "
            "0.0 ~ 1.0 범위의 실수여야 합니다."
        ),
        widget="float",
        default=0.001,
        minimum=0.0,
        maximum=1.0,
    ),
    FieldSpec(
        key="measurement_p",
        label="측정 잡음률 (measurement_p)",
        tooltip=(
            "Stabilizer 측정 시 bit-flip이 발생할 확률입니다. "
            "0.0 ~ 1.0 범위의 실수여야 합니다."
        ),
        widget="float",
        default=0.001,
        minimum=0.0,
        maximum=1.0,
    ),
    FieldSpec(
        key="shots",
        label="샷 수 (shots)",
        tooltip=(
            "Monte Carlo syndrome sampling 반복 횟수입니다. "
            "생성되는 detection sample 개수와 같습니다. 1 이상이어야 합니다."
        ),
        widget="int",
        default=10_000,
        minimum=1,
        maximum=10_000_000,
    ),
    FieldSpec(
        key="seed",
        label="난수 시드 (seed)",
        tooltip=(
            "샘플링 재현성을 위한 random seed입니다. "
            "동일 seed와 동일 조건이면 동일한 데이터셋이 생성됩니다."
        ),
        widget="int",
        default=20260819,
        minimum=0,
        maximum=2_147_483_647,
    ),
    FieldSpec(
        key="output_dir",
        label="결과 저장 디렉터리 (output_dir)",
        tooltip=(
            "실험 결과 데이터셋(npy, stim, metadata 등)이 저장될 기본 폴더입니다. "
            "파일 탐색기 버튼으로 경로를 지정하세요."
        ),
        widget="path",
        default=str(Path.home() / "qec_sim_output"),
    ),
)


class ConfigFormMapper:
    """폼 dict → ExperimentConfig 변환 및 사용자 친화 검증."""

    def to_config(self, values: Mapping[str, object]) -> ExperimentConfig:
        """
        GUI에서 수집한 값을 ExperimentConfig로 변환한다.

        Raises:
            ValueError: 형식이 잘못되었거나 domain 검증에 실패한 경우.
        """
        try:
            distance = self._require_int(values["distance"], "distance")
            rounds = self._optional_int(values.get("rounds"), "rounds")
            depolarizing_p = self._require_float(
                values["depolarizing_p"], "depolarizing_p"
            )
            measurement_p = self._require_float(
                values["measurement_p"], "measurement_p"
            )
            shots = self._require_int(values["shots"], "shots")
            seed = self._require_int(values["seed"], "seed")
            output_dir = Path(str(values["output_dir"]).strip())
            task = str(values["task"]).strip()
        except KeyError as exc:
            raise ValueError(
                f"필수 입력 필드가 누락되었습니다: {exc.args[0]}"
            ) from exc

        if not task:
            raise ValueError("task 값이 비어 있습니다.")

        if not str(values["output_dir"]).strip():
            raise ValueError("결과 저장 디렉터리를 지정해 주세요.")

        config = ExperimentConfig(
            task=task,
            distance=distance,
            rounds=rounds,
            depolarizing_p=depolarizing_p,
            measurement_p=measurement_p,
            shots=shots,
            seed=seed,
            output_dir=output_dir,
        )
        config.validate()
        return config

    @staticmethod
    def _require_int(raw: object, name: str) -> int:
        text = str(raw).strip()
        if text == "":
            raise ValueError(f"{name} 값이 비어 있습니다.")
        try:
            return int(text)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name}은(는) 정수여야 합니다. 입력값: {raw!r}"
            ) from exc

    @staticmethod
    def _optional_int(raw: object, name: str) -> int | None:
        if raw is None:
            return None
        text = str(raw).strip()
        if text == "" or text.lower() in {"none", "auto", "-"}:
            return None
        try:
            return int(text)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name}은(는) 비우거나 정수여야 합니다. 입력값: {raw!r}"
            ) from exc

    @staticmethod
    def _require_float(raw: object, name: str) -> float:
        text = str(raw).strip()
        if text == "":
            raise ValueError(f"{name} 값이 비어 있습니다.")
        try:
            return float(text)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name}은(는) 실수여야 합니다. 입력값: {raw!r}"
            ) from exc
