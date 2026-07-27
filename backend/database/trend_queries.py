"""
trend_queries.py

GeoSentinel AI — Historical trend queries.

Provides aggregated trend metrics for an AOI by reading
historical analysis records from SQLite.
"""

import json
import sqlite3
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / "geosentinel.db"


def _safe_parse(value) -> dict:
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def get_aoi_trend(aoi_id: str) -> dict:
    """
    Returns trend data for an AOI in a format suitable for the dashboard.

    Fields:
    - timestamps: list of ISO timestamps in ascending order
    - confidence_scores: list of floats
    - change_percentages: list of floats
    - dominant_landcover: list of {timestamp, class}
    - trend_direction: "Increasing" | "Decreasing" | "Stable" | "Insufficient Data"
    - change_trend: str
    - confidence_trend: str
    - analyses_count: int
    - avg_confidence: float
    - avg_change: float
    - max_change: float
    - latest_change: float
    - latest_confidence: float
    - growth_rates: list of floats (change % deltas)
    """

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id,
               timestamp,
               confidence_score,
               change_percentage,
               prithvi_results,
               fusion_results
        FROM analysis_results
        WHERE aoi_id = ?
        ORDER BY timestamp ASC
        """,
        (aoi_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {
            "aoi_id": aoi_id,
            "analyses_count": 0,
            "timestamps": [],
            "confidence_scores": [],
            "change_percentages": [],
            "dominant_landcover": [],
            "trend_direction": "Insufficient Data",
            "change_trend": "Insufficient Data",
            "confidence_trend": "Insufficient Data",
            "growth_rates": [],
            "avg_confidence": 0.0,
            "avg_change": 0.0,
            "max_change": 0.0,
            "latest_change": 0.0,
            "latest_confidence": 0.0,
        }

    timestamps = []
    confidence_scores = []
    change_percentages = []
    dominant_landcover = []

    for row in rows:
        timestamps.append(row["timestamp"])

        conf = float(row["confidence_score"] or 0)
        change = float(row["change_percentage"] or 0)
        confidence_scores.append(round(conf, 2))
        change_percentages.append(round(change, 2))

        prithvi = _safe_parse(row["prithvi_results"])
        after = prithvi.get("after", {})
        if after:
            dominant = max(after, key=after.get)
        else:
            # Try fusion results
            fusion = _safe_parse(row["fusion_results"])
            dominant = fusion.get("dominant_prithvi", "unknown")

        dominant_landcover.append(
            {"timestamp": row["timestamp"], "class": dominant}
        )

    # Trend direction for change %
    change_trend = _trend_direction(change_percentages)
    confidence_trend = _trend_direction(confidence_scores)

    # Growth rates (delta between consecutive change %)
    growth_rates = []
    for i in range(1, len(change_percentages)):
        delta = round(change_percentages[i] - change_percentages[i - 1], 2)
        growth_rates.append(delta)

    n = len(change_percentages)
    avg_conf = round(sum(confidence_scores) / n, 2) if n else 0.0
    avg_change = round(sum(change_percentages) / n, 2) if n else 0.0

    return {
        "aoi_id": aoi_id,
        "analyses_count": n,
        "timestamps": timestamps,
        "confidence_scores": confidence_scores,
        "change_percentages": change_percentages,
        "dominant_landcover": dominant_landcover,
        "trend_direction": change_trend,
        "change_trend": change_trend,
        "confidence_trend": confidence_trend,
        "growth_rates": growth_rates,
        "avg_confidence": avg_conf,
        "avg_change": avg_change,
        "max_change": max(change_percentages) if change_percentages else 0.0,
        "latest_change": change_percentages[-1] if change_percentages else 0.0,
        "latest_confidence": confidence_scores[-1] if confidence_scores else 0.0,
    }


def _trend_direction(values: list) -> str:
    if len(values) < 2:
        return "Insufficient Data"

    increasing = all(values[i] >= values[i - 1] for i in range(1, len(values)))
    decreasing = all(values[i] <= values[i - 1] for i in range(1, len(values)))

    if increasing:
        return "Increasing"
    if decreasing:
        return "Decreasing"

    # Check overall direction using linear regression slope sign
    n = len(values)
    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n
    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return "Stable"

    slope = numerator / denominator
    if slope > 0.5:
        return "Gradually Increasing"
    if slope < -0.5:
        return "Gradually Decreasing"
    return "Stable"
