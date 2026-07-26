"""
historical_intelligence.py

GeoSentinel AI

Historical Intelligence Engine

Responsibilities
----------------
- Read historical analyses from SQLite.
- Parse stored JSON results.
- Build a chronological history for an AOI.
- Provide clean objects for trend analysis.

Pipeline

SQLite
    ↓
Historical Intelligence
    ↓
Temporal Evidence
    ↓
Mission Assessment
"""

from __future__ import annotations

import json
import sqlite3

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ==========================================================
# Database
# ==========================================================

DB_NAME = (
    Path(__file__).resolve().parent.parent
    / "backend"
    / "database"
    / "geosentinel.db"
)


# ==========================================================
# Historical Analysis
# ==========================================================

@dataclass
class HistoricalAnalysis:

    analysis_id: int

    timestamp: str

    confidence_score: float

    change_percentage: float

    prithvi: dict

    dynamic_world: dict

    fusion: dict

    transition: dict

    evidence: dict

    report: str

    metadata: dict = field(default_factory=dict)


# ==========================================================
# Trend Result
# ==========================================================

@dataclass
class TrendResult:

    metric: str

    values: list

    trend: str

    average: float

    minimum: float

    maximum: float

    latest: float


# ==========================================================
# Historical Intelligence Engine
# ==========================================================

class HistoricalIntelligence:

    """
    Reads previous analyses and produces
    historical intelligence.
    """

    def __init__(self):

        self.history: list[HistoricalAnalysis] = []

    # ------------------------------------------------------
    # Database
    # ------------------------------------------------------

    def _connect(self):

        return sqlite3.connect(DB_NAME)

    # ------------------------------------------------------
    # JSON Parsing
    # ------------------------------------------------------

    @staticmethod
    def _parse_json(value):

        if value is None:
            return {}

        if value == "":
            return {}

        try:
            return json.loads(value)

        except Exception:

            return {}

    # ------------------------------------------------------
    # Clear
    # ------------------------------------------------------

    def clear(self):

        self.history.clear()

    # ------------------------------------------------------
    # Load AOI History
    # ------------------------------------------------------

    def load_history(
        self,
        aoi_id,
        limit=20,
    ):

        self.clear()

        conn = self._connect()

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *

            FROM analysis_results

            WHERE aoi_id = ?

            ORDER BY timestamp ASC

            LIMIT ?
            """,
            (
                aoi_id,
                limit,
            ),
        )

        rows = cursor.fetchall()

        conn.close()

        for row in rows:

            analysis = HistoricalAnalysis(

                analysis_id=row["id"],

                timestamp=row["timestamp"],

                confidence_score=float(
                    row["confidence_score"] or 0
                ),

                change_percentage=float(
                    row["change_percentage"] or 0
                ),

                prithvi=self._parse_json(
                    row["prithvi_results"]
                ),

                dynamic_world=self._parse_json(
                    row["dynamic_world_results"]
                ),

                fusion=self._parse_json(
                    row["fusion_results"]
                ),

                transition=self._parse_json(
                    row["transition_results"]
                ),

                evidence=self._parse_json(
                    row["evidence_results"]
                ),

                report=row["report"],

                metadata={

                    "analysis_name":
                        row["analysis_name"],

                    "execution_time":
                        row["execution_time"],

                    "pipeline_version":
                        row["pipeline_version"],

                }

            )

            self.history.append(
                analysis
            )

        return self.history

    # ------------------------------------------------------
    # Basic Information
    # ------------------------------------------------------

    def count(self):

        return len(self.history)

    def latest(self):

        if not self.history:
            return None

        return self.history[-1]

    def oldest(self):

        if not self.history:
            return None

        return self.history[0]

    # ------------------------------------------------------
    # Generic Metric Extraction
    # ------------------------------------------------------

    def extract_metric(
        self,
        attribute,
    ):

        values = []

        for analysis in self.history:

            values.append(

                getattr(
                    analysis,
                    attribute,
                )

            )

        return values

    # ------------------------------------------------------
    # Utility
    # ------------------------------------------------------

    def has_history(self):

        return len(self.history) > 1

    def __len__(self):

        return len(self.history)

    def __iter__(self):

        return iter(self.history)

    def __repr__(self):

        return (
            f"HistoricalIntelligence("
            f"analyses={len(self.history)})"
        )

        # ------------------------------------------------------
    # Trend Detection
    # ------------------------------------------------------

    def _determine_trend(self, values):

        if len(values) < 2:
            return "Insufficient Data"

        increasing = True
        decreasing = True

        for i in range(1, len(values)):

            if values[i] < values[i - 1]:
                increasing = False

            if values[i] > values[i - 1]:
                decreasing = False

        if increasing:
            return "Increasing"

        if decreasing:
            return "Decreasing"

        return "Stable"

    # ------------------------------------------------------
    # Moving Average
    # ------------------------------------------------------

    @staticmethod
    def moving_average(values, window=3):

        if len(values) < window:
            return values

        averages = []

        for i in range(len(values)):

            start = max(0, i - window + 1)

            subset = values[start:i + 1]

            averages.append(
                round(
                    sum(subset) / len(subset),
                    2,
                )
            )

        return averages

    # ------------------------------------------------------
    # Change Trend
    # ------------------------------------------------------

    def change_trend(self):

        values = self.extract_metric(
            "change_percentage"
        )

        if not values:

            return None

        return TrendResult(

            metric="Change Percentage",

            values=values,

            trend=self._determine_trend(values),

            average=round(
                sum(values) / len(values),
                2,
            ),

            minimum=min(values),

            maximum=max(values),

            latest=values[-1],

        )

    # ------------------------------------------------------
    # Confidence Trend
    # ------------------------------------------------------

    def confidence_trend(self):

        values = self.extract_metric(
            "confidence_score"
        )

        if not values:

            return None

        return TrendResult(

            metric="Mission Confidence",

            values=values,

            trend=self._determine_trend(values),

            average=round(
                sum(values) / len(values),
                2,
            ),

            minimum=min(values),

            maximum=max(values),

            latest=values[-1],

        )

    # ------------------------------------------------------
    # Land Cover History
    # ------------------------------------------------------

    def landcover_history(self):

        history = []

        for analysis in self.history:

            after = analysis.prithvi.get(
                "after",
                {}
            )

            if not after:
                continue

            dominant = max(
                after,
                key=after.get,
            )

            history.append(

                {

                    "timestamp":
                        analysis.timestamp,

                    "dominant":
                        dominant,

                    "distribution":
                        after,

                }

            )

        return history

    # ------------------------------------------------------
    # Activity Score
    # ------------------------------------------------------

    def activity_score(self):

        if not self.history:
            return 0

        latest = self.latest()

        score = (
            latest.change_percentage * 0.6
            +
            latest.confidence_score * 0.4
        )

        return round(
            min(score, 100),
            2,
        )

    # ------------------------------------------------------
    # Anomaly Detection
    # ------------------------------------------------------

    def detect_anomalies(self):

        anomalies = []

        values = self.extract_metric(
            "change_percentage"
        )

        if len(values) < 5:
            return anomalies

        avg = sum(values[:-1]) / (len(values) - 1)

        latest = values[-1]

        if latest > avg * 1.5:

            anomalies.append(

                {

                    "type":
                        "Rapid Increase",

                    "expected":
                        round(avg, 2),

                    "observed":
                        latest,

                }

            )

        return anomalies

    # ------------------------------------------------------
    # Temporal Evidence
    # ------------------------------------------------------

    def temporal_evidence(self):

        evidence = []

        change = self.change_trend()

        if change:

            evidence.append(

                {

                    "category":
                        "Historical",

                    "name":
                        "Change Trend",

                    "trend":
                        change.trend,

                    "average":
                        change.average,

                    "latest":
                        change.latest,

                }

            )

        confidence = self.confidence_trend()

        if confidence:

            evidence.append(

                {

                    "category":
                        "Historical",

                    "name":
                        "Confidence Trend",

                    "trend":
                        confidence.trend,

                    "average":
                        confidence.average,

                    "latest":
                        confidence.latest,

                }

            )

        return evidence

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    def summary(self):

        return {

            "analyses":
                self.count(),

            "activity_score":
                self.activity_score(),

            "change_trend":
                self.change_trend(),

            "confidence_trend":
                self.confidence_trend(),

            "landcover":
                self.landcover_history(),

            "anomalies":
                self.detect_anomalies(),

            "temporal_evidence":
                self.temporal_evidence(),

        }