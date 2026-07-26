import os
import subprocess
import cv2
import numpy as np
import sys

from backend.models.changeformer.tile_generator import generate_tiles
from backend.models.changeformer.tile_stitcher import stitch_tiles

from intelligence.evidence import Evidence


class ChangeFormerModel:
    """
    Wrapper around the ChangeFormer model.

    Responsibilities
    ----------------
    - Generate image tiles
    - Run ChangeFormer inference
    - Stitch predicted tiles
    - Compute change percentage
    - Return analysis results
    - Convert results into Evidence objects
    """

    def __init__(self):

        print("\nLoading ChangeFormer Module...")

        self.changeformer_root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../ChangeFormer"
            )
        )

    # ==========================================================
    # Main Analysis
    # ==========================================================

    def analyze_images(
        self,
        before_image,
        after_image
    ):

        print("\nRunning ChangeFormer Analysis...")

        temp_dataset = os.path.join(
            self.changeformer_root,
            "temp_dataset"
        )

        print("\nGenerating ChangeFormer tile dataset...")

        tile_info = generate_tiles(
            before_image_path=before_image,
            after_image_path=after_image,
            output_dataset_dir=temp_dataset,
            tile_size=256,
            stride=256
        )

        print(
            f"\nPrepared {tile_info['tiles']} paired tiles for ChangeFormer."
        )

        subprocess.run(
            [
                sys.executable,
                "demo_LEVIR.py",
                "--data_name",
                "temp_dataset"
            ],
            cwd=self.changeformer_root,
            check=True
        )

        prediction_folder = os.path.join(
            self.changeformer_root,
            "samples_LEVIR",
            "predict_CD_ChangeFormerV6"
        )

        output_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../outputs"
            )
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        stitched_mask = os.path.join(
            output_dir,
            "changeformer_result.png"
        )

        print("\n==============================")
        print("TILE INFO")
        print("==============================")
        print(tile_info)
        print("==============================")

        stitch_tiles(
            prediction_folder=prediction_folder,
            output_path=stitched_mask,
            image_width=tile_info["width"],
            image_height=tile_info["height"],
            tile_size=tile_info["tile_size"]
        )

        mask = cv2.imread(
            stitched_mask,
            cv2.IMREAD_GRAYSCALE
        )

        if mask is None:
            raise RuntimeError(
                "Failed to load stitched ChangeFormer mask."
            )

        white_pixels = np.sum(mask > 0)

        total_pixels = (
            mask.shape[0] *
            mask.shape[1]
        )

        change_percentage = (
            white_pixels /
            total_pixels
        ) * 100

        cv2.imwrite(
            stitched_mask,
            mask
        )

        findings = {

            "change_percentage":
                float(
                    round(
                        change_percentage,
                        2
                    )
                ),

            "mask_path":
                stitched_mask,

            "status":
                "success"

        }

        return findings

    # ==========================================================
    # Intelligence Integration
    # ==========================================================

    def generate_evidence(
        self,
        findings
    ):
        """
        Convert ChangeFormer findings into Evidence objects.
        """

        evidence = []

        change_percentage = findings.get(
            "change_percentage",
            0.0
        )

        confidence = min(
            max(
                change_percentage / 100.0,
                0.10
            ),
            1.0
        )

        description = (
            f"Detected {change_percentage:.2f}% structural change."
        )

        evidence.append(

            Evidence(

                source="ChangeStar",

                category="Change Detection",

                confidence=confidence,

                importance=1.0,

                description=description,

                metadata={

                    "change_percentage":
                        change_percentage,

                    "mask_path":
                        findings.get(
                            "mask_path"
                        ),

                    "status":
                        findings.get(
                            "status"
                        )

                }

            )

        )

        return evidence