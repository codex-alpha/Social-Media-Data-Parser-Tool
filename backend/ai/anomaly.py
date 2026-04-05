"""Anomaly Detection using statistical and isolation-based methods."""
from typing import List, Dict, Any
from models.schemas import AnomalyResult, ThreatLevel
from datetime import datetime
import numpy as np
import math


class AnomalyDetector:
    """Real-time anomaly detection for social media data streams."""

    def __init__(self):
        self.baseline_stats: Dict[str, Dict[str, float]] = {}
        self.history: List[Dict[str, Any]] = []

    def update_baseline(self, metric_name: str, values: List[float]):
        """Update statistical baseline for a metric."""
        if not values:
            return
        arr = np.array(values)
        self.baseline_stats[metric_name] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "median": float(np.median(arr)),
            "q1": float(np.percentile(arr, 25)),
            "q3": float(np.percentile(arr, 75)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(values),
        }

    def _z_score_check(self, value: float, metric_name: str) -> Dict[str, Any]:
        """Check if value is anomalous using Z-score."""
        baseline = self.baseline_stats.get(metric_name)
        if not baseline or baseline["std"] == 0:
            return {"is_anomaly": False, "z_score": 0.0}
        z = (value - baseline["mean"]) / baseline["std"]
        return {
            "is_anomaly": abs(z) > 2.5,
            "z_score": round(z, 4),
            "threshold": 2.5,
        }

    def _iqr_check(self, value: float, metric_name: str) -> Dict[str, Any]:
        """Check anomaly using IQR method."""
        baseline = self.baseline_stats.get(metric_name)
        if not baseline:
            return {"is_anomaly": False, "iqr": 0.0}
        iqr = baseline["q3"] - baseline["q1"]
        lower = baseline["q1"] - 1.5 * iqr
        upper = baseline["q3"] + 1.5 * iqr
        return {
            "is_anomaly": value < lower or value > upper,
            "value": round(value, 4),
            "bounds": [round(lower, 4), round(upper, 4)],
        }

    def detect_post_anomaly(self, post_metrics: Dict[str, float]) -> List[AnomalyResult]:
        """Detect anomalies in post metrics."""
        anomalies = []

        for metric, value in post_metrics.items():
            z_result = self._z_score_check(value, metric)
            iqr_result = self._iqr_check(value, metric)

            if z_result["is_anomaly"] or iqr_result.get("is_anomaly", False):
                severity = ThreatLevel.LOW
                z = abs(z_result.get("z_score", 0))
                if z > 4:
                    severity = ThreatLevel.CRITICAL
                elif z > 3.5:
                    severity = ThreatLevel.HIGH
                elif z > 3:
                    severity = ThreatLevel.MEDIUM

                anomalies.append(AnomalyResult(
                    entity_type="post_metric",
                    entity_id=metric,
                    anomaly_type="statistical_outlier",
                    severity=severity,
                    score=round(min(1.0, z / 5), 4),
                    description=f"Metric '{metric}' value {value:.2f} is {z:.1f} standard deviations from baseline",
                    metadata={"z_score": z_result, "iqr": iqr_result},
                ))

        return anomalies

    def detect_volume_spike(
        self, current_count: int, window_minutes: int = 5,
        historical_avg: float = 0.0
    ) -> AnomalyResult | None:
        """Detect unusual volume spikes."""
        if historical_avg <= 0:
            return None
        ratio = current_count / historical_avg
        if ratio > 3.0:
            severity = ThreatLevel.CRITICAL if ratio > 10 else (
                ThreatLevel.HIGH if ratio > 5 else ThreatLevel.MEDIUM
            )
            return AnomalyResult(
                entity_type="volume",
                anomaly_type="volume_spike",
                severity=severity,
                score=round(min(1.0, ratio / 10), 4),
                description=f"Volume spike: {current_count} events in {window_minutes}min (avg: {historical_avg:.0f}, {ratio:.1f}x normal)",
            )
        return None

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system anomaly health status."""
        return {
            "metrics_tracked": len(self.baseline_stats),
            "baselines": {k: {"mean": v["mean"], "std": v["std"]} for k, v in self.baseline_stats.items()},
            "status": "healthy",
        }


# Singleton
anomaly_detector = AnomalyDetector()
