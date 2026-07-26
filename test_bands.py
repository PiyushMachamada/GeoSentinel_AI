import rasterio

path = r"datasets\geotiff\before.tif"

with rasterio.open(path) as src:

    print("=" * 60)
    print("GENERAL")
    print("=" * 60)

    print("Driver:", src.driver)
    print("CRS:", src.crs)
    print("Width:", src.width)
    print("Height:", src.height)
    print("Count:", src.count)
    print("Dtypes:", src.dtypes)
    print("Indexes:", src.indexes)
    print()

    print("=" * 60)
    print("PROFILE")
    print("=" * 60)

    print(src.profile)

    print()

    print("=" * 60)
    print("TAGS")
    print("=" * 60)

    print(src.tags())

    print()

    print("=" * 60)
    print("BAND TAGS")
    print("=" * 60)

    for i in src.indexes:
        print(f"\nBand {i}")
        print("Description:", src.descriptions[i-1])
        print("Tags:", src.tags(i))
        print("ColorInterp:", src.colorinterp[i-1])