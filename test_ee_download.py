import ee
from google.oauth2 import service_account

PROJECT_ID = "geosentinel-earthengine"
SERVICE_ACCOUNT_FILE = "credentials/earthengine-service-account.json"

ee.Authenticate()
ee.Initialize(project="geosentinel-earthengine")

print("✓ Earth Engine initialized")

# AOI (Kempegowda Airport)
latitude = 13.1986
longitude = 77.7066
radius_km = 5

region = (
    ee.Geometry.Point([longitude, latitude])
    .buffer(radius_km * 1000)
)

# Fetch one Sentinel image
collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(region)
    .filterDate("2026-05-01", "2026-05-20")
    .sort("system:time_start", False)
)

count = collection.size().getInfo()
print(f"Images found: {count}")

if count == 0:
    raise RuntimeError("No Sentinel images found.")

image = collection.first().select(["B4", "B3", "B2"])

print("Generating download URL...")

url = image.getDownloadURL(
    {
        "scale": 10,
        "region": region,
        "format": "GEO_TIFF",
        "filePerBand": False,
    }
)

print("\nSUCCESS")
print(url)