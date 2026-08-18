import json
from pathlib import Path

import albumentations as A
import cv2
import ever as er
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from torchange.models.changen2 import (
    s9_init_s9c1_changestar_vitb_1x256,
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

    def _load_mask(self, mask_source, target_size):
        if mask_source is None:
            return np.zeros(target_size, dtype=np.uint8)

        if isinstance(mask_source, np.ndarray):
            mask = mask_source
        else:
            mask = cv2.imread(
                str(mask_source),
                cv2.IMREAD_GRAYSCALE,
            )
            if mask is None:
                return np.zeros(target_size, dtype=np.uint8)

        if mask.shape != target_size:
            mask = cv2.resize(
                mask,
                (target_size[1], target_size[0]),
                interpolation=cv2.INTER_NEAREST,
            )

        return (mask > 0).astype(np.uint8)

    def _adaptive_threshold(self, probability_map, valid_mask):
        valid_probabilities = probability_map[valid_mask > 0]
        if valid_probabilities.size == 0:
            return 0.55

        percentile_threshold = np.percentile(valid_probabilities, 92)
        otsu_ready = np.clip(valid_probabilities * 255.0, 0, 255).astype(np.uint8)
        otsu_threshold, _ = cv2.threshold(
            otsu_ready,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )
        otsu_threshold = otsu_threshold / 255.0
        threshold = float(np.clip((percentile_threshold + otsu_threshold) / 2.0, 0.45, 0.75))
        return threshold

    def _post_process(self, binary_map):
        binary_map = (binary_map > 0).astype(np.uint8) * 255
        opened = cv2.morphologyEx(
            binary_map,
            cv2.MORPH_OPEN,
            np.ones((3, 3), np.uint8),
        )
        closed = cv2.morphologyEx(
            opened,
            cv2.MORPH_CLOSE,
            np.ones((7, 7), np.uint8),
        )

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            closed,
            connectivity=8,
        )
        filtered = np.zeros_like(closed)

        for component_id in range(1, num_labels):
            area = stats[component_id, cv2.CC_STAT_AREA]
            if area >= 64:
                filtered[labels == component_id] = 255

        return (filtered > 0).astype(np.uint8)

    def _compute_change_statistics(
        self,
        probability_map,
        binary_map,
        cloud_mask,
        water_mask,
        before_segmentation=None,
        after_segmentation=None,
    ):
        total_pixels = binary_map.size
        cloud_only = (binary_map == 1) & (cloud_mask == 1)
        water_only = (binary_map == 1) & (water_mask == 1)
        valid_structural_mask = (
            (binary_map == 1)
            & (cloud_mask == 0)
            & (water_mask == 0)
        )

        urban_change = np.zeros_like(binary_map, dtype=bool)
        vegetation_change = np.zeros_like(binary_map, dtype=bool)

        if before_segmentation is not None and after_segmentation is not None:
            urban_classes = {1, 2}
            vegetation_classes = {4, 6}

            before_urban = np.isin(before_segmentation, list(urban_classes))
            after_urban = np.isin(after_segmentation, list(urban_classes))
            before_vegetation = np.isin(before_segmentation, list(vegetation_classes))
            after_vegetation = np.isin(after_segmentation, list(vegetation_classes))

            urban_change = valid_structural_mask & (before_urban | after_urban)
            vegetation_change = valid_structural_mask & (before_vegetation | after_vegetation)

        structural_probabilities = probability_map[valid_structural_mask]
        confidence = float(structural_probabilities.mean()) if structural_probabilities.size else float(probability_map.max())

        return {
            "raw_change_percentage": round(float(np.mean(binary_map) * 100), 2),
            "true_structural_change_percentage": round(float(np.mean(valid_structural_mask) * 100), 2),
            "cloud_only_change_percentage": round(float(np.mean(cloud_only) * 100), 2),
            "water_only_change_percentage": round(float(np.mean(water_only) * 100), 2),
            "urban_change_percentage": round(float(np.mean(urban_change) * 100), 2),
            "vegetation_change_percentage": round(float(np.mean(vegetation_change) * 100), 2),
            "changed_pixels": int(binary_map.sum()),
            "structural_pixels": int(valid_structural_mask.sum()),
            "cloud_pixels": int(cloud_only.sum()),
            "water_pixels": int(water_only.sum()),
            "total_pixels": int(total_pixels),
            "confidence": round(confidence, 4),
        }

    def predict(
        self,
        before_path,
        after_path,
        output_paths,
        cloud_mask_path=None,
        water_mask_path=None,
        before_segmentation_path=None,
        after_segmentation_path=None,
    ):
        before = cv2.imread(str(before_path))
        after = cv2.imread(str(after_path))

        if before is None:
            raise FileNotFoundError(before_path)
        if after is None:
            raise FileNotFoundError(after_path)

        before = cv2.cvtColor(before, cv2.COLOR_BGR2RGB)
        after = cv2.cvtColor(after, cv2.COLOR_BGR2RGB)

        before = cv2.resize(before, (512, 512), interpolation=cv2.INTER_LINEAR)
        after = cv2.resize(after, (512, 512), interpolation=cv2.INTER_LINEAR)

        data = self.preprocess(
            image=before,
            image2=after,
        )

        inp = torch.cat(
            [data["image"], data["image2"]],
            dim=0,
        ).unsqueeze(0).to(self.device)

        print("\nRunning ChangeStar2 inference...")
        with torch.no_grad():
            output = self.model(inp)

        output.logit_to_prob_()

        probability_map = (
            output.change_prediction
            .squeeze()
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

        cloud_mask = self._load_mask(cloud_mask_path, probability_map.shape)
        water_mask = self._load_mask(water_mask_path, probability_map.shape)
        valid_mask = ((cloud_mask == 0) & (water_mask == 0)).astype(np.uint8)

        threshold = self._adaptive_threshold(
            probability_map,
            valid_mask,
        )

        binary_map = (probability_map > threshold).astype(np.uint8)
        binary_map = self._post_process(binary_map)

        before_segmentation = None
        after_segmentation = None

        if before_segmentation_path and Path(before_segmentation_path).exists():
            before_segmentation = np.load(before_segmentation_path)
            before_segmentation = cv2.resize(
                before_segmentation.astype(np.uint8),
                (512, 512),
                interpolation=cv2.INTER_NEAREST,
            )

        if after_segmentation_path and Path(after_segmentation_path).exists():
            after_segmentation = np.load(after_segmentation_path)
            after_segmentation = cv2.resize(
                after_segmentation.astype(np.uint8),
                (512, 512),
                interpolation=cv2.INTER_NEAREST,
            )

        statistics = self._compute_change_statistics(
            probability_map,
            binary_map,
            cloud_mask,
            water_mask,
            before_segmentation=before_segmentation,
            after_segmentation=after_segmentation,
        )
        statistics["adaptive_threshold"] = round(threshold, 4)

        original = cv2.imread(str(before_path))
        original = cv2.resize(
            original,
            (512, 512),
            interpolation=cv2.INTER_LINEAR,
        )

        overlay = original.copy()
        overlay[binary_map == 1] = (0, 0, 255)
        overlay[cloud_mask == 1] = (255, 255, 255)
        overlay[water_mask == 1] = (255, 200, 0)
        result = cv2.addWeighted(
            original,
            0.72,
            overlay,
            0.28,
            0,
        )

        mask_path = str(output_paths["changestar_prediction"])
        probability_path = str(output_paths["changestar_probability"])
        statistics_path = str(output_paths["change_statistics"])

        cv2.imwrite(mask_path, result)
        np.save(probability_path, probability_map)

        # Save probability map as a browser-displayable heatmap PNG
        prob_png_path = output_paths.get("changestar_probability_map")
        if prob_png_path is not None:
            prob_uint8 = np.clip(probability_map * 255.0, 0, 255).astype(np.uint8)
            prob_heatmap = cv2.applyColorMap(prob_uint8, cv2.COLORMAP_JET)
            cv2.imwrite(str(prob_png_path), prob_heatmap)
            print(f"[ChangeStar2] Probability heatmap saved: {prob_png_path}")

        with open(statistics_path, "w", encoding="utf-8") as handle:
            json.dump(statistics, handle, indent=4)

        return {
            "change_percentage": float(statistics["true_structural_change_percentage"]),
            "raw_change_percentage": float(statistics["raw_change_percentage"]),
            "confidence": float(statistics["confidence"]),
            "model": "ChangeStar2",
            "mask_path": mask_path,
            "probability_map": probability_path,
            "change_map": probability_map,
            "binary_change_map": binary_map,
            "statistics_path": statistics_path,
            "statistics": statistics,
        }
