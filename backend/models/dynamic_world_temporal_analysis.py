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


def empty_dynamic_world_results():

    return {
        class_name: {
            "before": 0.0,
            "after": 0.0,
            "change": 0.0,
        }
        for class_name in CLASS_NAMES.values()
    }


def calculate_statistics(path):

    with rasterio.open(path) as src:
        data = src.read(1)

    total_pixels = data.size

    results = {}

    for class_id, class_name in CLASS_NAMES.items():

        count = np.sum(data == class_id)

        percentage = (
            count / total_pixels
        ) * 100

        results[class_name] = round(
            percentage,
            2
        )

    return results


def compare_dynamic_world(
    before_path,
    after_path
):

    before = calculate_statistics(before_path)

    after = calculate_statistics(after_path)

    comparison = {}

    for cls in CLASS_NAMES.values():

        comparison[cls] = {
            "before": before[cls],
            "after": after[cls],
            "change": round(
                after[cls] - before[cls],
                2
            )
        }

    return comparison