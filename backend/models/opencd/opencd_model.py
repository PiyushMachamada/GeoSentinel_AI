import torch
import cv2
import numpy as np
import os

from mmseg.structures import SegDataSample
from mmengine.config import Config
from mmengine.runner import load_checkpoint
from mmengine.registry import init_default_scope
from opencd.apis import OpenCDInferencer


import opencd.models
from opencd.registry import MODELS


class OpenCDModel:

    def __init__(self):

        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.config_path = r"D:\projects\GeoSentinel_AI\open-cd\configs\changer\changer_ex_r18_512x512_40k_levircd.py"

        self.checkpoint_path = r"D:\projects\GeoSentinel_AI\open-cd\checkpoints\changer\changer_r18_levir.pth"

        # Initialize OpenCD registry
        init_default_scope("opencd")

        # Load configuration
        cfg = Config.fromfile(self.config_path)
        

        # Build model
        self.model = MODELS.build(cfg.model)

        # Load weights
        load_checkpoint(
            self.model,
            self.checkpoint_path,
            map_location=self.device
        )

        # Move model to device
        self.model.to(self.device)

        # Evaluation mode
        self.model.eval()

        print("✓ OpenCD model initialized successfully")
        
    def predict(self, before_image, after_image):

        print("Loading images...")

        before = cv2.imread(before_image)
        after = cv2.imread(after_image)

        if before is None:
            raise FileNotFoundError(before_image)

        if after is None:
            raise FileNotFoundError(after_image)

        before = cv2.cvtColor(before, cv2.COLOR_BGR2RGB)
        after = cv2.cvtColor(after, cv2.COLOR_BGR2RGB)
        
        before = cv2.resize(before, (1024, 1024), interpolation=cv2.INTER_LINEAR)
        after = cv2.resize(after, (1024, 1024), interpolation=cv2.INTER_LINEAR)

        # ---------- ADD THIS PART ----------
        before = torch.from_numpy(before).permute(2, 0, 1).float()
        after = torch.from_numpy(after).permute(2, 0, 1).float()

        inputs = torch.cat([before, after], dim=0)

        print("Input tensor shape:", inputs.shape)

        inputs = inputs.to(self.device)
        # -----------------------------------
        
        # Add batch dimension: [6, H, W] -> [1, 6, H, W]
        inputs = inputs.unsqueeze(0)

        # Create a minimal data sample for inference
        data_sample = SegDataSample()

        h, w = before.shape[1], before.shape[2]

        data_sample.set_metainfo(
            dict(
                ori_shape=(h, w),
                img_shape=(h, w),
                pad_shape=(h, w),
                padding_size=[0, 0, 0, 0]
            )
        )

        # Build the dictionary expected by the data preprocessor
        data = {
            "inputs": [inputs.squeeze(0)],
            "data_samples": [data_sample]
        }

        processed = self.model.data_preprocessor(
            data,
            training=False
        )

        print(type(processed))
        print(processed.keys())

        print(type(processed["inputs"]))
        print(type(processed["data_samples"]))

        print(processed["data_samples"][0])

        print("Processed input shape:", processed["inputs"].shape)
        
        with torch.no_grad():
            predictions = self.model.test_step(processed)

        print(type(predictions))
        print(predictions)
        
        prediction = predictions[0]

        # Extract the predicted change mask
        change_mask = prediction.pred_sem_seg.data.squeeze().cpu().numpy()

        print("Change mask shape:", change_mask.shape)
        print("Unique values:", np.unique(change_mask))
        
        save_path = r"D:\projects\GeoSentinel_AI\backend\outputs\opencd_prediction.png"

        success = cv2.imwrite(
            save_path,
            (change_mask * 255).astype(np.uint8)
        )

        print("Save successful:", success)
        print("Exists:", os.path.exists(save_path))
        print("Saved to:", save_path)
        print(r"D:\projects\GeoSentinel_AI\backend\outputs\opencd_prediction.png")

        change_percentage = float(
            np.count_nonzero(change_mask) / change_mask.size * 100
        )

        return {
            "change_percentage": round(change_percentage, 2),
            "model": "OpenCD",
            "mask_path": save_path
        }