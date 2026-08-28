# qec/src/qec_sim/evaluation.py

from __future__ import annotations
import numpy as np
from .domain import (
    EvaluationResult,
    SampleBatch,
)

class LogicalErrorEvaluator:

    def evaluate(
        self,
        predictions: np.ndarray,
        batch: SampleBatch,
    ) -> EvaluationResult:

        predictions = np.asarray(predictions)
        observables = np.asarray(batch.observables)

        if predictions.ndim == 1:
            predictions = predictions[:, None]

        if observables.ndim == 1:
            observables = observables[:, None]

        if predictions.shape != observables.shape:
            raise ValueError(
                "Prediction shape does not match "
                f"observable shape: "
                f"{predictions.shape} != "
                f"{observables.shape}"
            )

        failures = np.any(
            predictions != observables,
            axis=1,
        )

        logical_errors = int(
            failures.sum()
        )

        logical_error_rate = float(
            failures.mean()
        )

        detection_event_density = float(
            batch.detections.mean()
        )

        return EvaluationResult(
            logical_errors=logical_errors,
            logical_error_rate=logical_error_rate,
            detection_event_density=
                detection_event_density,
        )
