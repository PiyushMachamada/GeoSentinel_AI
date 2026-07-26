import rasterio

with rasterio.open("datasets/geotiff/before.tif") as src:
    img = src.read()

    print("Shape:", img.shape)

    for i in range(src.count):
        print(f"\nBand {i+1}")
        print("Min :", img[i].min())
        print("Max :", img[i].max())
        print("Mean:", img[i].mean())

    print("\nBand Descriptions:", src.descriptions)