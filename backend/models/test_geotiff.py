from backend.models.geotiff_reader import (
    read_geotiff
)

metadata = read_geotiff(
    "datasets/geotiff/rgb2.tif"
)

print(metadata)