"""Bot Detection Engine using behavioral heuristic analysis."""
from typing import List, Dict, Any, Optional
from models.schemas import BotDetectionResult, UserProfile
from datetime import datetime, timedelta, timezone
import math
import re


class BotDetector:
    """Behavioral bot detection using multi-signal heuristics.

    Analyzes posting patterns, account metadata, content patterns,
    and network behavior to score bot probability.
    """

    def __init__(self):
        self.weights = {
            "posting_frequency": 0.15,
            "account_age": 0.12,
            "follower_ratio": 0.13,
            "content_repetition": 0.15,
            "username_pattern": 0.10,
            "bio_analysis": 0.08,
            "engagement_ratio": 0.12,
            "timing_pattern": 0.15,
        }

    def _score_posting_frequency(self, posts_count: int, account_age_days: int) -> Dict[str, Any]:
        """Score based on posts per day (extremely high = bot-like)."""
        if account_age_days <= 0:
            return {"score": 0.8, "detail": "Account age unknown"}
        ppd = posts_count / account_age_days
        if ppd > 50:
            score = 0.95
        elif ppd > 20:
            score = 0.7
        elif ppd > 10:
            score = 0.4
        else:
            score = max(0.0, ppd / 20)
        return {"score": round(score, 4), "detail": f"{ppd:.1f} posts/day"}

    def _score_follower_ratio(self, followers: int, following: int) -> Dict[str, Any]:
        """Analyze follower-to-following ratio."""
        if followers == 0 and following == 0:
            return {"score": 0.5, "detail": "No followers or following"}
        if following == 0:
            return {"score": 0.3, "detail": f"Only followers ({followers})"}
        ratio = followers / following
        if ratio < 0.01:  # Following many, few followers
            score = 0.85
        elif ratio < 0.1:
            score = 0.6
        elif ratio > 100:  # Unusual high ratio
            score = 0.4
        else:
            score = max(0.0, 0.3 - ratio * 0.05)
        return {"score": round(min(1.0, score), 4), "detail": f"Ratio: {ratio:.2f}"}

    def _score_username_pattern(self, username: str) -> Dict[str, Any]:
        """Check if username follows bot-like patterns."""
        score = 0.0
        flags = []

        # Random numbers at end
        if re.search(r"\d{4,}$", username):
            score += 0.3
            flags.append("numeric_suffix")

        # Very long random-looking
        if len(username) > 15 and re.search(r"[a-z]{2,}\d{3,}[a-z]*\d*", username):
            score += 0.3
            flags.append("random_pattern")

        # Default-looking names
        if re.match(r"^user_?\d+$", username, re.IGNORECASE):
            score += 0.5
            flags.append("default_name")

        # No vowels (generated)
        vowels = sum(1 for c in username.lower() if c in "aeiou")
        if len(username) > 5 and vowels / len(username) < 0.15:
            score += 0.2
            flags.append("few_vowels")

        return {"score": round(min(1.0, score), 4), "detail": flags if flags else ["normal_pattern"]}

    def _score_account_age(self, created_at: Optional[datetime]) -> Dict[str, Any]:
        """Score based on account age (very new = suspicious)."""
        if not created_at:
            return {"score": 0.5, "detail": "Unknown creation date"}
        age_days = (datetime.now(timezone.utc) - created_at).days
        if age_days < 7:
            score = 0.9
        elif age_days < 30:
            score = 0.6
        elif age_days < 90:
            score = 0.3
        else:
            score = max(0.0, 0.2 - age_days / 1000)
        return {"score": round(score, 4), "detail": f"{age_days} days old"}

    def _score_bio(self, bio: str) -> Dict[str, Any]:
        """Analyze bio for bot-like characteristics."""
        if not bio:
            return {"score": 0.4, "detail": "No bio"}
        score = 0.1
        if len(bio) < 10:
            score += 0.2
        # Crypto/spam keywords
        spam_words = ["follow back", "dm for", "crypto", "forex", "nft", "earn money",
                       "click link", "free", "giveaway", "promo code"]
        found = [w for w in spam_words if w in bio.lower()]
        score += len(found) * 0.15
        return {"score": round(min(1.0, score), 4), "detail": found if found else ["clean_bio"]}

    def _score_engagement(self, posts: int, likes_avg: float, comments_avg: float) -> Dict[str, Any]:
        """Score engagement patterns (no engagement on many posts = bot)."""
        if posts == 0:
            return {"score": 0.5, "detail": "No posts"}
        engagement_rate = (likes_avg + comments_avg) / max(posts, 1)
        if engagement_rate < 0.01:
            score = 0.8
        elif engagement_rate < 0.1:
            score = 0.5
        else:
            score = max(0.0, 0.3 - engagement_rate * 0.1)
        return {"score": round(min(1.0, score), 4), "detail": f"Engagement rate: {engagement_rate:.4f}"}

    def detect(self, profile: UserProfile, posts_data: Dict[str, Any] = None) -> BotDetectionResult:
        """Run full bot detection analysis on a user profile."""
        posts_data = posts_data or {}

        # Calculate individual signal scores
        account_age_days = 365  # default
        if profile.account_created:
            account_age_days = max(1, (datetime.now(timezone.utc) - profile.account_created).days)

        signal_scores = {}

        freq = self._score_posting_frequency(profile.posts_count, account_age_days)
        signal_scores["posting_frequency"] = freq["score"]

        age = self._score_account_age(profile.account_created)
        signal_scores["account_age"] = age["score"]

        ratio = self._score_follower_ratio(profile.followers_count, profile.following_count)
        signal_scores["follower_ratio"] = ratio["score"]

        name = self._score_username_pattern(profile.username)
        signal_scores["username_pattern"] = name["score"]

        bio = self._score_bio(profile.bio)
        signal_scores["bio_analysis"] = bio["score"]

        eng = self._score_engagement(
            profile.posts_count,
            posts_data.get("avg_likes", 0),
            posts_data.get("avg_comments", 0),
        )
        signal_scores["engagement_ratio"] = eng["score"]

        # Weighted total
        total = sum(
            signal_scores.get(key, 0.0) * weight
            for key, weight in self.weights.items()
            if key in signal_scores
        )
        # Normalize
        weight_sum = sum(self.weights[k] for k in signal_scores if k in self.weights)
        bot_score = total / weight_sum if weight_sum > 0 else 0.0

        is_bot = bot_score >= 0.55
        confidence = min(1.0, 0.4 + abs(bot_score - 0.5) * 1.2)

        # Collect flags
        flags = []
        if freq["score"] > 0.6:
            flags.append("high_posting_frequency")
        if age["score"] > 0.6:
            flags.append("new_account")
        if ratio["score"] > 0.6:
            flags.append("suspicious_follower_ratio")
        if name["score"] > 0.4:
            flags.append("bot_like_username")
        if bio["score"] > 0.5:
            flags.append("suspicious_bio")
        if eng["score"] > 0.6:
            flags.append("low_engagement")

        return BotDetectionResult(
            user_id=profile.id,
            username=profile.username,
            is_bot=is_bot,
            bot_score=round(bot_score, 4),
            signals=signal_scores,
            behavioral_flags=flags,
            confidence=round(confidence, 4),
        )


# Singleton
bot_detector = BotDetector()
