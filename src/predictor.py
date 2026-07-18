from __future__ import annotations

from typing import Any

from .model import load_pipeline
from .threat_analyzer import ThreatAnalyzer


class Predictor:
    """
    Enterprise prediction engine.

    Responsibilities:
    1. Load trained pipeline
    2. Predict class
    3. Predict confidence
    4. Run threat analyzer
    5. Return complete report
    """

    def __init__(self):
        self.pipeline = load_pipeline()
        self.analyzer = ThreatAnalyzer()

    def predict(self, text: str) -> dict[str, Any]:

        if not text or not text.strip():
            raise ValueError("Input message cannot be empty.")

        # Pipeline prediction
        prediction = int(self.pipeline.predict([text])[0])

        # Prediction probabilities
        probabilities = self.pipeline.predict_proba([text])[0]

        confidence = round(float(max(probabilities) * 100), 2)

        # Threat analysis
        report = self.analyzer.analyze(
            text=text,
            prediction=prediction,
            confidence=confidence,
        )

        return report