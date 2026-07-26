from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from PIL import Image
import requests
import torch
import numpy as np
import cv2
from io import BytesIO

print("Loading SegFormer...")

processor = SegformerImageProcessor.from_pretrained(
    "nvidia/segformer-b0-finetuned-ade-512-512"
)

model = SegformerForSemanticSegmentation.from_pretrained(
    "nvidia/segformer-b0-finetuned-ade-512-512"
)

image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

image = Image.open(
    BytesIO(requests.get(image_url).content)
).convert("RGB")

inputs = processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

seg = outputs.logits.argmax(dim=1)[0].cpu().numpy()

seg = cv2.resize(
    seg.astype(np.uint8),
    image.size
)

colored = cv2.applyColorMap(
    (seg * 10).astype(np.uint8),
    cv2.COLORMAP_JET
)

cv2.imwrite(
    "backend/outputs/segformer_result.png",
    colored
)

print("Segmentation image saved!")