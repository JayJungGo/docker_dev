# qec/src/qec_sim/metadata.py

from __future__ import annotations

import hashlib
import platform
from importlib.metadata import (
    PackageNotFoundError,
    version,
)
from typing import Mapping

from .domain import (
    CircuitStats,
    EvaluationResult,
    ExperimentConfig,
)


def _safe_version(
    package: str,
) -> str:

    try:
        return version(package)
    except PackageNotFoundError:
        return "unknown"


class PackageRuntimeInfoProvider:

    def get_info(
        self,
    ) -> Mapping[str, str]:

        return {
            "python_version":
                platform.python_version(),

            "stim_version":
                _safe_version("stim"),

            "pymatching_version":
                _safe_version("pymatching"),

            "numpy_version":
                _safe_version("numpy"),
        }


class ReproducibilityMetadataBuilder:

    def __init__(
        self,
        runtime_info_provider,
    ):
        self._runtime_info_provider = (
            runtime_info_provider
        )

    def build(
        self,
        config: ExperimentConfig,
        stats: CircuitStats,
        evaluation: EvaluationResult,
        circuit_text: str,
    ) -> Mapping[str, object]:

        circuit_hash = hashlib.sha256(
            circuit_text.encode("utf-8")
        ).hexdigest()

        metadata = {
            "task": config.task,

            "distance":
                config.distance,

            "rounds":
                config.effective_rounds,

            "depolarizing_p":
                config.depolarizing_p,

            "measurement_p":
                config.measurement_p,

            "shots":
                config.shots,

            "seed":
                config.seed,

            "num_qubits":
                stats.num_qubits,

            "num_detectors":
                stats.num_detectors,

            "num_observables":
                stats.num_observables,

            "logical_errors":
                evaluation.logical_errors,

            "logical_error_rate":
                evaluation.logical_error_rate,

            "detection_event_density":
                evaluation.detection_event_density,

            "circuit_sha256":
                circuit_hash,
        }

        metadata.update(
            self._runtime_info_provider.get_info()
        )

        return metadata
