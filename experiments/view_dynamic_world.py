import rasterio
import matplotlib.pyplot as plt

with rasterio.open("dynamic_world.tif") as src:
    image = src.read(1)

plt.imshow(image)
plt.colorbar()
plt.title("Dynamic World Classes")

plt.savefig("dynamic_world_visualization.png")

print("Saved successfully")