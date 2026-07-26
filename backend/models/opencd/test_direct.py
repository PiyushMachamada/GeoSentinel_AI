import cv2

from backend.models.opencd.opencd_model import OpenCDModel

CONFIG = r"D:\projects\GeoSentinel_AI\open-cd\configs\changer\changer_ex_r18_512x512_40k_levircd.py"

CHECKPOINT = r"D:\projects\GeoSentinel_AI\open-cd\checkpoints\changer\changer_r18_levir.pth"

BEFORE = r"C:\Users\HP\Documents\GeoSentinel_AI\backend\outputs\prithvi_before_geotiff.png"

AFTER = r"C:\Users\HP\Documents\GeoSentinel_AI\backend\outputs\prithvi_after_geotiff.png"

print("Loading OpenCD...")

model = OpenCDModel(CONFIG, CHECKPOINT)

print("Running inference...")

mask = model.predict(BEFORE, AFTER)

print(mask.shape)

mask = (mask * 255).astype("uint8")

cv2.imwrite(
    r"C:\Users\HP\Documents\GeoSentinel_AI\backend\outputs\opencd_result.png",
    mask
)

print("Saved!")