import ee
import geemap

ee.Initialize(project="geosentinel-earthengine")

roi = ee.Geometry.Rectangle([
    -77.74513477667382,
    24.45079559713128,
    -76.59943834724233,
    25.550873767434343
])

dynamic_world = (
    ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
    .filterBounds(roi)
    .first()
)

label = dynamic_world.select("label")

print("Downloading Dynamic World...")

geemap.ee_export_image(
    label,
    filename="dynamic_world.tif",
    scale=100,
    region=roi
)

print("Download Complete")