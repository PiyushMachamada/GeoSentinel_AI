import os
import json

import cv2
import torch

from PIL import Image
from collections import Counter

from torchvision.ops import nms
from .prompts import PROMPTS, THRESHOLDS

from transformers import (
    AutoProcessor,
    AutoModelForZeroShotObjectDetection,
)


class GroundingDINOModel:
    """
    Wrapper for Hugging Face Grounding DINO.

    Responsibilities
    ----------------
    - Load model
    - Run object detection
    - Apply post-processing
    - Save annotated images
    - Export detections as JSON
    """

    MODEL_NAME = "IDEA-Research/grounding-dino-base"

    def __init__(self):

        print("\n==========================================")
        print("Loading Grounding DINO...")
        print("==========================================")

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print(f"Using device: {self.device}")

        self.processor = AutoProcessor.from_pretrained(
            self.MODEL_NAME
        )

        self.model = (
            AutoModelForZeroShotObjectDetection
            .from_pretrained(
                self.MODEL_NAME
            )
        )

        self.model.to(self.device)
        self.model.eval()

        # Cached metadata from the last prediction
        self.last_scene_confidence = 0.0
        self.last_class_counts = {}
        self.last_aoi_type = None
        self.last_prompt = None

        print("✓ Grounding DINO loaded successfully.")

    # ======================================================
    # Detection
    # ======================================================

    def predict(
        self,
        image_path,
        aoi_type="default",
        text_prompt=None,
        box_threshold=None,
        text_threshold=None,
        min_box_size=20,
        max_detections=50,
    ):
        """
        Detect objects in an image.

        Returns
        -------
        list(dict)
        """

        if text_prompt is None:
            text_prompt = PROMPTS.get(
                aoi_type,
                PROMPTS["default"],
            )

        if (
            box_threshold is None
            or
            text_threshold is None
        ):
            box_threshold, text_threshold = THRESHOLDS.get(
                aoi_type,
                THRESHOLDS["default"],
            )

        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            images=image,
            text=text_prompt,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        results = (
            self.processor
            .post_process_grounded_object_detection(

                outputs,

                input_ids=inputs.input_ids,

                threshold=box_threshold,

                text_threshold=text_threshold,

                target_sizes=[image.size[::-1]],

            )[0]
        )

        detections = []

        boxes = results["boxes"]
        scores = results["scores"]
        labels = results["text_labels"]

        for box, score, label in zip(
            boxes,
            scores,
            labels,
        ):

            x1, y1, x2, y2 = box.tolist()

            width = x2 - x1
            height = y2 - y1

            # Ignore tiny detections

            if (
                width < min_box_size
                or
                height < min_box_size
            ):
                continue

            detections.append(

                {
                    "label": str(label),

                    "confidence": float(score),

                    "bbox": [
                        float(x1),
                        float(y1),
                        float(x2),
                        float(y2),
                    ],
                }

            )

        # Highest confidence first

        detections.sort(

            key=lambda x: x["confidence"],

            reverse=True,

        )

        detections = self._apply_nms(
            detections,
            iou_threshold=0.5,
        )

        detections = detections[:max_detections]

        counts = Counter(
            det["label"]
            for det in detections
        )

        print("\nDetected Classes")

        for label, count in counts.items():
            print(f"{label:<25} {count}")

        print("\n==========================================")
        print("Grounding DINO Summary")
        print("==========================================")
        print(f"AOI Type          : {aoi_type}")
        prompt_length = len(
            [p for p in text_prompt.split(".") if p.strip()]
        )

        print(f"Prompt Length     : {prompt_length}")
        print(f"Box Threshold     : {box_threshold}")
        print(f"Text Threshold    : {text_threshold}")
        print(f"Objects Detected  : {len(detections)}")

        scene_confidence = 0.0

        if detections:

            print("\nTop Detections")

            for det in detections[:10]:
                print(
                    f"- {det['label']} "
                    f"({det['confidence']:.2f})"
                )

            scene_confidence = (
                sum(d["confidence"] for d in detections)
                / len(detections)
            )

        print(f"Average Confidence : {scene_confidence:.2f}")

        self.last_scene_confidence = scene_confidence
        self.last_class_counts = dict(counts)
        self.last_aoi_type = aoi_type
        self.last_prompt = text_prompt

        return detections
    
        # ======================================================
    # Non-Maximum Suppression
    # ======================================================

    def _apply_nms(
        self,
        detections,
        iou_threshold=0.5,
    ):
        """
        Remove duplicate detections using class-wise
        Non-Maximum Suppression.
        """

        if not detections:
            return detections

        filtered_detections = []

        labels = sorted(
            set(det["label"] for det in detections)
        )

        for label in labels:

            class_detections = [

                det

                for det in detections

                if det["label"] == label

            ]

            boxes = torch.tensor(

                [
                    det["bbox"]
                    for det in class_detections
                ],

                dtype=torch.float32,

            )

            scores = torch.tensor(

                [
                    det["confidence"]
                    for det in class_detections
                ],

                dtype=torch.float32,

            )

            keep = nms(

                boxes,

                scores,

                iou_threshold,

            )

            for idx in keep:

                filtered_detections.append(

                    class_detections[idx.item()]

                )

        filtered_detections.sort(

            key=lambda x: x["confidence"],

            reverse=True,

        )

        return filtered_detections

    # ======================================================
    # Save Annotated Image
    # ======================================================

    def save_annotated_image(
        self,
        image_path,
        detections,
        output_path,
    ):
        """
        Draw detections and labels on the image.
        """

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        height, width = image.shape[:2]

        for det in detections:

            x1, y1, x2, y2 = det["bbox"]

            x1 = max(0, min(int(x1), width - 1))
            y1 = max(0, min(int(y1), height - 1))
            x2 = max(0, min(int(x2), width - 1))
            y2 = max(0, min(int(y2), height - 1))

            label = det["label"]

            confidence = det["confidence"]

            # Bounding box

            cv2.rectangle(

                image,

                (x1, y1),

                (x2, y2),

                (0, 255, 0),

                2,

            )

            text = f"{label} ({confidence:.2f})"

            (text_width, text_height), _ = cv2.getTextSize(

                text,

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                2,

            )

            # Label background

            cv2.rectangle(

                image,

                (x1, max(0, y1 - text_height - 10)),

                (x1 + text_width + 8, y1),

                (0, 255, 0),

                -1,

            )

            # Label text

            cv2.putText(

                image,

                text,

                (x1 + 4, y1 - 5),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 0, 0),

                2,

            )

        output_dir = os.path.dirname(output_path)

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True,
            )

        cv2.imwrite(
            output_path,
            image,
        )

        print(
            f"Annotated image saved:\n{output_path}"
        )

        return output_path

    # ======================================================
    # Save JSON
    # ======================================================

    def save_detections_json(
        self,
        detections,
        output_path,
    ):
        """
        Save detections to JSON.
        """

        output_dir = os.path.dirname(output_path)

        if output_dir:

            os.makedirs(
                output_dir,
                exist_ok=True,
            )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(

                detections,

                f,

                indent=4,

                ensure_ascii=False,

            )

        print(
            f"Detections JSON saved:\n{output_path}"
        )

        return output_path