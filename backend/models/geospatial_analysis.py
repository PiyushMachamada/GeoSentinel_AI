import rasterio


def analyze_geotiff(path):

    with rasterio.open(path) as src:

        bounds = {
            "left": src.bounds.left,
            "bottom": src.bounds.bottom,
            "right": src.bounds.right,
            "top": src.bounds.top
        }

        center_x = (bounds["left"] + bounds["right"]) / 2
        center_y = (bounds["bottom"] + bounds["top"]) / 2

        return {

            "crs": str(src.crs),

            "width": src.width,

            "height": src.height,

            "bands": src.count,

            "resolution_x": src.res[0],

            "resolution_y": src.res[1],

            "bounds": bounds,

            "center": {
                "x": center_x,
                "y": center_y
            },

            # Placeholder until reverse geocoding is added
            "location": "Unknown Location"
        }