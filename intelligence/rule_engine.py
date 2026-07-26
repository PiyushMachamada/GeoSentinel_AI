"""
rule_engine.py

GeoSentinel AI - Knowledge Driven Rule Engine

The Rule Engine converts fused evidence into high-level
intelligence events using mission-specific knowledge bases.

It performs deterministic reasoning and does not rely on
a language model for decision making.

Pipeline

Evidence
    ↓
Knowledge Base
    ↓
Rule Engine
    ↓
Mission Assessment
"""

from dataclasses import dataclass, field

from intelligence.evidence import (
    Evidence,
    EvidenceCollection,
)

from intelligence.knowledge_loader import load


# ==========================================================
# Intelligence Event
# ==========================================================

@dataclass
class IntelligenceEvent:
    """
    Represents an inferred intelligence event.
    """

    name: str

    confidence: float

    explanation: str

    supporting_models: list[str] = field(default_factory=list)

    supporting_evidence: list[Evidence] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)


# ==========================================================
# Rule Engine
# ==========================================================

class RuleEngine:

    def __init__(self):

        self.events: list[IntelligenceEvent] = []

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def evaluate(
        self,
        evidence: EvidenceCollection,
        profile,
    ):

        self.events.clear()

        knowledge = load(profile.name)

        if not knowledge:
            return self.events

        for event_name, rule in knowledge.items():

            self._evaluate_rule(
                event_name,
                rule,
                evidence,
            )

        return self.events

    # ------------------------------------------------------
    # Individual Rule
    # ------------------------------------------------------

    def _evaluate_rule(
        self,
        event_name,
        rule,
        evidence,
    ):

        supporting = []

        score = 0.0

        # --------------------------------------------------
        # Change Requirement
        # --------------------------------------------------

        minimum_change = rule.get(
            "minimum_change"
        )

        if minimum_change is not None:

            change = evidence.by_source(
                "ChangeStar"
            )

            if not change:
                return

            change_percentage = (
                change[0].metadata.get(
                    "change_percentage",
                    0
                )
            )

            if change_percentage < minimum_change:
                return

            supporting.extend(change)

            score += 0.40

        # --------------------------------------------------
        # Object Requirement
        # --------------------------------------------------

        required_objects = rule.get(
            "required_objects",
            []
        )

        if required_objects:

            detections = evidence.by_category(
                "Object Detection"
            )

            matched = []

            for obj in detections:

                label = obj.metadata.get(
                    "label",
                    ""
                )

                if label in required_objects:

                    matched.append(obj)

            if not matched:
                return

            supporting.extend(matched)

            score += min(
                len(matched) * 0.10,
                0.40
            )

        # --------------------------------------------------
        # Land Cover Requirement
        # --------------------------------------------------

        required_landcover = rule.get(
            "landcover",
            []
        )

        if required_landcover:

            landcover = evidence.by_category(
                "Land Cover"
            )

            found = False

            for lc in landcover:

                dominant = lc.metadata.get(
                    "dominant_class",
                    ""
                )

                if dominant in required_landcover:

                    supporting.append(lc)

                    found = True

                    break

            if not found:
                return

            score += 0.20

        # --------------------------------------------------
        # Final Confidence
        # --------------------------------------------------

        confidence = min(
            max(score, 0.50),
            0.99
        )

        models = sorted(
            {
                e.source
                for e in supporting
            }
        )

        explanation = (
            f"{event_name} inferred from "
            f"{len(supporting)} supporting evidence item(s)."
        )

        self.events.append(

            IntelligenceEvent(

                name=event_name,

                confidence=confidence,

                explanation=explanation,

                supporting_models=models,

                supporting_evidence=supporting,

                metadata={

                    "priority": rule.get(
                        "priority",
                        "Unknown"
                    )

                }

            )

        )

    # ------------------------------------------------------
    # Summary
    # ------------------------------------------------------

    def summary(self):

        return [

            {

                "event": event.name,

                "confidence": round(
                    event.confidence,
                    2
                ),

                "priority": event.metadata.get(
                    "priority",
                    "Unknown"
                ),

                "models": event.supporting_models,

                "explanation": event.explanation,

            }

            for event in self.events

        ]

    # ------------------------------------------------------
    # Reset
    # ------------------------------------------------------

    def clear(self):

        self.events.clear()

    # ------------------------------------------------------
    # String Representation
    # ------------------------------------------------------

    def __repr__(self):

        return (
            f"RuleEngine("
            f"Events={len(self.events)})"
        )