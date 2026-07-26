import rasterio


def read_geotiff(path):

    with rasterio.open(path) as src:

        metadata = {

            "crs": str(src.crs),

            "width": src.width,

            "height": src.height,

            "bands": src.count,

            "bounds": {
                "left": src.bounds.left,
                "bottom": src.bounds.bottom,
                "right": src.bounds.right,
                "top": src.bounds.top
            },

            "resolution": src.res,

            "driver": src.driver
        }

    return metadata