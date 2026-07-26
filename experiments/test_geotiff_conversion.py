from backend.models.geotiff_preprocessing import (
    geotiff_to_png
)

geotiff_to_png(
    "datasets/geotiff/before.tif",
    "datasets/change_detection/before_geotiff.png"
)

geotiff_to_png(
    "datasets/geotiff/after.tif",
    "datasets/change_detection/after_geotiff.png"
)