import rasterio
import numpy as np

# -----------------------------
# Sentinel-1 VH image
# -----------------------------
vh_path = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\measurement\s1a-iw-grd-vh-20230120t182506-20230120t182542-046871-059ed4-002.tiff"

# -----------------------------
# Sentinel-1 VV image
# -----------------------------
vv_path = r"D:\Sentinel\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\S1A_IW_GRDH_1SDV_20230120T182506_20230120T182542_046871_059ED4_1331.SAFE\measurement\s1a-iw-grd-vv-20230120t182506-20230120t182542-046871-059ed4-001.tiff"


def inspect_image(name, path):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    with rasterio.open(path) as src:

        image = src.read(1)

        print("Shape        :", image.shape)
        print("Data type    :", image.dtype)
        print("Bands        :", src.count)

        print("Minimum      :", np.nanmin(image))
        print("Maximum      :", np.nanmax(image))
        print("Mean         :", np.nanmean(image))
        print("Std          :", np.nanstd(image))

        print("\nMetadata")
        print("----------------------------")
        print("CRS          :", src.crs)
        print("Resolution   :", src.res)
        print("Bounds       :", src.bounds)
        print("Transform    :", src.transform)

        print("\nFirst 10 unique values:")
        print(np.unique(image)[:10])


inspect_image("Sentinel-1 VH", vh_path)
inspect_image("Sentinel-1 VV", vv_path)