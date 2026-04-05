"""Account Correlation Engine for cross-platform identity analysis."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from forensics.hasher import forensic_hasher
import re
import math
import uuid


class AccountCorrelator:
    """Cross-platform account correlation and identity analysis.

    Correlates accounts across platforms using:
    - Username similarity
    - Behavioral fingerprinting
    - Temporal activity overlap
    - Linguistic pattern matching
    - Network overlap analysis
    - Device/IP fingerprint simulation
    """

    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.correlations: List[Dict[str, Any]] = []

    def register_profile(self, profile: Dict[str, Any]) -> str:
        """Register a user profile for correlation analysis."""
        profile_id = profile.get("id", str(uuid.uuid4()))
        self.profiles[profile_id] = profile
        return profile_id

    def _username_similarity(self, name1: str, name2: str) -> float:
        """Calculate username similarity using Levenshtein-based method."""
        n1 = re.sub(r"[^a-z0-9]", "", name1.lower())
        n2 = re.sub(r"[^a-z0-9]", "", name2.lower())
        if n1 == n2:
            return 1.0
        if not n1 or not n2:
            return 0.0

        # Check if one contains the other
        if n1 in n2 or n2 in n1:
            return 0.8

        # Simple character overlap ratio
        set1 = set(n1)
        set2 = set(n2)
        intersection = set1 & set2
        union = set1 | set2
        jaccard = len(intersection) / len(union) if union else 0.0

        # N-gram overlap
        def ngrams(s, n=2):
            return set(s[i:i+n] for i in range(len(s)-n+1))

        ng1 = ngrams(n1)
        ng2 = ngrams(n2)
        if ng1 and ng2:
            ng_sim = len(ng1 & ng2) / len(ng1 | ng2)
        else:
            ng_sim = 0.0

        return round((jaccard * 0.4 + ng_sim * 0.6), 4)

    def _behavioral_similarity(self, p1: Dict, p2: Dict) -> float:
        """Compare behavioral patterns between accounts."""
        score = 0.0
        signals = 0

        # Posting frequency similarity
        ppd1 = p1.get("posts_per_day", 0)
        ppd2 = p2.get("posts_per_day", 0)
        if ppd1 > 0 and ppd2 > 0:
            freq_sim = 1.0 - min(1.0, abs(ppd1 - ppd2) / max(ppd1, ppd2))
            score += freq_sim
            signals += 1

        # Active hours overlap
        hours1 = set(p1.get("active_hours", []))
        hours2 = set(p2.get("active_hours", []))
        if hours1 and hours2:
            hour_overlap = len(hours1 & hours2) / len(hours1 | hours2)
            score += hour_overlap
            signals += 1

        # Language overlap
        langs1 = set(p1.get("languages", []))
        langs2 = set(p2.get("languages", []))
        if langs1 and langs2:
            lang_overlap = len(langs1 & langs2) / len(langs1 | langs2)
            score += lang_overlap
            signals += 1

        # Hashtag usage similarity
        tags1 = set(p1.get("frequent_hashtags", []))
        tags2 = set(p2.get("frequent_hashtags", []))
        if tags1 and tags2:
            tag_overlap = len(tags1 & tags2) / len(tags1 | tags2)
            score += tag_overlap
            signals += 1

        return round(score / max(signals, 1), 4)

    def _temporal_overlap(self, p1: Dict, p2: Dict) -> float:
        """Analyze temporal activity overlap between accounts."""
        hours1 = p1.get("active_hours", [])
        hours2 = p2.get("active_hours", [])

        if not hours1 or not hours2:
            return 0.0

        set1 = set(hours1)
        set2 = set(hours2)
        overlap = len(set1 & set2)
        total = len(set1 | set2)

        return round(overlap / total if total > 0 else 0.0, 4)

    def _linguistic_similarity(self, p1: Dict, p2: Dict) -> float:
        """Compare linguistic patterns."""
        vocab1 = set(p1.get("vocabulary_sample", []))
        vocab2 = set(p2.get("vocabulary_sample", []))

        if not vocab1 or not vocab2:
            return 0.0

        overlap = len(vocab1 & vocab2) / len(vocab1 | vocab2)
        return round(overlap, 4)

    def _device_fingerprint_sim(self, p1: Dict, p2: Dict) -> float:
        """Simulate device/IP fingerprint comparison."""
        fp1 = p1.get("device_fingerprint", {})
        fp2 = p2.get("device_fingerprint", {})

        if not fp1 or not fp2:
            return 0.0

        match_count = 0
        total = 0

        for key in set(fp1.keys()) | set(fp2.keys()):
            if key in fp1 and key in fp2:
                total += 1
                if fp1[key] == fp2[key]:
                    match_count += 1

        return round(match_count / total if total > 0 else 0.0, 4)

    def correlate(self, profile1_id: str, profile2_id: str) -> Dict[str, Any]:
        """Perform full correlation analysis between two profiles."""
        p1 = self.profiles.get(profile1_id, {})
        p2 = self.profiles.get(profile2_id, {})

        if not p1 or not p2:
            return {"error": "Profile(s) not found"}

        username_sim = self._username_similarity(
            p1.get("username", ""), p2.get("username", "")
        )
        behavioral_sim = self._behavioral_similarity(p1, p2)
        temporal_sim = self._temporal_overlap(p1, p2)
        linguistic_sim = self._linguistic_similarity(p1, p2)
        device_sim = self._device_fingerprint_sim(p1, p2)

        # Weighted composite score
        weights = {
            "username": 0.15,
            "behavioral": 0.25,
            "temporal": 0.20,
            "linguistic": 0.25,
            "device": 0.15,
        }
        composite = (
            username_sim * weights["username"] +
            behavioral_sim * weights["behavioral"] +
            temporal_sim * weights["temporal"] +
            linguistic_sim * weights["linguistic"] +
            device_sim * weights["device"]
        )

        correlation = {
            "id": f"COR-{uuid.uuid4().hex[:10].upper()}",
            "profile1": {"id": profile1_id, "username": p1.get("username", ""), "platform": p1.get("platform", "")},
            "profile2": {"id": profile2_id, "username": p2.get("username", ""), "platform": p2.get("platform", "")},
            "correlation_score": round(composite, 4),
            "is_likely_same_person": composite >= 0.6,
            "confidence": round(min(1.0, composite * 1.3), 4),
            "signals": {
                "username_similarity": username_sim,
                "behavioral_similarity": behavioral_sim,
                "temporal_overlap": temporal_sim,
                "linguistic_similarity": linguistic_sim,
                "device_fingerprint": device_sim,
            },
            "risk_assessment": "HIGH" if composite >= 0.7 else ("MEDIUM" if composite >= 0.4 else "LOW"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.correlations.append(correlation)
        return correlation

    def correlate_all(self) -> List[Dict[str, Any]]:
        """Correlate all registered profiles against each other."""
        results = []
        profile_ids = list(self.profiles.keys())

        for i in range(len(profile_ids)):
            for j in range(i + 1, len(profile_ids)):
                result = self.correlate(profile_ids[i], profile_ids[j])
                if "error" not in result:
                    results.append(result)

        return sorted(results, key=lambda x: x["correlation_score"], reverse=True)

    def get_correlations(self) -> List[Dict[str, Any]]:
        """Get all correlation results."""
        return self.correlations

    def get_statistics(self) -> Dict[str, Any]:
        """Get correlation statistics."""
        return {
            "total_profiles": len(self.profiles),
            "total_correlations": len(self.correlations),
            "high_risk": sum(1 for c in self.correlations if c["risk_assessment"] == "HIGH"),
            "medium_risk": sum(1 for c in self.correlations if c["risk_assessment"] == "MEDIUM"),
            "low_risk": sum(1 for c in self.correlations if c["risk_assessment"] == "LOW"),
        }


# Singleton
account_correlator = AccountCorrelator()
