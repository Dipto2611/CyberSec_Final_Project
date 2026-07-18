"""
decision_engine.py

Enterprise Decision Engine

This module combines:
1. Machine Learning Prediction
2. Threat Analyzer Result

to produce a final enterprise security assessment.
"""


class DecisionEngine:

    def __init__(self):
        pass

    def evaluate(
        self,
        prediction,
        confidence,
        risk_score,
        threat_level
    ):

        result = {
            "final_assessment": "",
            "severity": "",
            "message": ""
        }

        # -------------------------------------------------
        # SAFE
        # -------------------------------------------------

        if prediction == "Safe":

            if threat_level == "LOW":

                result["final_assessment"] = "Appears Legitimate"
                result["severity"] = "LOW"

                result["message"] = (
                    "The AI model and Threat Intelligence engine "
                    "agree that this message appears legitimate."
                )

            else:

                result["final_assessment"] = "Review Carefully"
                result["severity"] = "MEDIUM"

                result["message"] = (
                    "The AI model predicts this message is safe, "
                    "but the rule engine detected suspicious indicators."
                )

        # -------------------------------------------------
        # SPAM
        # -------------------------------------------------

        elif prediction == "Spam":

            if threat_level in ["LOW", "MEDIUM"]:

                result["final_assessment"] = "Likely Spam"
                result["severity"] = threat_level

                result["message"] = (
                    "This message appears to be spam. "
                    "Avoid interacting unless you trust the sender."
                )

            else:

                result["final_assessment"] = "Suspicious Spam"
                result["severity"] = "HIGH"

                result["message"] = (
                    "Spam message with multiple suspicious indicators detected."
                )

        # -------------------------------------------------
        # PHISHING
        # -------------------------------------------------

        elif prediction == "Phishing":

            if threat_level == "LOW":

                result["final_assessment"] = "Possible False Positive"
                result["severity"] = "MEDIUM"

                result["message"] = (
                    "The AI model classified this message as phishing, "
                    "but only a few phishing indicators were detected. "
                    "Review the sender before taking action."
                )

            elif threat_level == "MEDIUM":

                result["final_assessment"] = "Suspicious Message"
                result["severity"] = "MEDIUM"

                result["message"] = (
                    "Some phishing indicators were detected. "
                    "Exercise caution before interacting."
                )

            elif threat_level == "HIGH":

                result["final_assessment"] = "High Confidence Threat"
                result["severity"] = "HIGH"

                result["message"] = (
                    "Both the AI model and Threat Intelligence engine "
                    "indicate this message is highly suspicious."
                )

            else:

                result["final_assessment"] = "Critical Threat"
                result["severity"] = "CRITICAL"

                result["message"] = (
                    "Critical phishing indicators detected. "
                    "Do not interact with this message."
                )

        else:

            result["final_assessment"] = "Unknown"

            result["severity"] = "UNKNOWN"

            result["message"] = (
                "Unable to determine a final assessment."
            )

        return result