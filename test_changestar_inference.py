import torch
import ever as er
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
from skimage.io import imread

from torchange.models.changen2 import s1_init_s1c1_changestar_vitb_1x256


torch.set_grad_enabled(False)

print("Loading ChangeStar2...")

model = s1_init_s1c1_changestar_vitb_1x256()
model.eval()
model.to(er.auto_device())

print(f"Device: {er.auto_device()}")

before_path = r"backend\outputs\prithvi_before_geotiff.png"
after_path = r"backend\outputs\prithvi_after_geotiff.png"

img1 = imread(before_path)
img2 = imread(after_path)

# Test on a small crop first
img1 = img1[1500:2012, 1500:2012]
img2 = img2[1500:2012, 1500:2012]

print("Before image shape:", img1.shape)
print("After image shape :", img2.shape)

preprocess = A.Compose(
    [
        A.Normalize(),
        ToTensorV2(),
    ],
    additional_targets={"image2": "image"},
)

print("Setup completed successfully.")

data = preprocess(
    image=img1,
    image2=img2
)

print("Preprocessing successful.")

print(type(data["image"]))
print(type(data["image2"]))

print("Image 1 tensor:", data["image"].shape)
print("Image 2 tensor:", data["image2"].shape)

img = torch.concat(
    [data["image"], data["image2"]],
    dim=0
)

print("Concatenated tensor:", img.shape)

print("\nRunning ChangeStar2 inference...")

prediction = model(
    img.unsqueeze(0).to(er.auto_device())
)

print("Inference completed!\n")

print("Prediction type:", type(prediction))

if isinstance(prediction, dict):
    print("Prediction keys:")
    for key in prediction.keys():
        print(f" - {key}")
else:
    print(prediction)

    outputs = {
    "change_prediction": prediction.change_prediction,
    "t1_semantic_prediction": prediction.t1_semantic_prediction,
    "t2_semantic_prediction": prediction.t2_semantic_prediction,
}

for name, tensor in outputs.items():
    print(f"\n{name}")
    print("---------------------------")
    print("Shape :", tensor.shape)
    print("dtype :", tensor.dtype)
    print("Min   :", tensor.min().item())
    print("Max   :", tensor.max().item())
    print("Unique values (first 20):")

    unique = torch.unique(tensor.cpu())

    print(unique[:20])
    print("Total unique:", len(unique))

    change = prediction.change_prediction

    print("\nRaw output")
    print("Min:", change.min().item())
    print("Max:", change.max().item())

    change_sigmoid = torch.sigmoid(change)

    print("\nAfter sigmoid")
    print("Min:", change_sigmoid.min().item())
    print("Max:", change_sigmoid.max().item())