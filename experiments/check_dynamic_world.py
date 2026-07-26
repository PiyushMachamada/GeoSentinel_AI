# experiments/check_dynamic_world.py

import rasterio

with rasterio.open("dynamic_world.tif") as src:

    print("Width:", src.width)
    print("Height:", src.height)
    print("Bands:", src.count)
    print("CRS:", src.crs)

    band = src.read(1)

    print("Min:", band.min())
    print("Max:", band.max())

    print("Shape:", band.shape)