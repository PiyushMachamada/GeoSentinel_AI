# experiments/dynamic_world_stats.py

import rasterio
import numpy as np

CLASS_NAMES = {
    0: "Water",
    1: "Trees",
    2: "Grass",
    3: "Flooded Vegetation",
    4: "Crops",
    5: "Shrub & Scrub",
    6: "Built Area",
    7: "Bare Ground",
    8: "Snow & Ice"
}

with rasterio.open("dynamic_world.tif") as src:

    image = src.read(1)

unique, counts = np.unique(image, return_counts=True)

total = image.size

print("\nDynamic World Statistics\n")

for value, count in zip(unique, counts):

    percentage = (count / total) * 100

    print(
        f"{CLASS_NAMES.get(int(value), value)}: "
        f"{percentage:.2f}%"
    )