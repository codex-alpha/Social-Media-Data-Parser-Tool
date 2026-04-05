"""Timeline Reconstruction for forensic event analysis."""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from models.schemas import TimelineEvent, ThreatLevel, Platform
from forensics.hasher import forensic_hasher
import uuid


class TimelineReconstructor:
    """Forensic timeline reconstruction engine.

    Builds chronological event timelines from multiple data sources,
    detects gaps, identifies patterns, and correlates events.
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.gaps: List[Dict[str, Any]] = []

    def add_event(
        self, timestamp: datetime, event_type: str, platform: str,
        actor: str, action: str, target: str = "",
        content_preview: str = "", metadata: Dict = None,
        severity: str = "none"
    ) -> Dict[str, Any]:
        """Add a new event to the timeline."""
        event_id = f"TLE-{uuid.uuid4().hex[:10].upper()}"
        event_hash = forensic_hasher.hash_data({
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
        })

        event = {
            "id": event_id,
            "timestamp": timestamp.isoformat(),
            "timestamp_unix": timestamp.timestamp(),
            "event_type": event_type,
            "platform": platform,
            "actor": actor,
            "action": action,
            "target": target,
            "content_preview": content_preview[:200] if content_preview else "",
            "metadata": metadata or {},
            "severity": severity,
            "forensic_hash": event_hash,
        }

        self.events.append(event)
        self.events.sort(key=lambda x: x["timestamp_unix"])
        return event

    def get_timeline(
        self, start: datetime = None, end: datetime = None,
        platform: str = None, actor: str = None,
        event_type: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get filtered timeline events."""
        filtered = self.events.copy()

        if start:
            filtered = [e for e in filtered if e["timestamp_unix"] >= start.timestamp()]
        if end:
            filtered = [e for e in filtered if e["timestamp_unix"] <= end.timestamp()]
        if platform:
            filtered = [e for e in filtered if e["platform"] == platform]
        if actor:
            filtered = [e for e in filtered if e["actor"] == actor]
        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]

        return filtered[:limit]

    def detect_gaps(self, expected_interval_minutes: int = 60) -> List[Dict[str, Any]]:
        """Detect gaps in the timeline (periods of no activity)."""
        if len(self.events) < 2:
            return []

        self.gaps = []
        sorted_events = sorted(self.events, key=lambda x: x["timestamp_unix"])

        for i in range(1, len(sorted_events)):
            gap = sorted_events[i]["timestamp_unix"] - sorted_events[i - 1]["timestamp_unix"]
            gap_minutes = gap / 60

            if gap_minutes > expected_interval_minutes:
                self.gaps.append({
                    "gap_start": sorted_events[i - 1]["timestamp"],
                    "gap_end": sorted_events[i]["timestamp"],
                    "duration_minutes": round(gap_minutes, 1),
                    "duration_hours": round(gap_minutes / 60, 2),
                    "before_event": sorted_events[i - 1]["id"],
                    "after_event": sorted_events[i]["id"],
                    "suspicious": gap_minutes > expected_interval_minutes * 3,
                })

        return self.gaps

    def find_patterns(self) -> Dict[str, Any]:
        """Identify temporal patterns in the timeline."""
        if not self.events:
            return {"patterns": [], "summary": "No events to analyze"}

        # Activity by hour
        hour_counts = [0] * 24
        for event in self.events:
            ts = datetime.fromisoformat(event["timestamp"])
            hour_counts[ts.hour] += 1

        peak_hour = hour_counts.index(max(hour_counts))

        # Activity by platform
        platform_counts: Dict[str, int] = {}
        for event in self.events:
            p = event["platform"]
            platform_counts[p] = platform_counts.get(p, 0) + 1

        # Burst detection
        bursts = self._detect_bursts()

        # Actor frequency
        actor_counts: Dict[str, int] = {}
        for event in self.events:
            a = event["actor"]
            actor_counts[a] = actor_counts.get(a, 0) + 1

        return {
            "total_events": len(self.events),
            "hourly_distribution": hour_counts,
            "peak_activity_hour": peak_hour,
            "platform_distribution": platform_counts,
            "top_actors": sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "bursts_detected": len(bursts),
            "bursts": bursts,
        }

    def _detect_bursts(self, window_seconds: int = 300, threshold: int = 5) -> List[Dict[str, Any]]:
        """Detect bursts of activity within time windows."""
        if len(self.events) < threshold:
            return []

        bursts = []
        sorted_events = sorted(self.events, key=lambda x: x["timestamp_unix"])

        i = 0
        while i < len(sorted_events):
            window_end = sorted_events[i]["timestamp_unix"] + window_seconds
            window_events = [
                e for e in sorted_events[i:]
                if e["timestamp_unix"] <= window_end
            ]
            if len(window_events) >= threshold:
                bursts.append({
                    "start": sorted_events[i]["timestamp"],
                    "end": datetime.fromtimestamp(window_end, tz=timezone.utc).isoformat(),
                    "event_count": len(window_events),
                    "window_seconds": window_seconds,
                })
                i += len(window_events)
            else:
                i += 1

        return bursts

    def get_actor_timeline(self, actor: str) -> Dict[str, Any]:
        """Get complete timeline for a specific actor."""
        actor_events = [e for e in self.events if e["actor"] == actor]
        return {
            "actor": actor,
            "total_events": len(actor_events),
            "events": sorted(actor_events, key=lambda x: x["timestamp_unix"]),
            "platforms_used": list(set(e["platform"] for e in actor_events)),
            "first_seen": actor_events[0]["timestamp"] if actor_events else None,
            "last_seen": actor_events[-1]["timestamp"] if actor_events else None,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get timeline statistics."""
        return {
            "total_events": len(self.events),
            "total_gaps": len(self.gaps),
            "event_types": list(set(e["event_type"] for e in self.events)),
            "platforms": list(set(e["platform"] for e in self.events)),
            "actors": list(set(e["actor"] for e in self.events)),
            "time_range": {
                "start": self.events[0]["timestamp"] if self.events else None,
                "end": self.events[-1]["timestamp"] if self.events else None,
            }
        }


# Singleton
timeline_reconstructor = TimelineReconstructor()
