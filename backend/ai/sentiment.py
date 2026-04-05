"""Sentiment Analysis Engine using VADER + enhanced scoring."""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models.schemas import SentimentResult, SentimentLabel
from typing import List, Dict, Any
import re


class SentimentAnalyzer:
    """Multi-signal sentiment analysis engine."""

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        # Enhanced emoji sentiment mappings
        self.emoji_sentiments = {
            "😀": 0.6, "😃": 0.6, "😄": 0.7, "😁": 0.5, "😊": 0.6,
            "🥰": 0.8, "😍": 0.8, "❤️": 0.7, "🔥": 0.4, "👍": 0.5,
            "😢": -0.6, "😭": -0.7, "😡": -0.8, "🤬": -0.9, "👎": -0.5,
            "💀": -0.3, "🤮": -0.7, "😤": -0.6, "😠": -0.7, "🖕": -0.9,
            "😐": 0.0, "🤔": 0.0, "😶": 0.0, "🤷": 0.0,
        }

    def _extract_emojis(self, text: str) -> List[str]:
        """Extract emojis from text."""
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0\U0000FE00-\U0000FE0F"
            "\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.findall(text)

    def _emoji_sentiment_boost(self, text: str) -> float:
        """Calculate emoji-based sentiment modifier."""
        emojis = self._extract_emojis(text)
        if not emojis:
            return 0.0
        scores = [self.emoji_sentiments.get(e, 0.0) for e in emojis]
        return sum(scores) / len(scores) if scores else 0.0

    def _classify_label(self, compound: float) -> SentimentLabel:
        """Classify compound score into sentiment label."""
        if compound >= 0.05:
            return SentimentLabel.POSITIVE
        elif compound <= -0.05:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.NEUTRAL

    def analyze(self, text: str, post_id: str = "") -> SentimentResult:
        """Perform sentiment analysis on text."""
        if not text or not text.strip():
            return SentimentResult(
                post_id=post_id,
                label=SentimentLabel.NEUTRAL,
                score=0.0, compound=0.0,
                positive=0.0, negative=0.0, neutral=1.0,
                confidence=0.5,
            )

        # VADER analysis
        scores = self.analyzer.polarity_scores(text)

        # Emoji boost
        emoji_boost = self._emoji_sentiment_boost(text)
        adjusted_compound = max(-1.0, min(1.0, scores["compound"] + emoji_boost * 0.2))

        label = self._classify_label(adjusted_compound)

        # Confidence based on score strength
        confidence = min(1.0, abs(adjusted_compound) * 1.2 + 0.3)

        # Check for mixed sentiment
        if scores["pos"] > 0.25 and scores["neg"] > 0.25:
            label = SentimentLabel.MIXED
            confidence *= 0.8

        return SentimentResult(
            post_id=post_id,
            label=label,
            score=adjusted_compound,
            compound=adjusted_compound,
            positive=round(scores["pos"], 4),
            negative=round(scores["neg"], 4),
            neutral=round(scores["neu"], 4),
            confidence=round(confidence, 4),
        )

    def analyze_batch(self, texts: List[Dict[str, str]]) -> List[SentimentResult]:
        """Analyze multiple texts."""
        return [self.analyze(item.get("text", ""), item.get("id", "")) for item in texts]

    def get_aggregate_sentiment(self, results: List[SentimentResult]) -> Dict[str, Any]:
        """Get aggregate sentiment stats."""
        if not results:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0, "mixed": 0, "avg_compound": 0.0}

        counts = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}
        total_compound = 0.0

        for r in results:
            counts[r.label.value] += 1
            total_compound += r.compound

        return {
            "total": len(results),
            **counts,
            "avg_compound": round(total_compound / len(results), 4),
        }


# Singleton instance
sentiment_analyzer = SentimentAnalyzer()
