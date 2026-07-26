import torch

ckpt_path = r"backend/models/changeformer/checkpoints/ChangeFormer_LEVIR/best_ckpt.pt"

print("Loading checkpoint...")

checkpoint = torch.load(
    ckpt_path,
    map_location="cpu",
    weights_only=False
)

print("\nCheckpoint Type:")
print(type(checkpoint))

if isinstance(checkpoint, dict):
    print("\nCheckpoint Keys:")
    for key in checkpoint.keys():
        print("-", key)