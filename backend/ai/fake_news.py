"""Fake News Detection using multi-signal heuristic analysis."""
import re
import math
from typing import List, Dict, Any
from models.schemas import FakeNewsResult


class FakeNewsDetector:
    """Multi-signal fake news detection engine.

    Uses linguistic analysis, source credibility, and behavioral
    patterns to score content reliability.
    """

    def __init__(self):
        # Sensationalism indicators
        self.clickbait_patterns = [
            r"\byou won't believe\b", r"\bshocking\b", r"\bbreaking\b",
            r"\burgent\b", r"\bexclusive\b", r"\b100%\b",
            r"\bsecret\b", r"\bthey don't want you to know\b",
            r"\bwake up\b", r"\bsheeple\b", r"\btruth bomb\b",
            r"\bmainstream media\b", r"\bcoverup\b", r"\bconspiracy\b",
            r"\bhoax\b", r"\bplandemic\b", r"\bmanipulation\b",
        ]
        # Emotional manipulation words
        self.emotional_triggers = [
            "outrage", "fury", "disgusting", "horrifying", "terrifying",
            "unbelievable", "insane", "crazy", "evil", "destroy",
            "catastrophe", "nightmare", "apocalypse", "bombshell",
        ]
        # Credibility negative signals
        self.low_credibility_signals = [
            "anonymous sources", "some people say", "rumor has it",
            "reportedly", "allegedly", "unconfirmed", "sources say",
            "insider reveals", "leaked documents show",
        ]
        # Known unreliable URL patterns
        self.suspicious_domains = [
            "blogspot", "wordpress.com", "medium.com", "substack",
        ]

    def _check_caps_ratio(self, text: str) -> float:
        """Check ratio of uppercase characters (ALL CAPS = suspicious)."""
        if not text:
            return 0.0
        alpha_chars = [c for c in text if c.isalpha()]
        if not alpha_chars:
            return 0.0
        upper_count = sum(1 for c in alpha_chars if c.isupper())
        return upper_count / len(alpha_chars)

    def _check_exclamation_density(self, text: str) -> float:
        """Check density of exclamation marks."""
        if not text:
            return 0.0
        exc_count = text.count("!") + text.count("‼") + text.count("⚠")
        return min(1.0, exc_count / max(len(text.split()), 1))

    def _check_clickbait(self, text: str) -> Dict[str, Any]:
        """Check for clickbait patterns."""
        text_lower = text.lower()
        found = []
        for pattern in self.clickbait_patterns:
            if re.search(pattern, text_lower):
                found.append(pattern.replace(r"\b", "").strip())
        return {"score": min(1.0, len(found) * 0.2), "matches": found}

    def _check_emotional_manipulation(self, text: str) -> Dict[str, Any]:
        """Check for emotional manipulation words."""
        text_lower = text.lower()
        found = [w for w in self.emotional_triggers if w in text_lower]
        return {"score": min(1.0, len(found) * 0.15), "matches": found}

    def _check_source_credibility(self, text: str, urls: List[str] = None) -> float:
        """Score source credibility (0=unreliable, 1=credible)."""
        text_lower = text.lower()
        cred_loss = 0.0
        for signal in self.low_credibility_signals:
            if signal in text_lower:
                cred_loss += 0.1
        if urls:
            for url in urls:
                for domain in self.suspicious_domains:
                    if domain in url.lower():
                        cred_loss += 0.05
        return max(0.0, 1.0 - cred_loss)

    def _check_factual_claims(self, text: str) -> float:
        """Check for unsubstantiated factual claims."""
        claim_patterns = [
            r"\b\d+%\s+of\b", r"\bstudies show\b", r"\bscientists say\b",
            r"\bexperts agree\b", r"\bproven\b", r"\bfact:\b",
        ]
        text_lower = text.lower()
        matches = sum(1 for p in claim_patterns if re.search(p, text_lower))
        return min(1.0, matches * 0.2)

    def detect(self, text: str, post_id: str = "", urls: List[str] = None) -> FakeNewsResult:
        """Analyze text for fake news indicators."""
        if not text or not text.strip():
            return FakeNewsResult(
                post_id=post_id, is_fake=False, confidence=0.0,
                credibility_score=1.0, reasoning="No content to analyze"
            )

        signals = []
        total_score = 0.0

        # 1. Caps ratio
        caps = self._check_caps_ratio(text)
        if caps > 0.3:
            signals.append({"signal": "excessive_caps", "score": caps, "detail": f"{caps:.0%} uppercase"})
            total_score += caps * 0.15

        # 2. Exclamation density
        exc = self._check_exclamation_density(text)
        if exc > 0.1:
            signals.append({"signal": "exclamation_density", "score": exc, "detail": "High punctuation density"})
            total_score += exc * 0.1

        # 3. Clickbait
        clickbait = self._check_clickbait(text)
        if clickbait["score"] > 0:
            signals.append({"signal": "clickbait_patterns", "score": clickbait["score"], "detail": clickbait["matches"]})
            total_score += clickbait["score"] * 0.25

        # 4. Emotional manipulation
        emotional = self._check_emotional_manipulation(text)
        if emotional["score"] > 0:
            signals.append({"signal": "emotional_manipulation", "score": emotional["score"], "detail": emotional["matches"]})
            total_score += emotional["score"] * 0.2

        # 5. Source credibility
        credibility = self._check_source_credibility(text, urls)
        if credibility < 0.8:
            signals.append({"signal": "low_credibility", "score": 1 - credibility, "detail": f"Credibility: {credibility:.2f}"})
            total_score += (1 - credibility) * 0.15

        # 6. Factual claims
        claims = self._check_factual_claims(text)
        if claims > 0:
            signals.append({"signal": "unsubstantiated_claims", "score": claims, "detail": "Contains factual claims without sources"})
            total_score += claims * 0.15

        # Normalize total score
        fake_score = min(1.0, total_score)
        is_fake = fake_score >= 0.4
        confidence = min(1.0, 0.3 + fake_score * 0.7)

        reasoning_parts = [s["signal"] for s in signals]
        reasoning = f"Flagged signals: {', '.join(reasoning_parts)}" if signals else "No fake news indicators detected"

        return FakeNewsResult(
            post_id=post_id,
            is_fake=is_fake,
            confidence=round(confidence, 4),
            signals=signals,
            credibility_score=round(credibility, 4),
            reasoning=reasoning,
        )


# Singleton
fake_news_detector = FakeNewsDetector()
