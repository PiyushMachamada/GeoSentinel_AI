import rasterio
import numpy as np

with rasterio.open("datasets/geotiff/before.tif") as src:
    before = src.read()

with rasterio.open("datasets/geotiff/after.tif") as src:
    after = src.read()

difference = np.mean(np.abs(before.astype(float) - after.astype(float)))

print("Average Pixel Difference:")
print(difference)