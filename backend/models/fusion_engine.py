import copy
import json
from pathlib import Path

import cv2
import numpy as np
import rasterio

from backend.models.evidence_reasoning import EvidenceReasoner
from backend.models.evidence_validation import EvidenceValidator


class FusionEngine:

    def __init__(self):
        print("\n" + "=" * 60)
        print("Loading GeoSentinel Fusion Engine")
        print("=" * 60)

        self.class_mapping = {
            "forest": "trees",
            "river": "water",
            "agricultural_area": "crops",
            "residential_area": "built_area",
            "unused_land": "bare_ground",
            "road": "built_area",
            "background": "unknown"
        }

        self.dynamic_world_ids = {
            "water": 0,
            "trees": 1,
            "grass": 2,
            "flooded_vegetation": 3,
            "crops": 4,
            "shrub_and_scrub": 5,
            "built_area": 6,
            "bare_ground": 7,
            "snow_and_ice": 8,
        }

        self.evidence_validator = EvidenceValidator()
        self.evidence_reasoner = EvidenceReasoner()

    def get_dominant_dynamic_world(self, dynamic_world_results):
        if not dynamic_world_results:
            return "unknown", 0.0

        after = {
            cls: values.get("after", 0)
            for cls, values in dynamic_world_results.items()
            if isinstance(values, dict)
        }
        if not after:
            return "unknown", 0.0

        dominant = max(after, key=after.get)
        return dominant, float(after[dominant])

    def get_dominant_prithvi(self, prithvi_results):
        after = prithvi_results.get("after", {})
        if not after:
            return "unknown", 0.0

        dominant = max(after, key=after.get)
        return dominant, float(after[dominant])

    def estimate_transition(self, prithvi_results):
        before = prithvi_results.get("before", {})
        after = prithvi_results.get("after", {})
        if not before or not after:
            return "unknown"

        dominant_before = max(before, key=before.get)
        dominant_after = max(after, key=after.get)
        return f"{dominant_before} → {dominant_after}"

    def build_evidence_item(
        self,
        source,
        finding,
        confidence,
        details,
    ):
        return {
            "source": source,
            "finding": finding,
            "confidence": round(float(confidence), 2),
            "details": details,
        }

    def _load_prithvi_dynamic_world_alignment(self, output_paths):
        segmask_path = output_paths.get("segmask_after")
        dynamic_world_path = output_paths.get("dynamic_world_after")

        if not segmask_path or not dynamic_world_path:
            return None

        segmask_path = Path(segmask_path)
        dynamic_world_path = Path(dynamic_world_path)

        if not segmask_path.exists() or not dynamic_world_path.exists():
            return None

        prithvi_mask = np.load(segmask_path)
        with rasterio.open(dynamic_world_path) as src:
            dynamic_world_mask = src.read(1)

        dynamic_world_mask = cv2.resize(
            dynamic_world_mask.astype(np.uint8),
            (prithvi_mask.shape[1], prithvi_mask.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )

        mapped_prithvi = np.full_like(prithvi_mask, 255, dtype=np.uint8)
        reverse_mapping = {
            3: "water",
            4: "trees",
            6: "crops",
            1: "built_area",
            2: "built_area",
            5: "bare_ground",
        }

        for class_id, dynamic_world_name in reverse_mapping.items():
            mapped_prithvi[prithvi_mask == class_id] = self.dynamic_world_ids[dynamic_world_name]

        valid = mapped_prithvi != 255
        if not np.any(valid):
            return None

        agreement = (mapped_prithvi == dynamic_world_mask) & valid
        agreement_score = round(float(np.mean(agreement[valid]) * 100), 2)

        return {
            "agreement_mask": agreement,
            "mapped_prithvi": mapped_prithvi,
            "dynamic_world_mask": dynamic_world_mask,
            "valid_mask": valid,
            "agreement_score": agreement_score,
        }

    def _save_maps(
        self,
        output_paths,
        alignment,
        changestar_results,
        prithvi_results,
        preprocessing_results,
    ):
        probability_path = changestar_results.get("probability_map")
        confidence_path = output_paths.get("prithvi_after_confidence_npy")

        if probability_path and Path(probability_path).exists():
            change_prob = np.load(probability_path)
        else:
            change_prob = None

        if confidence_path and Path(confidence_path).exists():
            segmentation_confidence = np.load(confidence_path)
        else:
            segmentation_confidence = None

        if alignment is not None:
            agreement_visual = np.zeros(
                alignment["agreement_mask"].shape + (3,),
                dtype=np.uint8,
            )
            agreement_visual[alignment["valid_mask"]] = (0, 0, 255)
            agreement_visual[alignment["agreement_mask"]] = (0, 200, 0)
            cv2.imwrite(
                str(output_paths["agreement_map"]),
                agreement_visual,
            )

        if change_prob is not None:
            evidence_map = change_prob

            if segmentation_confidence is not None:
                segmentation_confidence = cv2.resize(
                    segmentation_confidence.astype(np.float32),
                    (change_prob.shape[1], change_prob.shape[0]),
                    interpolation=cv2.INTER_LINEAR,
                )
                evidence_map = 0.55 * evidence_map + 0.45 * segmentation_confidence

            if alignment is not None:
                agreement_resized = cv2.resize(
                    alignment["agreement_mask"].astype(np.float32),
                    (change_prob.shape[1], change_prob.shape[0]),
                    interpolation=cv2.INTER_NEAREST,
                )
                evidence_map = 0.7 * evidence_map + 0.3 * agreement_resized

            evidence_visual = np.clip(evidence_map * 255.0, 0, 255).astype(np.uint8)
            cv2.imwrite(str(output_paths["evidence_map"]), evidence_visual)

            uncertainty_map = 1.0 - evidence_map

            cloud_average = preprocessing_results.get("cloud_fraction", {}).get("average", 0.0)
            uncertainty_map = np.clip(
                uncertainty_map + (cloud_average / 100.0) * 0.15,
                0.0,
                1.0,
            )
            uncertainty_visual = np.clip(uncertainty_map * 255.0, 0, 255).astype(np.uint8)
            cv2.imwrite(str(output_paths["uncertainty_map"]), uncertainty_visual)

    def fuse(
        self,
        prithvi_results,
        dynamic_world_results,
        changestar_results,
        ssim_results,
        grounding_dino_results,
        semantic_results,
        osint_results,
        reliability_results,
        output_paths=None,
        preprocessing_results=None,
    ):
        output_paths = output_paths or {}
        preprocessing_results = preprocessing_results or {}
        evidence_items = []

        dominant_prithvi, prithvi_percentage = self.get_dominant_prithvi(prithvi_results)
        dominant_dw, dw_percentage = self.get_dominant_dynamic_world(dynamic_world_results)
        mapped_prithvi = self.class_mapping.get(dominant_prithvi, dominant_prithvi)

        alignment = self._load_prithvi_dynamic_world_alignment(output_paths)
        pixel_agreement = alignment["agreement_score"] if alignment is not None else 0.0
        dominant_agreement = 100.0 if mapped_prithvi == dominant_dw else 25.0

        cloud_fraction = preprocessing_results.get("cloud_fraction", {}).get("average", 0.0)
        water_fraction = preprocessing_results.get("water_fraction", {}).get("average", 0.0)
        image_quality = preprocessing_results.get("image_quality", {})

        segmentation_confidence = float(
            prithvi_results.get("confidence_summary", {}).get("after_average_confidence", 0.0)
        )
        segmentation_uncertainty = float(
            prithvi_results.get("confidence_summary", {}).get("after_average_uncertainty", 100.0)
        )

        object_stats = grounding_dino_results.get("statistics", {})
        detection_confidence = float(
            object_stats.get("overall_average_confidence", 0.0)
        )
        new_objects = object_stats.get("new_objects", {})

        change_percentage = float(changestar_results.get("change_percentage", 0.0))
        structural_stats = changestar_results.get("statistics", {})
        raw_change = float(changestar_results.get("raw_change_percentage", change_percentage))
        ssim_change = float(ssim_results.get("change_percentage", 0.0))
        change_support = max(0.0, 100.0 - abs(change_percentage - ssim_change) * 3.0)

        evidence_items.append(
            self.build_evidence_item(
                "Prithvi EO 2.0",
                f"Dominant land-cover: {dominant_prithvi}",
                max(segmentation_confidence / 100.0, 0.01),
                {
                    "class": dominant_prithvi,
                    "coverage_percentage": round(prithvi_percentage, 2),
                    "average_confidence": segmentation_confidence,
                    "average_uncertainty": segmentation_uncertainty,
                },
            )
        )
        evidence_items.append(
            self.build_evidence_item(
                "Dynamic World",
                f"Dominant land-cover: {dominant_dw}",
                max(dw_percentage / 100.0, 0.01),
                {
                    "class": dominant_dw,
                    "coverage_percentage": round(dw_percentage, 2),
                    "pixel_agreement": pixel_agreement,
                },
            )
        )
        evidence_items.append(
            self.build_evidence_item(
                "ChangeStar2",
                f"{change_percentage:.2f}% structural change detected",
                max(float(changestar_results.get("confidence", 0.0)), 0.01),
                {
                    "change_percentage": round(change_percentage, 2),
                    "raw_change_percentage": round(raw_change, 2),
                    "statistics": structural_stats,
                },
            )
        )
        evidence_items.append(
            self.build_evidence_item(
                "Grounding DINO",
                f"{object_stats.get('total_after', 0)} objects detected in the latest observation",
                max(detection_confidence, 0.01),
                {
                    "before_count": object_stats.get("total_before", 0),
                    "after_count": object_stats.get("total_after", 0),
                    "new_objects": new_objects,
                    "before_objects": grounding_dino_results.get("before", []),
                    "after_objects": grounding_dino_results.get("after", []),
                },
            )
        )
        evidence_items.append(
            self.build_evidence_item(
                "SSIM",
                f"{ssim_change:.2f}% pixel-level change detected",
                max(change_support / 100.0, 0.01),
                {
                    "change_percentage": round(ssim_change, 2),
                    "ignored_percentage": ssim_results.get("ignored_percentage", 0.0),
                },
            )
        )

        validated_evidence = self.evidence_validator.validate(evidence_items)
        reasoned_evidence = self.evidence_reasoner.reason(
            copy.deepcopy(validated_evidence),
            semantic_results,
            changestar_results,
        )

        evidence_reliability_score = round(
            float(reliability_results.get("overall").score * 100)
            if reliability_results.get("overall") else 0.0,
            2,
        )

        object_change_corroboration = 100.0 if change_percentage > 1.0 and new_objects else 45.0
        environmental_penalty = min(35.0, (cloud_fraction * 0.6) + (water_fraction * 0.25))

        agreement_score = round(
            (
                0.40 * dominant_agreement
                + 0.35 * pixel_agreement
                + 0.25 * object_change_corroboration
            ),
            2,
        )

        contradiction_matrix = {
            "prithvi_vs_dynamic_world": round(100.0 - pixel_agreement, 2),
            "changestar_vs_ssim": round(max(0.0, 100.0 - change_support), 2),
            "objects_vs_change": round(0.0 if object_change_corroboration >= 80.0 else 55.0, 2),
        }

        agreement_matrix = {
            "prithvi_vs_dynamic_world": pixel_agreement,
            "changestar_vs_ssim": round(change_support, 2),
            "objects_vs_change": round(object_change_corroboration, 2),
        }

        overall_evidence_score = round(
            max(
                0.0,
                (
                    0.28 * agreement_score
                    + 0.22 * evidence_reliability_score
                    + 0.20 * segmentation_confidence
                    + 0.15 * (detection_confidence * 100.0)
                    + 0.15 * max(0.0, 100.0 - environmental_penalty)
                ),
            ),
            2,
        )

        model_agreement_score = round(
            max(
                0.0,
                min(
                    100.0,
                    (
                        0.45 * agreement_score
                        + 0.20 * change_support
                        + 0.20 * evidence_reliability_score
                        + 0.15 * max(0.0, 100.0 - environmental_penalty)
                    ),
                ),
            ),
            2,
        )

        if model_agreement_score >= 85:
            assessment = "Very High agreement"
        elif model_agreement_score >= 70:
            assessment = "High agreement"
        elif model_agreement_score >= 55:
            assessment = "Moderate agreement"
        else:
            assessment = "Low agreement"

        conflicts = []
        if mapped_prithvi != dominant_dw:
            conflicts.append(
                f"Prithvi predicts '{dominant_prithvi}' while Dynamic World predicts '{dominant_dw}'."
            )
        if cloud_fraction > 8:
            conflicts.append("Cloud contamination may influence apparent surface change.")
        if water_fraction > 15:
            conflicts.append("Water presence may inflate shoreline or tidal variability.")
        if abs(change_percentage - ssim_change) > 8:
            conflicts.append("Structural change and pixel-level change diverge materially.")

        severity = "Low"
        if change_percentage >= 20:
            severity = "High"
        elif change_percentage >= 8:
            severity = "Moderate"

        transition = self.estimate_transition(prithvi_results)
        mission_change = round((change_percentage + ssim_change) / 2.0, 2)

        mission_summary = (
            f"GeoSentinel detected {severity.lower()} structural change "
            f"({change_percentage:.2f}%) with an evidence score of "
            f"{overall_evidence_score:.2f}%. "
            f"Model agreement is {model_agreement_score:.2f}% after accounting for "
            f"cloud cover ({cloud_fraction:.2f}%) and water influence ({water_fraction:.2f}%)."
        )

        fused = {
            "mission_summary": mission_summary,
            "summary": (
                f"Prithvi detected {dominant_prithvi} ({prithvi_percentage:.2f}%). "
                f"Dynamic World detected {dominant_dw} ({dw_percentage:.2f}%). "
                f"Structural change is {change_percentage:.2f}% and pixel-level change is {ssim_change:.2f}%."
            ),
            "assessment": assessment,
            "agreement": mapped_prithvi == dominant_dw,
            "agreement_score": agreement_score,
            "model_agreement_score": model_agreement_score,
            "overall_evidence_score": overall_evidence_score,
            "dominant_prithvi": dominant_prithvi,
            "dominant_dynamic_world": dominant_dw,
            "estimated_transition": transition,
            "structural_change": change_percentage,
            "ssim_change_percentage": ssim_change,
            "change_percentage": mission_change,
            "change_severity": severity,
            "conflicts": conflicts,
            "agreement_matrix": agreement_matrix,
            "contradiction_matrix": contradiction_matrix,
            "evidence_reliability_score": evidence_reliability_score,
            "confidence_breakdown": {
                "segmentation_confidence": round(segmentation_confidence, 2),
                "detection_confidence": round(detection_confidence * 100.0, 2),
                "change_confidence": round(float(changestar_results.get("confidence", 0.0)) * 100.0, 2),
                "image_quality": round(image_quality.get("valid_fraction", 0.0), 2),
                "cloud_percentage": round(cloud_fraction, 2),
                "water_percentage": round(water_fraction, 2),
                "spatial_consistency": round(pixel_agreement, 2),
                "temporal_consistency": round(change_support, 2),
            },
            "evidence": {
                "prithvi": {
                    "dominant_class": dominant_prithvi,
                    "percentage": round(prithvi_percentage, 2),
                },
                "dynamic_world": {
                    "dominant_class": dominant_dw,
                    "percentage": round(dw_percentage, 2),
                },
                "changestar": {
                    "change_percentage": round(change_percentage, 2),
                    "statistics": structural_stats,
                },
                "grounding_dino": {
                    "before_objects": grounding_dino_results.get("before", []),
                    "after_objects": grounding_dino_results.get("after", []),
                    "before_count": object_stats.get("total_before", 0),
                    "after_count": object_stats.get("total_after", 0),
                },
            },
            "validated_evidence": validated_evidence,
            "reasoned_evidence": reasoned_evidence,
            "land_cover_evidence": {
                "prithvi": {
                    "dominant_class": dominant_prithvi,
                    "coverage": round(prithvi_percentage, 2),
                },
                "dynamic_world": {
                    "dominant_class": dominant_dw,
                    "coverage": round(dw_percentage, 2),
                },
                "agreement": mapped_prithvi == dominant_dw,
                "pixel_agreement": pixel_agreement,
            },
            "object_evidence": {
                "statistics": object_stats,
                "before": grounding_dino_results.get("before", []),
                "after": grounding_dino_results.get("after", []),
            },
            "change_evidence": {
                "change_percentage": round(change_percentage, 2),
                "raw_change_percentage": round(raw_change, 2),
                "severity": severity,
                "transition": transition,
                "statistics": structural_stats,
            },
            "osint_evidence": osint_results if osint_results else {},
            "reliability": reliability_results,
            "preprocessing": preprocessing_results,
        }

        if output_paths:
            self._save_maps(
                output_paths,
                alignment,
                changestar_results,
                prithvi_results,
                preprocessing_results,
            )
            with open(output_paths["model_agreement_json"], "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "agreement_matrix": agreement_matrix,
                        "contradiction_matrix": contradiction_matrix,
                        "model_agreement_score": model_agreement_score,
                    },
                    handle,
                    indent=4,
                )
            with open(output_paths["fusion_json"], "w", encoding="utf-8") as handle:
                json.dump(fused, handle, indent=4, default=str)

        return fused
