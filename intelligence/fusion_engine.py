"""
fusion_engine.py

GeoSentinel AI - Intelligence Fusion Engine

The Fusion Engine is responsible for combining evidence produced by
multiple AI perception models into a single intelligence assessment.

Unlike traditional computer vision pipelines that simply average model
outputs, the Fusion Engine performs evidence-based reasoning by
combining confidence scores from independent models.

The Fusion Engine does NOT perform:

- Object Detection
- Segmentation
- Change Detection
- Classification

Instead, it receives standardized Evidence objects produced by:

- Prithvi EO
- ChangeStar2
- Dynamic World
- Grounding DINO
- YOLO
- SSIM
- OSINT
- Future AI models

Responsibilities
----------------
- Collect evidence from all AI models.
- Maintain a unified evidence collection.
- Compute weighted mission confidence.
- Measure agreement between evidence.
- Produce a summary for the Rule Engine.
- Supply structured information to the Intelligence Report Generator.

This module forms the bridge between AI perception and high-level
geospatial reasoning.
"""

from intelligence.evidence import Evidence
from intelligence.evidence import EvidenceCollection


class FusionEngine:
    """
    Central evidence fusion engine.
    """

    def __init__(self):

        self.collection = EvidenceCollection()

    # ---------------------------------------------------------
    # Add Evidence
    # ---------------------------------------------------------

    def add(self, evidence: Evidence):
        """
        Add a single evidence object.
        """

        self.collection.add(evidence)

    def add_many(self, evidence_list):
        """
        Add multiple evidence objects.
        """

        for evidence in evidence_list:
            self.collection.add(evidence)

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def evidence_count(self):
        """
        Return total number of evidence objects.
        """

        return len(self.collection.evidence)

    def average_confidence(self):
        """
        Average confidence of all evidence.
        """

        return self.collection.average_confidence()

    def weighted_confidence(self):
        """
        Weighted confidence using evidence importance.
        """

        return self.collection.weighted_confidence()

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    def summary(self):
        """
        Return a summary of fused evidence.
        """

        return {

            "mission_confidence": round(
                self.weighted_confidence(),
                3
            ),

            "average_confidence": round(
                self.average_confidence(),
                3
            ),

            "total_evidence": self.evidence_count(),

            "sources": list(
                {
                    evidence.source
                    for evidence in self.collection.evidence
                }
            )

        }

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def clear(self):
        """
        Remove all stored evidence.
        """

        self.collection = EvidenceCollection()

    # ---------------------------------------------------------
    # String Representation
    # ---------------------------------------------------------

    def __repr__(self):

        return (
            f"FusionEngine("
            f"Evidence={self.evidence_count()}, "
            f"MissionConfidence={self.weighted_confidence():.2f}"
            f")"
        )