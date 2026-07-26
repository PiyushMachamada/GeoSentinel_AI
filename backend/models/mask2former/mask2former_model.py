from transformers import (
    Mask2FormerForUniversalSegmentation,
    Mask2FormerImageProcessor
)

print("Loading model...")

processor = Mask2FormerImageProcessor.from_pretrained(
    "mfaytin/mask2former-satellite"
)

model = Mask2FormerForUniversalSegmentation.from_pretrained(
    "mfaytin/mask2former-satellite"
)

print("\nMODEL LABELS")
print("=" * 30)

for k, v in model.config.id2label.items():
    print(k, ":", v)