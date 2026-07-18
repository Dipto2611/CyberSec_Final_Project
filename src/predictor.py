from __future__ import annotations

from typing import Any

from .model import load_pipeline
from .threat_analyzer import ThreatAnalyzer
from .decision_engine import DecisionEngine


class Predictor:
    """
    Enterprise Prediction Engine

    Responsibilities:
    1. Load trained ML pipeline
    2. Predict email/message class
    3. Calculate prediction confidence
    4. Calculate probabilities for all classes
    5. Run Threat Analyzer
    6. Run Enterprise Decision Engine
    7. Return complete enterprise report
    """

    def __init__(self):

        self.pipeline = load_pipeline()
        self.analyzer = ThreatAnalyzer()
        self.decision_engine = DecisionEngine()

    def predict(self, text: str) -> dict[str, Any]:

        if not text or not text.strip():
            raise ValueError("Input message cannot be empty.")

        # =====================================================
        # ML Prediction
        # =====================================================

        prediction = int(self.pipeline.predict([text])[0])

        # =====================================================
        # Prediction Confidence
        # =====================================================

        probabilities = self.pipeline.predict_proba([text])[0]

        confidence = round(
            float(max(probabilities) * 100),
            2,
        )

        # =====================================================
        # Class Probability Distribution
        # =====================================================

        class_probabilities = {
            "Safe": round(float(probabilities[0] * 100), 2),
            "Phishing": round(float(probabilities[1] * 100), 2),
            "Spam": round(float(probabilities[2] * 100), 2),
        }

        # =====================================================
        # Threat Analysis
        # =====================================================

        report = self.analyzer.analyze(
            text=text,
            prediction=prediction,
            confidence=confidence,
        )

        # =====================================================
        # Enterprise Decision Engine
        # =====================================================

        decision = self.decision_engine.evaluate(
            prediction=report["prediction"],
            confidence=report["confidence"],
            risk_score=report["risk_score"],
            threat_level=report["threat_level"],
        )

        # =====================================================
        # Merge Enterprise Decision
        # =====================================================

        report["final_assessment"] = decision["final_assessment"]
        report["severity"] = decision["severity"]
        report["assessment_message"] = decision["message"]

        # =====================================================
        # Attach Probability Distribution
        # =====================================================

        report["class_probabilities"] = class_probabilities

        # =====================================================
        # Return Complete Report
        # =====================================================

        return report