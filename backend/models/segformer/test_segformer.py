from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from PIL import Image
import requests
import torch
from io import BytesIO

print("Loading SegFormer model...")

processor = SegformerImageProcessor.from_pretrained(
    "nvidia/segformer-b0-finetuned-ade-512-512"
)

model = SegformerForSemanticSegmentation.from_pretrained(
    "nvidia/segformer-b0-finetuned-ade-512-512"
)

image_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

response = requests.get(image_url)

image = Image.open(BytesIO(response.content)).convert("RGB")

inputs = processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

print("SegFormer inference successful!")
print("Output shape:", outputs.logits.shape)