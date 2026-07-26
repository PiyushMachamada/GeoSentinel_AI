import rasterio

with rasterio.open("datasets/geotiff/before.tif") as src:
    print("=" * 50)
    print("Band count:", src.count)
    print("CRS:", src.crs)
    print("Descriptions:", src.descriptions)
    print()

    for i in range(1, src.count + 1):
        print(f"Band {i}")
        print("dtype:", src.dtypes[i - 1])
        print()

    print("Profile:")
    print(src.profile)