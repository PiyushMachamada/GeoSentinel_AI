from backend.models.geospatial_analysis import (
    analyze_geotiff
)

results = analyze_geotiff(
    "datasets/geotiff/rgb2.tif"
)

print(results)
