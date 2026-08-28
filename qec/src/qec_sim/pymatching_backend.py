# qec/src/qec_sim/pymatching_backend.py
"""
PyMatching 기반 MWPM decoder backend.
Stim에서 생성된 Detector Error Model(DEM)과 shot별 detection event를 입력으로 받아 Minimum-Weight Perfect Matching decoding을 수행한다.
이 모듈은 QEC simulation framework에서 PyMatching 라이브러리에 직접 의존하는 decoding 기능을 격리한다.
----입력----
1. Detector Error Model
 - Stim circuit으로부터 생성된 오류 모델
 - detector 사이의 오류 관계와 logical observable 정보를 포함
2. Detection events
 - StimSyndromeSampler가 생성한 shot별 detector 활성화 정보
----출력----
- 각 shot에 대한 logical observable prediction
--------
전체 흐름
---------
Detector Error Model + Detection Events
        ↓
PyMatching Matching Graph
        ↓
MWPM Decoding
        ↓
Logical Observable Predictions
---------
이 모듈에서는 circuit 생성, syndrome sampling, logical error rate 계산 및 결과 저장을 수행하지 않는다.
"""
from __future__ import annotations
from typing import Any
import numpy as np
import pymatching

class PyMatchingDecoder:
"""
----역할----
1. Stim Detector Error Model을 PyMatching matching graph로 변환
2. 여러 shot의 surface-code detection event를 batch 단위로 decoding함
3. 각 shot에 대한 logical observable prediction 반환
이 prediction은 이후 LogicalErrorEvaluator에서 Stim이 생성한 실제 observable과 비교되어 Logical Error Rate 계산에 사용된다. 또한, 이 클래스는 decoding에만 책임을 가진다.
다음 작업은 다른 객체가 담당한다.
 - Circuit 생성: StimCircuitBuilder
 - Syndrome 생성: StimSyndromeSampler
 - Decoder 평가: LogicalErrorEvaluator
 - 결과 저장: ResultWriter
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
          반환값은 이후 실제 observables와 비교하여 logical error 여부를 계산한다.
        """
        matching = (  
            pymatching.Matching
            .from_detector_error_model(
                detector_error_model
            )
        )
        # Detector Error Model을 PyMatching이 사용할 수 있는 weighted matching graph로 변환한다.
        # 이 graph에는 detector 간 오류 관계와 각 오류의 weight 정보가 반영된다.
        predictions = matching.decode_batch(
            detections
        )
        # 여러 shot의 detection event를 한 번에 decoding한다.
        # detections:
        #   decoder 입력
        # predictions:
        #   decoder가 추정한 logical observable 결과
        return np.asarray(predictions) 
        # 상위 framework에서는 특정 backend의 반환 타입에 의존하지 않도록 공통 NumPy 배열 형태로 변환한다.
