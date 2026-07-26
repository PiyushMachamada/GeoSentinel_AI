from dataclasses import dataclass


@dataclass
class ConfidenceResult:

    score: float
    level: str
    breakdown: dict
    reasoning: str


class MissionConfidenceEngine:
    """
    Computes the overall mission confidence.

    Confidence measures the reliability of the intelligence,
    NOT the magnitude of detected change.
    """

    def compute(
        self,
        grounding_dino_results,
        prithvi_results,
        dynamic_world_results,
        changestar_results,
        fusion_results,
        evidence_validation_results,
        reliability_results,
    ):

        breakdown = {}

        # -------------------------------------------------
        # Change Evidence (25)
        # -------------------------------------------------

        confidence = float(
            changestar_results.get(
                "confidence",
                0.70
            )
        )

        change_score = round(
            confidence * 25,
            2
        )

        breakdown["change_detection"] = change_score

        # -------------------------------------------------
        # Object Evidence (15)
        # -------------------------------------------------

        detections = []

        detections.extend(
            grounding_dino_results.get(
                "before",
                []
            )
        )

        detections.extend(
            grounding_dino_results.get(
                "after",
                []
            )
        )

        if detections:

            avg = sum(
                d["confidence"]
                for d in detections
            ) / len(detections)

            object_score = round(
                avg * 15,
                2,
            )

        else:

            object_score = 0

        breakdown["object_detection"] = object_score

        # -------------------------------------------------
        # Fusion Agreement (20)
        # -------------------------------------------------

        model_agreement = float(
            fusion_results.get(
                "model_agreement_score",
                0,
            )
        )

        fusion_score = round(
            (model_agreement / 100) * 20,
            2,
        )

        breakdown["fusion"] = fusion_score

        # -------------------------------------------------
        # Evidence Validation (25)
        # -------------------------------------------------

        evidence_score = float(
            evidence_validation_results.get(
                "evidence_score",
                0,
            )
        )

        evidence_score = (
            evidence_score / 100
        ) * 25

        breakdown["evidence_validation"] = round(
            evidence_score,
            2,
        )

        # -------------------------------------------------
        # Evidence Reliability (15)
        # -------------------------------------------------

        overall_reliability = reliability_results.get(
            "overall"
        )

        if overall_reliability:

            reliability_score = (
                overall_reliability.score * 15
            )

        else:

            reliability_score = 0

        breakdown["reliability"] = round(
            reliability_score,
            2,
        )

        # -------------------------------------------------
        # Semantic Evidence (15)
        # -------------------------------------------------

        reasoned = fusion_results.get(
            "reasoned_evidence",
            []
        )

        if isinstance(reasoned, dict):
            transition_count = len(reasoned.keys())
        else:
            transition_count = len(reasoned)

        if transition_count >= 5:

            semantic_score = 15

        elif transition_count >= 2:

            semantic_score = 10

        elif transition_count >= 1:

            semantic_score = 5

        else:

            semantic_score = 0

        breakdown["semantic"] = semantic_score

        # -------------------------------------------------
        # Final Score
        # -------------------------------------------------

        final_score = round(
            (sum(breakdown.values()) / 115) * 100,
            2,
        )
        if final_score >= 80:

            level = "HIGH"

        elif final_score >= 60:

            level = "MEDIUM"

        else:

            level = "LOW"

        reasoning = (
            f"{level} confidence based on "
            f"model agreement ({model_agreement:.1f}%), "
            f"validated evidence ({evidence_score / 25 * 100:.1f}%), "
            f"object detection quality ({(object_score / 15) * 100:.1f}%), "
            f"and evidence reliability ({overall_reliability.score * 100:.1f}%)."
        )
        return ConfidenceResult(

            score=final_score,

            level=level,

            breakdown=breakdown,

            reasoning=reasoning,

        )