import os
import sys
import torch

# -------------------------------------------------
# Locate OEM-Lightweight
# -------------------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

OEM_ROOT = os.path.join(PROJECT_ROOT, "oem-lightweight")

sys.path.insert(0, OEM_ROOT)
sys.path.insert(0, os.path.join(OEM_ROOT, "oem_lightweight"))
sys.path.insert(0, os.path.join(OEM_ROOT, "fasterseg_api"))
sys.path.insert(0, os.path.join(OEM_ROOT, "sparsemask_api"))

# -------------------------------------------------
# OEM Imports
# -------------------------------------------------

from config import config
from oem_lightweight.model import fasterseg
from oem_lightweight.evaluator import SegEvaluator
from oem_lightweight.utils import prepare_data


class OpenEarthMapRunner:

    def __init__(self):

        print("\nLoading OpenEarthMap FasterSeg...")

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

        self.network = fasterseg(
            arch=arch,
            weights=weights
        )

        print("OpenEarthMap Loaded Successfully.")

    def segment(self, image_path):

        data = prepare_data(
            img_file=image_path,
            label_file=image_path
        )

        evaluator = SegEvaluator(
            config,
            data,
            self.network
        )

        prediction = evaluator.evaluate()

        return prediction