from terratorch.models.encoder_decoder_factory import EncoderDecoderFactory
import torch
import rasterio
import numpy as np
import cv2

import terratorch
print("Terratorch Version:", terratorch.__version__)

print("Creating Prithvi Segmentation Model...")

factory = EncoderDecoderFactory()

model = factory.build_model(
    task="segmentation",
    backbone="terratorch_prithvi_eo_v2_300",
    decoder="FCNDecoder",
    num_classes=7
)

model.eval()

print("Reading GeoTIFF...")

with rasterio.open("datasets/geotiff/rgb2.tif") as src:
    image = src.read()

print("Original Shape:")
print(image.shape)

image = image.astype(np.float32)

if image.shape[0] < 6:
    extra = np.zeros(
        (
            6 - image.shape[0],
            image.shape[1],
            image.shape[2]
        ),
        dtype=np.float32
    )
    image = np.concatenate([image, extra], axis=0)

image = image[:6]

tensor = torch.tensor(image)

tensor = torch.nn.functional.interpolate(
    tensor.unsqueeze(0),
    size=(224,224),
    mode="bilinear",
    align_corners=False
)

tensor = tensor.unsqueeze(2)

with torch.no_grad():
    output = model(tensor)

prediction = output.output.argmax(dim=1)

prediction = prediction.squeeze().cpu().numpy()

print("\nPrediction Shape:")
print(prediction.shape)

print("\nUnique Classes:")
print(np.unique(prediction))

# ------------------------------------
# COLOR MAP
# ------------------------------------

colors = {
    0: (0, 0, 0),         # background
    1: (255, 0, 0),       # residential
    2: (128, 128, 128),   # road
    3: (0, 0, 255),       # river
    4: (0, 255, 0),       # forest
    5: (255, 255, 0),     # unused land
    6: (255, 165, 0),     # agriculture
}

mask_rgb = np.zeros(
    (prediction.shape[0],
     prediction.shape[1],
     3),
    dtype=np.uint8
)

for cls, color in colors.items():
    mask_rgb[prediction == cls] = color

cv2.imwrite(
    "experiments/prithvi_segmentation.png",
    cv2.cvtColor(mask_rgb, cv2.COLOR_RGB2BGR)
)

print("\nSaved:")
print("experiments/prithvi_segmentation.png")