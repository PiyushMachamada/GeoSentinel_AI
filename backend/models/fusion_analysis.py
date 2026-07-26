import numpy as np
import cv2
import json

CLASS_NAMES = {
    0: "background",
    1: "residential_area",
    2: "road",
    3: "river",
    4: "forest",
    5: "unused_land",
    6: "agricultural_area"
}


def analyze_change_by_class():

    seg_before = np.load(
        "backend/outputs/segmask_before.npy"
    )

    change_mask = cv2.imread(
        "backend/outputs/changeformer_result.png",
        cv2.IMREAD_GRAYSCALE
    )

    if change_mask is None:
        raise ValueError(
            "Could not load ChangeFormer mask"
        )

    change_mask = cv2.resize(
        change_mask,
        (
            seg_before.shape[1],
            seg_before.shape[0]
        ),
        interpolation=cv2.INTER_NEAREST
    )

    changed_pixels = seg_before[
        change_mask > 0
    ]

    total_changed = len(
        changed_pixels
    )

    if total_changed == 0:

        return {
            "total_changed_pixels": 0,
            "change_distribution": {}
        }

    distribution = {}

    for class_id, class_name in CLASS_NAMES.items():

        count = np.sum(
            changed_pixels == class_id
        )

        percent = (
            count /
            total_changed
        ) * 100

        distribution[
            class_name
        ] = round(
            percent,
            2
        )

    results = {
        "total_changed_pixels":
            int(total_changed),

        "change_distribution":
            distribution
    }

    with open(
        "backend/outputs/fusion_results.json",
        "w"
    ) as f:

        json.dump(
            results,
            f,
            indent=4
        )

    return results