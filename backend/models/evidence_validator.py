class EvidenceValidator:

    def validate(
        self,
        change_percentage,
        transition_results,
        dynamic_world_results,
        objects_detected,
    ):

        score = 0

        # -----------------------------------------
        # Change Evidence (25)
        # -----------------------------------------

        if change_percentage >= 20:

            score += 25

        elif change_percentage >= 10:

            score += 18

        elif change_percentage >= 5:

            score += 10

        # -----------------------------------------
        # Semantic Evidence (25)
        # -----------------------------------------

        if (
            isinstance(transition_results, dict)
            and len(transition_results) >= 3
        ):

            score += 25

        elif transition_results:

            score += 15

        # -----------------------------------------
        # Dynamic World (25)
        # -----------------------------------------

        if dynamic_world_results:

            score += 25

        # -----------------------------------------
        # Object Detection (25)
        # -----------------------------------------

        detections = []

        if isinstance(objects_detected, dict):

            detections.extend(
                objects_detected.get("before", [])
            )

            detections.extend(
                objects_detected.get("after", [])
            )

        if detections:

            avg_conf = sum(
                d["confidence"]
                for d in detections
            ) / len(detections)

            score += round(avg_conf * 25)

        # -----------------------------------------
        # Clamp
        # -----------------------------------------

        score = min(score, 100)

        if score >= 80:

            status = "HIGH"

        elif score >= 60:

            status = "MEDIUM"

        else:

            status = "LOW"

        return {

            "evidence_score": score,

            "agreement": status,

        }