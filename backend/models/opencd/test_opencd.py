from opencd.apis import OpenCDInferencer

CONFIG = r"D:\projects\GeoSentinel_AI\open-cd\configs\changer\changer_ex_r18_512x512_40k_levircd.py"
CHECKPOINT = r"D:\projects\GeoSentinel_AI\open-cd\checkpoints\changer\changer_r18_levir.pth"

BEFORE = r"C:\Users\HP\Documents\GeoSentinel_AI\backend\outputs\prithvi_before_geotiff.png"
AFTER = r"C:\Users\HP\Documents\GeoSentinel_AI\backend\outputs\prithvi_after_geotiff.png"

inferencer = OpenCDInferencer(
    model=CONFIG,
    weights=CHECKPOINT,
    device="cuda:0"
)

result = inferencer(
    inputs=[[BEFORE, AFTER]],
    show=False,
    save_dir="backend/outputs/opencd"
)

print(result)