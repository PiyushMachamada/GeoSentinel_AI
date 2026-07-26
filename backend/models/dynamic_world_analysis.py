import rasterio
import numpy as np


CLASS_NAMES = {
    0: "water",
    1: "trees",
    2: "grass",
    3: "flooded_vegetation",
    4: "crops",
    5: "shrub_and_scrub",
    6: "built_area",
    7: "bare_ground",
    8: "snow_and_ice"
}


def analyze_dynamic_world(path):
    """
    Analyze a Dynamic World GeoTIFF.

    Returns:
        {
            metadata,
            summary,
            classes
        }
    """

    with rasterio.open(path) as src:

        data = src.read(1)

        metadata = {
            "width": src.width,
            "height": src.height,
            "bands": src.count,
            "crs": str(src.crs),
            "resolution": src.res,
            "bounds": list(src.bounds)
        }

    if data.size == 0:
        raise ValueError("Dynamic World raster is empty.")

    total_pixels = int(data.size)

    class_results = {}

    dominant_class = None
    dominant_percentage = 0

    for class_id, class_name in CLASS_NAMES.items():

        pixel_count = int(np.sum(data == class_id))

        percentage = round(
            (pixel_count / total_pixels) * 100,
            2
        )

        class_results[class_name] = {

            "pixels": pixel_count,

            "percentage": percentage

        }

        if percentage > dominant_percentage:

            dominant_percentage = percentage
            dominant_class = class_name

    summary = {

        "total_pixels": total_pixels,

        "dominant_class": dominant_class,

        "dominant_percentage": dominant_percentage

    }

    return {

        "metadata": metadata,

        "summary": summary,

        "classes": class_results

    }


if __name__ == "__main__":

    results = analyze_dynamic_world(
        "datasets/geotiff/before_dynamic_world.tif"
    )

    from pprint import pprint

    pprint(results)