from backend.models.grounding_dino.grounding_dino_model import (
    GroundingDINOModel,
)

from collections import Counter


class GroundingDINOEngine:
    """
    High-level orchestration for Grounding DINO.

    Responsibilities
    ----------------
    • Run inference on BEFORE and AFTER images
    • Save annotated images
    • Save detection JSON
    • Return detections to the GeoSentinel pipeline
    """

    def __init__(self):

        self.model = GroundingDINOModel()

    def _run_single_image(
        self,
        image_path,
        annotated_output,
        json_output,
        aoi_type="default",
    ):

        detections = self.model.predict(
            image_path=image_path,
            aoi_type=aoi_type,
        )

        self.model.save_annotated_image(
            image_path=image_path,
            detections=detections,
            output_path=annotated_output,
        )

        self.model.save_detections_json(
            detections=detections,
            output_path=json_output,
        )

        return detections

    def compare_images(
        self,
        before_image,
        after_image,
        before_output,
        after_output,
        before_json,
        after_json,
        statistics_output=None,
        aoi_type="default",
    ):

        before_results = self._run_single_image(
            image_path=before_image,
            annotated_output=before_output,
            json_output=before_json,
            aoi_type=aoi_type,
        )

        after_results = self._run_single_image(
            image_path=after_image,
            annotated_output=after_output,
            json_output=after_json,
            aoi_type=aoi_type,
        )

        statistics = self._compute_statistics(
            before_results,
            after_results,
            aoi_type=aoi_type,
        )

        if statistics_output is not None:
            self.model.save_detections_json(
                detections=statistics,
                output_path=statistics_output,
            )

        return {
            "before": before_results,
            "after": after_results,
            "statistics": statistics,
        }
    
    def _compute_statistics(
        self,
        before_results,
        after_results,
        aoi_type="default",
    ):
        """
        Compute object statistics for before/after detections.
        """

        before_counts = Counter(
            det["label"] for det in before_results
        )

        after_counts = Counter(
            det["label"] for det in after_results
        )

        all_labels = sorted(
            set(before_counts.keys()) |
            set(after_counts.keys())
        )

        differences = {}

        for label in all_labels:
            differences[label] = (
                after_counts.get(label, 0)
                - before_counts.get(label, 0)
            )

        all_detections = before_results + after_results
        overall_average_confidence = 0.0

        if all_detections:
            overall_average_confidence = sum(
                det["confidence"] for det in all_detections
            ) / len(all_detections)

        new_objects = {
            label: diff
            for label, diff in differences.items()
            if diff > 0
        }
        disappeared_objects = {
            label: abs(diff)
            for label, diff in differences.items()
            if diff < 0
        }

        return {
            "before_counts": dict(before_counts),
            "after_counts": dict(after_counts),
            "differences": differences,
            "total_before": len(before_results),
            "total_after": len(after_results),
            "overall_average_confidence": round(
                overall_average_confidence,
                4,
            ),
            "before_average_confidence": round(
                (
                    sum(det["confidence"] for det in before_results)
                    / len(before_results)
                )
                if before_results else 0.0,
                4,
            ),
            "after_average_confidence": round(
                (
                    sum(det["confidence"] for det in after_results)
                    / len(after_results)
                )
                if after_results else 0.0,
                4,
            ),
            "new_objects": new_objects,
            "disappeared_objects": disappeared_objects,
            "aoi_type": aoi_type,
            "prompt": self.model.last_prompt,
        }