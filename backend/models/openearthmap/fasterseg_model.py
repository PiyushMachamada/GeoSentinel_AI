from PIL import Image
import torchvision.transforms as transforms

from .class_mapping import OEM_CLASSES, CLASS_COLORS

import os
import sys
import torch
import numpy as np
import cv2


# --------------------------------------------------
# Locate OEM-Lightweight Repository
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

OEM_ROOT = os.path.join(PROJECT_ROOT, "oem-lightweight")

sys.path.insert(0, OEM_ROOT)
sys.path.insert(0, os.path.join(OEM_ROOT, "oem_lightweight"))
sys.path.insert(0, os.path.join(OEM_ROOT, "fasterseg_api"))


# --------------------------------------------------
# Import FasterSeg
# --------------------------------------------------

from oem_lightweight.model import fasterseg


class FasterSegModel:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        arch = os.path.join(
            OEM_ROOT,
            "models",
            "FasterSeg",
            "arch_1.pt"
        )

        weights = os.path.join(
            OEM_ROOT,
            "models",
            "FasterSeg",
            "weights1.pt"
        )

        print("\nLoading FasterSeg...")

        self.model = fasterseg(
            arch=arch,
            weights=weights
        )

        self.model.to(self.device)
        self.model.eval()

        print("FasterSeg Loaded Successfully.\n")
        
    def preprocess_image(self, image_path):

        image = Image.open(image_path).convert("RGB")

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.4325, 0.4483, 0.3879],
                std=[0.0195, 0.0169, 0.0179]
            )
        ])

        tensor = transform(image).unsqueeze(0)

        return image, tensor.to(self.device)
    
        @torch.no_grad()
        def predict(self, image_path):

         original_image, image_tensor = self.preprocess_image(image_path)

        prediction = self.model(image_tensor)
 
        if isinstance(prediction, (list, tuple)):
            prediction = prediction[0]

        prediction = torch.argmax(
            prediction,
            dim=1
        )

        prediction = prediction.squeeze().cpu().numpy()

        return prediction