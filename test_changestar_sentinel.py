import cv2
import torch
import rasterio
import numpy as np
import albumentations as A
import ever as er
from torchange.models.changen2 import s1_init_s1c1_changestar_vitb_1x256

# ==========================================================
# CHANGE THESE FOUR PATHS
# ==========================================================

BEFORE_VV = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\measurement\s1a-iw-grd-vv-20230120t182506-20230120t182542-046871-059ed4-001.tiff"

BEFORE_VH = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\measurement\s1a-iw-grd-vh-20230120t182506-20230120t182542-046871-059ed4-002.tiff"

AFTER_VV = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230210T180045_20230210T180110_047177_05A91B_9D5D.SAFE\S1A_IW_GRDH_1SDV_20230210T180045_20230210T180110_047177_05A91B_9D5D.SAFE\measurement\s1a-iw-grd-vv-20230210t180045-20230210t180110-047177-05a91b-001.tiff"

AFTER_VH = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230210T180045_20230210T180110_047177_05A91B_9D5D.SAFE\S1A_IW_GRDH_1SDV_20230210T180045_20230210T180110_047177_05A91B_9D5D.SAFE\measurement\s1a-iw-grd-vh-20230210t180045-20230210t180110-047177-05a91b-002.tiff"

# ==========================================================

print("Loading ChangeStar2...")
model = s1_init_s1c1_changestar_vitb_1x256()
model.eval()
model.to(er.auto_device())

print("Device:", er.auto_device())


def load_sar(vv_path, vh_path):

    with rasterio.open(vv_path) as src:
        vv = src.read(1).astype(np.float32)

    with rasterio.open(vh_path) as src:
        vh = src.read(1).astype(np.float32)

    print("\nOriginal size:", vv.shape)

    # Resize to model size
    vv = cv2.resize(vv, (512, 512))
    vh = cv2.resize(vh, (512, 512))

    # Normalize each channel
    vv = (vv - vv.mean()) / (vv.std() + 1e-6)
    vh = (vh - vh.mean()) / (vh.std() + 1e-6)

    # Normalize VV and VH independently
    vv = (vv - vv.mean()) / (vv.std() + 1e-6)
    vh = (vh - vh.mean()) / (vh.std() + 1e-6)

    # Build third channel from normalized bands
    ratio = (vv - vh)

    img = np.stack([vv, vh, ratio], axis=-1).astype(np.float32)

    return img


before = load_sar(BEFORE_VV, BEFORE_VH)
after = load_sar(AFTER_VV, AFTER_VH)

print("\nBefore:", before.shape)
print("After :", after.shape)

transform = A.Compose([
    A.pytorch.ToTensorV2()
], additional_targets={'image2': 'image'})

sample = transform(image=before, image2=after)

before = sample["image"]
after = sample["image2"]

print("\nTensor shapes")
print(before.shape)
print(after.shape)

# concatenate
inp = torch.cat([before, after], dim=0)

print("Model input:", inp.shape)

inp = inp.unsqueeze(0).to(er.auto_device())

print("\nRunning inference...")

with torch.no_grad():
    output = model(inp)

output.logit_to_prob_()

change = output.change_prediction.squeeze().cpu().numpy()

print("\nPrediction")
print("----------------------------")
print("Shape :", change.shape)
print("Min   :", change.min())
print("Max   :", change.max())
print("Mean  :", change.mean())

change_img = (change * 255).astype(np.uint8)

cv2.imwrite("changestar_sentinel_prediction.png", change_img)

print("\nSaved:")
print("changestar_sentinel_prediction.png")