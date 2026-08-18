from backend.models.grounding_dino.grounding_dino_model import (
    GroundingDINOModel,
)

from collections import Counter

import cv2
import numpy as np


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
        diff_output=None,
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

        if diff_output is not None:
            try:
                self._generate_diff_map(
                    before_image=before_image,
                    after_image=after_image,
                    before_results=before_results,
                    after_results=after_results,
                    output_path=diff_output,
                )
            except Exception as exc:
                print(f"[GroundingDINO] diff_map generation failed: {exc}")

        return {
            "before": before_results,
            "after": after_results,
            "statistics": statistics,
        }

    def _generate_diff_map(
        self,
        before_image,
        after_image,
        before_results,
        after_results,
        output_path,
    ):
        """
        Generate a side-by-side object change visualisation.

        Left panel  : BEFORE annotated image with disappeared objects
                      highlighted in red.
        Right panel : AFTER annotated image with new objects
                      highlighted in green.
        A thin black separator bar divides the panels, and a legend
        is drawn at the top.
        """

        before_img = cv2.imread(str(before_image))
        after_img = cv2.imread(str(after_image))

        if before_img is None or after_img is None:
            return

        h = 512
        w = 512

        before_img = cv2.resize(before_img, (w, h))
        after_img = cv2.resize(after_img, (w, h))

        before_counts = Counter(
            det["label"] for det in before_results
        )
        after_counts = Counter(
            det["label"] for det in after_results
        )

        all_labels = set(before_counts) | set(after_counts)

        disappeared = {
            lbl for lbl in all_labels
            if before_counts.get(lbl, 0) > after_counts.get(lbl, 0)
        }
        appeared = {
            lbl for lbl in all_labels
            if after_counts.get(lbl, 0) > before_counts.get(lbl, 0)
        }

        before_panel = before_img.copy()
        after_panel = after_img.copy()

        RED = (0, 0, 200)
        GREEN = (0, 200, 0)

        def _draw_boxes(panel, detections, highlight_labels, color):
            for det in detections:
                if det.get("label") in highlight_labels:
                    box = det.get("box")
                    if box and len(box) == 4:
                        x1 = int(box[0] * w)
                        y1 = int(box[1] * h)
                        x2 = int(box[2] * w)
                        y2 = int(box[3] * h)
                        cv2.rectangle(panel, (x1, y1), (x2, y2), color, 3)
                        label_text = det["label"]
                        cv2.putText(
                            panel, label_text,
                            (x1, max(y1 - 6, 12)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1,
                            cv2.LINE_AA,
                        )

        _draw_boxes(before_panel, before_results, disappeared, RED)
        _draw_boxes(after_panel, after_results, appeared, GREEN)

        sep = np.zeros((h, 6, 3), dtype=np.uint8)
        diff_map = np.concatenate([before_panel, sep, after_panel], axis=1)

        legend_height = 32
        legend = np.full((legend_height, diff_map.shape[1], 3), 30, dtype=np.uint8)

        cv2.putText(
            legend, "BEFORE  (red = disappeared)",
            (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 255), 1, cv2.LINE_AA,
        )
        cv2.putText(
            legend, "AFTER  (green = appeared)",
            (w + 16, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 220, 80), 1, cv2.LINE_AA,
        )

        diff_map = np.concatenate([legend, diff_map], axis=0)

        cv2.imwrite(str(output_path), diff_map)
        print(f"[GroundingDINO] Diff map saved: {output_path}")
    
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