import ee
import geemap

ee.Initialize(project="geosentinel-earthengine")

roi = ee.Geometry.Rectangle([
    -54.90,
    -10.35,
    -54.75,
    -10.20
])

print("Downloading BEFORE image...")

before = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(roi)
    .filterDate("2020-01-01", "2020-12-31")
    .sort("CLOUDY_PIXEL_PERCENTAGE")
    .first()
)

geemap.ee_export_image(
    before.select(["B4", "B3", "B2"]),
    filename="datasets/geotiff/before.tif",
    scale=10,
    region=roi
)

print("Downloading AFTER image...")

after = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(roi)
    .filterDate("2025-01-01", "2025-12-31")
    .sort("CLOUDY_PIXEL_PERCENTAGE")
    .first()
)

geemap.ee_export_image(
    after.select(["B4", "B3", "B2"]),
    filename="datasets/geotiff/after.tif",
    scale=10,
    region=roi
)

print("Download Complete")