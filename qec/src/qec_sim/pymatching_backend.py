# qec/src/qec_sim/pymatching_backend.py
"""
PyMatching 기반 MWPM decoder backend.
Stim에서 생성된 Detector Error Model(DEM)과 shot별 detection event를 입력으로 받아
Minimum-Weight Perfect Matching decoding을 수행한다.
"""
from __future__ import annotations
from typing import Any
import numpy as np
import pymatching


class PyMatchingDecoder:
    """
    Stim Detector Error Model을 PyMatching matching graph로 변환하고,
    여러 shot의 detection event를 batch 단위로 decoding한다.
    """

    def decode(
        self,
        detector_error_model: Any,
        detections: np.ndarray,
    ) -> np.ndarray:
        """
        Detection event batch를 MWPM 방식으로 decoding한다.
        Parameters
        ----------
        detector_error_model:
          Stim circuit으로부터 만들어진 Detector Error Model.
        detections:
          StimSyndromeSampler가 생성한 detection event 배열.
          각 행은 하나의 shot, 각 열은 하나의 detector에 대응한다.
        Returns
        -------
        np.ndarray
          각 shot에 대해 decoder가 추정한 logical observable prediction.
        """
        matching = (
            pymatching.Matching
            .from_detector_error_model(
                detector_error_model
            )
        )
        predictions = matching.decode_batch(
            detections
        )
        return np.asarray(predictions)
