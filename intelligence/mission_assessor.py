"""
mission_assessor.py

GeoSentinel AI - Mission Assessor

The Mission Assessor is the top-level intelligence component of
GeoSentinel AI.

It combines:

- Evidence
- Fusion Engine
- Rule Engine
- AOI Profile

to produce a complete intelligence assessment.

The Mission Assessor is responsible for:

- Collecting evidence from all AI models
- Running evidence fusion
- Applying reasoning rules
- Computing mission confidence
- Assigning a threat level
- Producing a structured intelligence summary

This module is the final reasoning stage before report generation.
"""

from intelligence.evidence import Evidence
from intelligence.fusion_engine import FusionEngine
from intelligence.rule_engine import RuleEngine
from intelligence.profiles import AOIProfile


class MissionAssessor:
    """
    Coordinates the intelligence pipeline.
    """

    def __init__(self, profile: AOIProfile):

        self.profile = profile

        self.fusion = FusionEngine()

        self.rule_engine = RuleEngine()

    # ----------------------------------------------------
    # Add Evidence
    # ----------------------------------------------------

    def add_evidence(self, evidence: Evidence):

        self.fusion.add(evidence)

    def add_many(self, evidence_list):

        self.fusion.add_many(evidence_list)

    # ----------------------------------------------------
    # Assessment
    # ----------------------------------------------------

    def assess(self):

        summary = self.fusion.summary()

        events = self.rule_engine.evaluate(
            self.fusion.collection,
            self.profile
        )

        mission_confidence = summary[
            "mission_confidence"
        ]

        threat_level = self._calculate_threat_level(
            mission_confidence,
            len(events)
        )

        return {

            "profile": self.profile.name,

            "mission_confidence":
                mission_confidence,

            "threat_level":
                threat_level,

            "total_evidence":
                summary["total_evidence"],

            "average_confidence":
                summary["average_confidence"],

            "sources":
                summary["sources"],

            "events":
                self.rule_engine.summary()

        }

    # ----------------------------------------------------
    # Threat Assessment
    # ----------------------------------------------------

    def _calculate_threat_level(

        self,

        confidence,

        event_count

    ):

        score = confidence + (event_count * 5)

        if score >= 90:
            return "Critical"

        if score >= 75:
            return "High"

        if score >= 50:
            return "Medium"

        if score >= 25:
            return "Low"

        return "Minimal"

    # ----------------------------------------------------
    # Reset
    # ----------------------------------------------------

    def clear(self):

        self.fusion.clear()

        self.rule_engine.clear()

    # ----------------------------------------------------
    # String Representation
    # ----------------------------------------------------

    def __repr__(self):

        return (

            f"MissionAssessor("

            f"Profile={self.profile.name}, "

            f"Evidence={self.fusion.evidence_count()})"

        )