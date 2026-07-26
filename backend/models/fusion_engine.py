from backend.models.evidence_validation import EvidenceValidator
from backend.models.evidence_reasoning import EvidenceReasoner
import copy


class FusionEngine:

    def __init__(self):

        print("\n" + "=" * 60)
        print("Loading GeoSentinel Fusion Engine")
        print("=" * 60)

        # Mapping between Prithvi classes and Dynamic World classes
        self.class_mapping = {
            "forest": "trees",
            "river": "water",
            "agricultural_area": "crops",
            "residential_area": "built_area",
            "unused_land": "bare_ground",
            "road": "built_area",
            "background": "unknown"
        }

        self.evidence_validator = EvidenceValidator()
        self.evidence_reasoner = EvidenceReasoner()

    # ==========================================================
    # Get dominant Dynamic World class
    # ==========================================================

    def get_dominant_dynamic_world(self, dynamic_world_results):

        after = {}

        for cls, values in dynamic_world_results.items():

            after[cls] = values.get("after", 0)

        dominant = max(after, key=after.get)

        return dominant, after[dominant]

    # ==========================================================
    # Get dominant Prithvi class
    # ==========================================================

    def get_dominant_prithvi(self, prithvi_results):

        after = prithvi_results["after"]

        dominant = max(after, key=after.get)

        return dominant, after[dominant]

    # ==========================================================
    # Estimate land-cover transition
    # ==========================================================

    def estimate_transition(self, prithvi_results):

        before = prithvi_results["before"]
        after = prithvi_results["after"]

        dominant_before = max(before, key=before.get)
        dominant_after = max(after, key=after.get)

        return f"{dominant_before} → {dominant_after}"
    
    # ==========================================================
    # Standardize Evidence
    # ==========================================================

    def build_evidence_item(
        self,
        source,
        finding,
        confidence,
        details,
    ):
        """
        Create a standardized evidence object that every model
        contributes to.
        """

        return {
            "source": source,
            "finding": finding,
            "confidence": round(float(confidence), 2),
            "details": details,
        }

    # ==========================================================
    # Main Fusion Function
    # ==========================================================

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
    ):
        fused = {}

        evidence_items = []

        # --------------------------------------------------
        # Dominant classes
        # --------------------------------------------------

        dominant_prithvi, prithvi_percentage = (
            self.get_dominant_prithvi(
                prithvi_results
            )
        )

        evidence_items.append(

            self.build_evidence_item(

                source="Prithvi EO 2.0",

                finding=f"Dominant land-cover: {dominant_prithvi}",

                confidence=prithvi_percentage / 100,

                details={

                    "class": dominant_prithvi,

                    "coverage_percentage": round(prithvi_percentage, 2)

                }

            )

        )

        dominant_dw, dw_percentage = (
            self.get_dominant_dynamic_world(
                dynamic_world_results
            )
        )

        evidence_items.append(

            self.build_evidence_item(

                source="Dynamic World",

                finding=f"Dominant land-cover: {dominant_dw}",

                confidence=dw_percentage / 100,

                details={

                    "class": dominant_dw,

                    "coverage_percentage": round(dw_percentage, 2)

                }

            )

        )

        mapped_prithvi = self.class_mapping.get(
            dominant_prithvi,
            dominant_prithvi
        )

        agreement = (
            mapped_prithvi == dominant_dw
        )

        difference = abs(
            prithvi_percentage -
            dw_percentage
        )

        if agreement:

            agreement_score = max(
                100 - difference,
                70
            )

        else:

            agreement_score = max(
                70 - difference,
                20
            )

        agreement_score = round(
            agreement_score,
            2
        )

        # --------------------------------------------------
        # ChangeStar2
        # --------------------------------------------------

        change_percentage = float(

            changestar_results.get(
                "change_percentage",
                0
            )

        )

        # Pixel-level change from SSIM
        ssim_change = float(
            ssim_results.get(
                "change_percentage",
                0
            )
        )

        # Combined mission change estimate
        mission_change = round(
            (change_percentage + ssim_change) / 2,
            2,
        )

        evidence_items.append(

          self.build_evidence_item(

            source="ChangeStar2",

            finding=f"{change_percentage:.2f}% structural change detected",

            confidence=min(change_percentage / 20, 1.0),

            details={
                "change_percentage": round(change_percentage, 2)
            }

          )

       )

        if change_percentage < 5:

            severity = "Low"

        elif change_percentage < 20:

            severity = "Moderate"

        else:

            severity = "High"

        # --------------------------------------------------
        # model_agreement_score Score
        # --------------------------------------------------

        model_agreement_score = min(
            round(
                (
                    agreement_score * 0.60
                    +
                    min(change_percentage, 100) * 0.40
                ),
                2
            ),
            100
        )

        # --------------------------------------------------
        # Transition
        # --------------------------------------------------

        transition = self.estimate_transition(
            prithvi_results
        )

        # --------------------------------------------------
        # Conflict Detection
        # --------------------------------------------------

        conflicts = []

        if not agreement:

                    conflicts.append(
                        f"Prithvi predicts '{dominant_prithvi}' "
                        f"while Dynamic World predicts '{dominant_dw}'."
                    )

        if difference > 25:

                    conflicts.append(
                        "Large disagreement in land-cover percentages."
                    )

        before_count = len(
            grounding_dino_results.get("before", [])
        )

        after_count = len(
            grounding_dino_results.get("after", [])
        )   

        evidence_items.append(

            self.build_evidence_item(

                source="Grounding DINO",

                finding=f"{after_count} objects detected in the latest observation",

                confidence=1.0,

                details={
                    "before_count": before_count,
                    "after_count": after_count,
                    "before_objects": grounding_dino_results.get("before", []),
                    "after_objects": grounding_dino_results.get("after", []),
                }

            )

        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        evidence = {

            "prithvi": {
                "dominant_class": dominant_prithvi,
                "percentage": round(prithvi_percentage, 2),
            },

            "dynamic_world": {
                "dominant_class": dominant_dw,
                "percentage": round(dw_percentage, 2),
            },

            "changestar": {
                "change_percentage": round(
                    change_percentage,
                    2,
                ),
            },

            "grounding_dino": {
                "before_objects": grounding_dino_results.get(
                    "before",
                    [],
                ),
                "after_objects": grounding_dino_results.get(
                    "after",
                    [],
                ),

                "before_count": before_count,
                "after_count": after_count,

            },

        }

        validated_evidence = self.evidence_validator.validate(evidence_items)

        reasoned_evidence = self.evidence_reasoner.reason(
            copy.deepcopy(validated_evidence),
            semantic_results,
            changestar_results,
        )
        # --------------------------------------------------
        # Overall Assessment
        # --------------------------------------------------

        if model_agreement_score >= 90:

            assessment = (
                "Very High agreement"
            )

        elif model_agreement_score >= 75:

            assessment = (
                "High agreement"
            )

        elif model_agreement_score >= 60:

            assessment = (
                "Moderate agreement"
            )

        else:

            assessment = (
                "Low agreement"
            )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        summary = (
            f"Prithvi detected "
            f"{dominant_prithvi} "
            f"({prithvi_percentage:.2f}%). "
            f"Dynamic World detected "
            f"{dominant_dw} "
            f"({dw_percentage:.2f}%). "
            f"Estimated structural change is "
            f"{change_percentage:.2f}%. "
            f"Overall model_agreement_score is "
            f"{model_agreement_score:.2f}%."
        )

        # --------------------------------------------------
        # Semantic Evidence Package
        # --------------------------------------------------

        land_cover_evidence = {
            "prithvi": {
                "dominant_class": dominant_prithvi,
                "coverage": round(prithvi_percentage, 2),
            },
            "dynamic_world": {
                "dominant_class": dominant_dw,
                "coverage": round(dw_percentage, 2),
            },
            "agreement": agreement,
        }

        object_statistics = grounding_dino_results.get("statistics", {})

        object_evidence = {
            "statistics": object_statistics,
            "before": grounding_dino_results.get("before", []),
            "after": grounding_dino_results.get("after", []),
        }

        change_evidence = {
            "change_percentage": round(change_percentage, 2),
            "severity": severity,
            "transition": transition,
        }

        osint_evidence = osint_results if osint_results else {}

        mission_summary = (
            f"GeoSentinel detected {severity.lower()} structural change "
            f"({change_percentage:.2f}%). "
            f"Dominant land cover is '{dominant_dw}' according to Dynamic World "
            f"and '{dominant_prithvi}' according to Prithvi."
        )

        # --------------------------------------------------
        # Final Object
        # --------------------------------------------------

        fused = {

            "mission_summary": mission_summary,

            "summary": summary,

            "assessment": assessment,

            "agreement": agreement,

            "agreement_score": agreement_score,

            "model_agreement_score": model_agreement_score,

            "dominant_prithvi": dominant_prithvi,

            "dominant_dynamic_world": dominant_dw,

            "estimated_transition": transition,

            "structural_change": change_percentage,

            "ssim_change_percentage": ssim_change,

            "change_percentage": mission_change,

            "change_severity": severity,

            "conflicts": conflicts,

            "evidence": evidence,

            "validated_evidence": validated_evidence,

            "reasoned_evidence": reasoned_evidence,

            "land_cover_evidence": land_cover_evidence,

            "object_evidence": object_evidence,

            "change_evidence": change_evidence,

            "osint_evidence": osint_evidence,

            "reliability": reliability_results,
        }

        return fused