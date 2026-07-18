# Threat Analysis Engine
# Analyzes classified messages for specific threat indicators.

"""Rule-based threat analysis engine for phishing and spam explanations."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


class ThreatAnalyzer:
    """Explain why a message looks safe, spammy, or phishing-like."""

    LABEL_NAMES = {
        0: "Safe",
        1: "Phishing",
        2: "Spam",
    }

    THREAT_LEVELS = ("LOW", "MEDIUM", "HIGH")

    def __init__(self) -> None:
        # URL / email patterns
        self.url_pattern = re.compile(
            r"""(?ix)
            \b(
                (?:https?://|www\.)[^\s<>()]+
                |
                (?:[a-z0-9-]+\.)+(?:com|net|org|edu|gov|co|io|me|xyz|top|click|icu|ru|tk|zip|support|site|online|biz|shop|info|app)
                (?:/[^\s<>()]*)?
            )
            """
        )
        self.email_pattern = re.compile(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            re.IGNORECASE,
        )

        # Threat keyword lists
        self.urgency_keywords = {
            "urgent",
            "immediately",
            "asap",
            "act now",
            "limited time",
            "expires today",
            "final warning",
            "within 24 hours",
            "verify now",
            "open now",
            "response required",
            "immediate action",
        }

        self.credential_keywords = {
            "password",
            "otp",
            "pin",
            "login",
            "log in",
            "sign in",
            "verify account",
            "verify your account",
            "confirm identity",
            "update credentials",
            "security code",
            "passcode",
            "account verification",
        }

        self.financial_keywords = {
            "bank",
            "account",
            "credit card",
            "debit card",
            "transaction",
            "payment",
            "wallet",
            "refund",
            "invoice",
            "transfer",
            "loan",
            "chargeback",
            "billing",
            "money",
        }

        self.suspicious_shorteners = {
            "bit.ly",
            "tinyurl.com",
            "goo.gl",
            "t.co",
            "ow.ly",
            "is.gd",
            "buff.ly",
            "cutt.ly",
            "rebrand.ly",
        }

        self.suspicious_tlds = {
            "zip",
            "xyz",
            "top",
            "click",
            "icu",
            "ru",
            "tk",
            "support",
            "site",
            "online",
            "biz",
            "shop",
            "info",
            "app",
            "work",
        }

    def _normalize_text(self, text: Any) -> str:
        if text is None:
            return ""
        return str(text).strip()

    def _find_keyword_hits(self, text_lower: str, keywords: set[str]) -> list[str]:
        hits: list[str] = []
        for keyword in sorted(keywords, key=len, reverse=True):
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, text_lower, flags=re.IGNORECASE):
                hits.append(keyword)
        return hits

    def _extract_host(self, url: str) -> str:
        candidate = url.strip()
        if not re.match(r"(?i)^https?://", candidate):
            candidate = "http://" + candidate
        parsed = urlparse(candidate)
        host = parsed.netloc.lower().strip()
        if host.startswith("www."):
            host = host[4:]
        return host

    def _is_suspicious_domain(self, host: str) -> bool:
        if not host:
            return False

        if host in self.suspicious_shorteners:
            return True

        # Check TLD-like endings
        for tld in self.suspicious_tlds:
            if host == tld or host.endswith(f".{tld}"):
                return True

        return False

    def detect_urls(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text)
        matches = [match.group(0).strip(").,;:!?\"'") for match in self.url_pattern.finditer(message)]

        reasons: list[str] = []
        points = 0

        if matches:
            reasons.append("Suspicious URL detected")
            points += 25

            if len(matches) > 1:
                reasons.append("Multiple URLs detected")
                points += min((len(matches) - 1) * 5, 10)

            suspicious_hosts = []
            for url in matches:
                host = self._extract_host(url)
                if self._is_suspicious_domain(host):
                    suspicious_hosts.append(host)

            if suspicious_hosts:
                reasons.append("Suspicious domain pattern detected")
                points += 10

        return {
            "name": "url",
            "detected": bool(matches),
            "points": points,
            "matches": matches,
            "reasons": reasons,
        }

    def detect_emails(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text)
        matches = [match.group(0) for match in self.email_pattern.finditer(message)]

        reasons: list[str] = []
        points = 0

        if matches:
            reasons.append("Email address detected")
            points = 5

            if len(matches) > 1:
                reasons.append("Multiple email addresses detected")
                points += 3

        return {
            "name": "email",
            "detected": bool(matches),
            "points": points,
            "matches": matches,
            "reasons": reasons,
        }

    def detect_urgency(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text).lower()
        hits = self._find_keyword_hits(message, self.urgency_keywords)

        reasons: list[str] = []
        points = 0

        if hits:
            reasons.append("Urgent language detected")
            points = 15
            if len(hits) > 1:
                reasons.append("Repeated urgency cues detected")
                points += min((len(hits) - 1) * 2, 5)

        return {
            "name": "urgency",
            "detected": bool(hits),
            "points": points,
            "matches": hits,
            "reasons": reasons,
        }

    def detect_credentials(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text).lower()
        hits = self._find_keyword_hits(message, self.credential_keywords)

        reasons: list[str] = []
        points = 0

        if hits:
            reasons.append("Credential request detected")
            points = 25
            if len(hits) > 1:
                reasons.append("Multiple credential-related terms detected")
                points += min((len(hits) - 1) * 3, 10)

        return {
            "name": "credentials",
            "detected": bool(hits),
            "points": points,
            "matches": hits,
            "reasons": reasons,
        }

    def detect_financial_keywords(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text).lower()
        hits = self._find_keyword_hits(message, self.financial_keywords)

        reasons: list[str] = []
        points = 0

        if hits:
            reasons.append("Financial / banking keyword detected")
            points = 15
            if len(hits) > 1:
                reasons.append("Multiple financial keywords detected")
                points += min((len(hits) - 1) * 2, 5)

        return {
            "name": "financial",
            "detected": bool(hits),
            "points": points,
            "matches": hits,
            "reasons": reasons,
        }

    def detect_formatting(self, text: Any) -> dict[str, Any]:
        message = self._normalize_text(text)

        reasons: list[str] = []
        points = 0

        # Excessive punctuation
        exclamation_count = message.count("!")
        question_count = message.count("?")
        dollar_count = message.count("$")

        if exclamation_count >= 3:
            reasons.append("Excessive exclamation marks detected")
            points += 5

        if question_count >= 3:
            reasons.append("Excessive question marks detected")
            points += 5

        if dollar_count >= 3:
            reasons.append("Suspicious currency emphasis detected")
            points += 5

        if re.search(r"([!?$])\1{2,}", message):
            reasons.append("Repeated punctuation detected")
            points += 5

        # ALL CAPS words
        all_caps_words = re.findall(r"\b[A-Z]{4,}\b", message)
        if len(all_caps_words) >= 2:
            reasons.append("Excessive capitalization detected")
            points += 5

        # Uppercase ratio heuristic
        alpha_chars = [ch for ch in message if ch.isalpha()]
        if len(alpha_chars) >= 20:
            uppercase_ratio = sum(1 for ch in alpha_chars if ch.isupper()) / len(alpha_chars)
            if uppercase_ratio >= 0.6:
                reasons.append("High uppercase ratio detected")
                points += 5

        return {
            "name": "formatting",
            "detected": bool(reasons),
            "points": min(points, 15),
            "matches": all_caps_words,
            "reasons": reasons,
        }

    def calculate_risk(self, detector_results: list[dict[str, Any]]) -> int:
        score = sum(result["points"] for result in detector_results if result["detected"])

        active_detectors = sum(1 for result in detector_results if result["detected"])
        if active_detectors >= 3:
            score += 10

        return min(score, 100)

    def get_threat_level(self, risk_score: int) -> str:
        if risk_score >= 60:
            return "HIGH"
        if risk_score >= 30:
            return "MEDIUM"
        return "LOW"

    def generate_recommendations(
        self,
        detector_results: list[dict[str, Any]],
        threat_level: str,
    ) -> list[str]:
        recommendations: list[str] = []
        seen: set[str] = set()

        def add(item: str) -> None:
            if item not in seen:
                seen.add(item)
                recommendations.append(item)

        # Level-based advice
        if threat_level == "HIGH":
            add("Do not click links in the message.")
            add("Do not share passwords, OTPs, or PINs.")
            add("Verify the sender using official channels.")
            add("Report or delete the message if it looks suspicious.")
        elif threat_level == "MEDIUM":
            add("Double-check the sender before acting.")
            add("Inspect links carefully before opening them.")
            add("Verify requests through an official website or phone number.")
        else:
            add("No major phishing indicators detected.")
            add("Still review the sender and links before taking action.")

        # Indicator-specific advice
        indicator_names = {result["name"] for result in detector_results if result["detected"]}

        if "url" in indicator_names:
            add("Avoid clicking unknown or shortened URLs.")
        if "email" in indicator_names:
            add("Check the sender domain carefully.")
        if "credentials" in indicator_names:
            add("Never share passwords, OTPs, or security codes.")
        if "financial" in indicator_names:
            add("Verify financial or banking requests through an official source.")
        if "urgency" in indicator_names:
            add("Be cautious of pressure tactics and deadline-based messages.")
        if "formatting" in indicator_names:
            add("Treat excessive capitalization or punctuation as a warning sign.")

        return recommendations

    def build_report(
        self,
        text: Any,
        prediction: Any | None = None,
        confidence: float | int | None = None,
    ) -> dict[str, Any]:
        message = self._normalize_text(text)

        detector_results = [
            self.detect_urls(message),
            self.detect_emails(message),
            self.detect_urgency(message),
            self.detect_credentials(message),
            self.detect_financial_keywords(message),
            self.detect_formatting(message),
        ]

        risk_score = self.calculate_risk(detector_results)
        threat_level = self.get_threat_level(risk_score)
        recommendations = self.generate_recommendations(detector_results, threat_level)

        detected_indicators: list[str] = []
        for result in detector_results:
            if result["detected"]:
                detected_indicators.extend(result["reasons"])

        model_prediction = self._normalize_prediction(prediction)

        if detected_indicators:
            summary = (
                f"{len(detected_indicators)} indicator(s) found. "
                f"Overall threat level: {threat_level}."
            )
        else:
            summary = f"No strong phishing indicators detected. Overall threat level: {threat_level}."

        return {
            "input_text": message,
            "prediction": model_prediction,
            "confidence": confidence,
            "risk_score": risk_score,
            "threat_level": threat_level,
            "detected_indicators": detected_indicators,
            "detector_details": detector_results,
            "recommendations": recommendations,
            "summary": summary,
        }

    def analyze(
        self,
        text: Any,
        prediction: Any | None = None,
        confidence: float | int | None = None,
    ) -> dict[str, Any]:
        return self.build_report(text=text, prediction=prediction, confidence=confidence)

    def _normalize_prediction(self, prediction: Any | None) -> str:
        if prediction is None:
            return "Unknown"

        if isinstance(prediction, int):
            return self.LABEL_NAMES.get(prediction, str(prediction))

        prediction_str = str(prediction).strip()
        if prediction_str.isdigit():
            return self.LABEL_NAMES.get(int(prediction_str), prediction_str)

        return prediction_str