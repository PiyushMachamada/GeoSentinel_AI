import cv2
import torch
import numpy as np
import ever as er

import albumentations as A
from albumentations.pytorch import ToTensorV2

from torchange.models.changen2 import (
    s9_init_s9c1_changestar_vitb_1x256
)


class ChangeStarModel:

    def __init__(self):

        print("\n==========================================")
        print("Loading ChangeStar2...")
        print("==========================================")

        self.device = er.auto_device()

        self.model = s9_init_s9c1_changestar_vitb_1x256()

        self.model.eval()

        self.model.to(self.device)

        self.preprocess = A.Compose(
            [
                A.Normalize(),
                ToTensorV2(),
            ],
            additional_targets={
                "image2": "image"
            },
        )

        print("✓ ChangeStar2 loaded successfully")
        print("Device:", self.device)

    def predict(
        self,
        before_path,
        after_path,
        output_paths,
    ):

        # -------------------------------------------------
        # Read images
        # -------------------------------------------------

        before = cv2.imread(before_path)
        after = cv2.imread(after_path)

        if before is None:
            raise FileNotFoundError(before_path)

        if after is None:
            raise FileNotFoundError(after_path)

        before = cv2.cvtColor(
            before,
            cv2.COLOR_BGR2RGB
        )

        after = cv2.cvtColor(
            after,
            cv2.COLOR_BGR2RGB
        )

        before = cv2.resize(
            before,
            (512, 512)
        )

        after = cv2.resize(
            after,
            (512, 512)
        )

        # -------------------------------------------------
        # Official preprocessing
        # -------------------------------------------------

        data = self.preprocess(
            image=before,
            image2=after,
        )

        before = data["image"]
        after = data["image2"]

        print("\nImage Shapes")
        print("Before:", before.shape)
        print("After :", after.shape)

        # -------------------------------------------------
        # Create (6,H,W) tensor
        # -------------------------------------------------

        inp = torch.cat(
            [before, after],
            dim=0
        )

        print("Model Input:", inp.shape)

        inp = inp.unsqueeze(0).to(self.device)

        print("\nRunning ChangeStar2 inference...")

        with torch.no_grad():

            output = self.model(inp)

        # -------------------------------------------------
        # Debug logits
        # -------------------------------------------------

        logits = (
            output.change_prediction
            .clone()
            .squeeze()
            .cpu()
            .numpy()
        )

        print("\nRAW LOGITS")
        print("------------------------------")
        print("Shape :", logits.shape)
        print("Min   :", logits.min())
        print("Max   :", logits.max())
        print("Mean  :", logits.mean())

        # -------------------------------------------------
        # Convert logits -> probabilities
        # -------------------------------------------------

        output.logit_to_prob_()

        change = (
            output.change_prediction
            .squeeze()
            .cpu()
            .numpy()
        )

        print("\nPrediction Statistics")
        print("------------------------------")
        print("Shape :", change.shape)
        print("Min   :", change.min())
        print("Max   :", change.max())
        print("Mean  :", change.mean())

        print("\nPercentiles")
        print("------------------------------")

        for p in [50, 75, 90, 95, 99, 99.5, 99.9]:
            print(f"{p:5.1f}% :", np.percentile(change, p))

        # -------------------------------------------------
        # Threshold
        # -------------------------------------------------

        threshold = 0.55

        binary = (change > threshold).astype(np.uint8)

        print("\nThreshold Statistics")
        print("------------------------------")
        print("Threshold      :", threshold)
        print("Changed Pixels :", binary.sum())
        print("Total Pixels   :", binary.size)

        change_percentage = binary.mean() * 100

        # -------------------------------------------------
        # Load original image
        # -------------------------------------------------

        original = cv2.imread(before_path)

        original = cv2.resize(
            original,
            (512, 512)
        )

        # -------------------------------------------------
        # Overlay
        # -------------------------------------------------

        overlay = original.copy()

        overlay[binary == 1] = (0, 0, 255)

        result = cv2.addWeighted(
            original,
            0.70,
            overlay,
            0.30,
            0,
        )

        mask_path = str(
            output_paths["changestar_prediction"]
        )

        cv2.imwrite(
            mask_path,
            result,
        )

        # -------------------------------------------------
        # Save probability map
        # -------------------------------------------------

        probability_path = str(
            output_paths["changestar_probability"]
        )

        np.save(
            probability_path,
            change,
        )

        print("Saved probability map:")
        print(probability_path)

        return {

            "change_percentage": float(change_percentage),

            "confidence": float(change.max()),

            "model": "ChangeStar2",

            "mask_path": mask_path,

            "probability_map": probability_path,

            "change_map": change,

            "binary_change_map": binary,

        }