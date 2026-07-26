from transformers import (
SegformerImageProcessor,
SegformerForSemanticSegmentation
)

from PIL import Image
import torch
import numpy as np
import cv2
import os

class SegFormerModel:

 def __init__(self):

    print("Loading SegFormer Model...")

    self.processor = SegformerImageProcessor.from_pretrained(
        "Pranilllllll/segformer-satellite-segementation"
    )

    self.model = SegformerForSemanticSegmentation.from_pretrained(
        "Pranilllllll/segformer-satellite-segementation"
    )

    print("\nMODEL NAME")
    print("=" * 30)
    print(self.model.config._name_or_path)

    print("\nNUMBER OF LABELS")
    print("=" * 30)
    print(self.model.config.num_labels)

    self.device = torch.device(
        "cuda" if torch.cuda.is_available()
        else "cpu"
    )

    print(f"\nUsing device: {self.device}")

    self.model.to(self.device)

    print("\nMODEL LABELS")
    print("=" * 30)

    for k, v in self.model.config.id2label.items():
        print(k, ":", v)

 def segment(self, image_path):

    image = Image.open(image_path).convert("RGB")

    inputs = self.processor(
        images=image,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(self.device)
        for k, v in inputs.items()
    }

    with torch.no_grad():
        outputs = self.model(**inputs)

    seg = outputs.logits.argmax(
        dim=1
    )[0].cpu().numpy()

    seg = cv2.resize(
        seg.astype(np.uint8),
        image.size,
        interpolation=cv2.INTER_NEAREST
    )

    # ==================================
    # LAND COVER STATISTICS
    # ==================================

    unique, counts = np.unique(
        seg,
        return_counts=True
    )

    total_pixels = seg.size

    class_stats = {}

    print("\nLand Cover Statistics")
    print("-" * 30)

    for cls, count in zip(unique, counts):

        percentage = (
            count / total_pixels
        ) * 100

        class_name = self.model.config.id2label.get(
            int(cls),
            f"class_{cls}"
        )

        class_stats[class_name] = round(
            percentage,
            2
        )

        print(
            f"{class_name}: {percentage:.2f}%"
        )

    # ==================================
    # SEMANTIC COLOR MAP
    # ==================================

    colored = np.zeros(
        (
            seg.shape[0],
            seg.shape[1],
            3
        ),
        dtype=np.uint8
    )

    colors = {
        0: [0, 0, 0],
        1: [128, 0, 0],
        2: [0, 128, 0],
        3: [128, 128, 0],
        4: [0, 0, 128],
        5: [128, 0, 128],
        6: [0, 128, 128]
    }

    for class_id, color in colors.items():
        colored[seg == class_id] = color

    # ==================================
    # OVERLAY
    # ==================================

    original = np.array(image)

    original = cv2.cvtColor(
        original,
        cv2.COLOR_RGB2BGR
    )

    blended = cv2.addWeighted(
        original,
        0.6,
        colored,
        0.4,
        0
    )

    # ==================================
    # OUTPUT FILES
    # ==================================

    filename = os.path.basename(
        image_path
    )

    name = os.path.splitext(
        filename
    )[0]

    mask_path = (
        f"backend/outputs/segmask_{name}.npy"
    )

    np.save(
        mask_path,
        seg
    )

    print(
        f"Segmentation mask saved: {mask_path}"
    )

    output_path = (
        f"backend/outputs/segformer_{name}.png"
    )

    cv2.imwrite(
        output_path,
        blended
    )

    print(
        f"\nSegmentation saved:"
    )

    print(output_path)

    return class_stats
