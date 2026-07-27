from dataclasses import dataclass


@dataclass
class ConfidenceResult:
    score: float
    level: str
    breakdown: dict
    reasoning: str


class MissionConfidenceEngine:
    """
    Computes mission confidence from cross-model agreement,
    observation quality, and evidence consistency.
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
        preprocessing_results=None,
    ):
        preprocessing_results = preprocessing_results or {}
        breakdown = {}

        segmentation_confidence = float(
            prithvi_results.get(
                "confidence_summary",
                {},
            ).get(
                "after_average_confidence",
                0.0,
            )
        )
        detection_confidence = float(
            grounding_dino_results.get(
                "statistics",
                {},
            ).get(
                "overall_average_confidence",
                0.0,
            )
        ) * 100.0
        change_confidence = float(
            changestar_results.get("confidence", 0.0)
        ) * 100.0
        model_agreement = float(
            fusion_results.get("model_agreement_score", 0.0)
        )
        evidence_score = float(
            evidence_validation_results.get("evidence_score", 0.0)
        )
        evidence_reliability = float(
            reliability_results.get("overall").score
            if reliability_results.get("overall") else 0.0
        ) * 100.0
        cloud_percentage = float(
            preprocessing_results.get("cloud_fraction", {}).get("average", 0.0)
        )
        water_percentage = float(
            preprocessing_results.get("water_fraction", {}).get("average", 0.0)
        )
        image_quality = float(
            preprocessing_results.get("image_quality", {}).get("valid_fraction", 0.0)
        )
        temporal_consistency = float(
            fusion_results.get("agreement_matrix", {}).get("changestar_vs_ssim", 0.0)
        )
        spatial_consistency = float(
            fusion_results.get("agreement_matrix", {}).get("prithvi_vs_dynamic_world", 0.0)
        )
        uncertainty = float(
            prithvi_results.get("confidence_summary", {}).get("after_average_uncertainty", 100.0)
        )

        breakdown["model_agreement"] = round(model_agreement, 2)
        breakdown["evidence_validation"] = round(evidence_score, 2)
        breakdown["evidence_reliability"] = round(evidence_reliability, 2)
        breakdown["segmentation_confidence"] = round(segmentation_confidence, 2)
        breakdown["detection_confidence"] = round(detection_confidence, 2)
        breakdown["change_confidence"] = round(change_confidence, 2)
        breakdown["image_quality"] = round(image_quality, 2)
        breakdown["spatial_consistency"] = round(spatial_consistency, 2)
        breakdown["temporal_consistency"] = round(temporal_consistency, 2)
        breakdown["cloud_penalty"] = round(max(0.0, 100.0 - cloud_percentage * 4.0), 2)
        breakdown["water_penalty"] = round(max(0.0, 100.0 - water_percentage * 2.0), 2)
        breakdown["uncertainty_penalty"] = round(max(0.0, 100.0 - uncertainty), 2)

        final_score = round(
            (
                0.18 * breakdown["model_agreement"]
                + 0.12 * breakdown["evidence_validation"]
                + 0.12 * breakdown["evidence_reliability"]
                + 0.10 * breakdown["segmentation_confidence"]
                + 0.08 * breakdown["detection_confidence"]
                + 0.12 * breakdown["change_confidence"]
                + 0.08 * breakdown["image_quality"]
                + 0.08 * breakdown["spatial_consistency"]
                + 0.06 * breakdown["temporal_consistency"]
                + 0.03 * breakdown["cloud_penalty"]
                + 0.02 * breakdown["water_penalty"]
                + 0.01 * breakdown["uncertainty_penalty"]
            ),
            2,
        )

        if final_score >= 80:
            level = "HIGH"
        elif final_score >= 60:
            level = "MEDIUM"
        else:
            level = "LOW"

        reasoning = (
            f"{level} confidence driven by model agreement ({model_agreement:.1f}%), "
            f"evidence reliability ({evidence_reliability:.1f}%), "
            f"segmentation confidence ({segmentation_confidence:.1f}%), "
            f"change confidence ({change_confidence:.1f}%), "
            f"cloud cover ({cloud_percentage:.1f}%), and water influence ({water_percentage:.1f}%)."
        )

        return ConfidenceResult(
            score=final_score,
            level=level,
            breakdown=breakdown,
            reasoning=reasoning,
        )
