from backend.models.opencd.opencd_model import OpenCDModel

print("Creating OpenCD model...")
model = OpenCDModel()
print("OpenCD model loaded successfully!")

BEFORE = r"D:\projects\GeoSentinel_AI\backend\outputs\prithvi_before_geotiff.png"
AFTER = r"D:\projects\GeoSentinel_AI\backend\outputs\prithvi_after_geotiff.png"

result = model.predict(BEFORE, AFTER)

print("Prediction completed.")
print(type(result))