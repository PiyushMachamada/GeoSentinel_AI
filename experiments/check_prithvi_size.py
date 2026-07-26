import torch

from terratorch.models import EncoderDecoderFactory

print("Building model...")

factory = EncoderDecoderFactory()

model = factory.build_model(
    task="segmentation",
    backbone="terratorch_prithvi_eo_v2_300",
    decoder="FCNDecoder",
    num_classes=7
)

total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"\nTotal Parameters: {total_params:,}")
print(f"Trainable Parameters: {trainable_params:,}")

size_mb = total_params * 4 / (1024**2)

print(f"Approx Model Size: {size_mb:.2f} MB")