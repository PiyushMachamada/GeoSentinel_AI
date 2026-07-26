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


def analyze_transitions():

    print("\nRunning Transition Analysis...")

    # ==========================
    # LOAD SEGMENTATION MASKS
    # ==========================

    seg_before = np.load(
        "backend/outputs/segmask_before.npy"
    )

    seg_after = np.load(
        "backend/outputs/segmask_after.npy"
    )

    print(
        f"SegFormer BEFORE shape: {seg_before.shape}"
    )

    print(
        f"SegFormer AFTER shape: {seg_after.shape}"
    )

    # ==========================
    # LOAD CHANGEFORMER MASK
    # ==========================

    change_mask = cv2.imread(
        "backend/outputs/changeformer_result.png",
        cv2.IMREAD_GRAYSCALE
    )

    if change_mask is None:
        raise FileNotFoundError(
            "Could not load changeformer_result.png"
        )

    print(
        f"Original ChangeFormer shape: {change_mask.shape}"
    )

    # ==========================
    # RESIZE TO SEGFORMER SIZE
    # ==========================

    change_mask = cv2.resize(
        change_mask,
        (
            seg_before.shape[1],
            seg_before.shape[0]
        ),
        interpolation=cv2.INTER_NEAREST
    )

    print(
        f"Resized ChangeFormer shape: {change_mask.shape}"
    )

    # ==========================
    # BINARY CHANGE REGION
    # ==========================

    changed_pixels = change_mask > 0

    print(
        "Total Changed Pixels:",
        np.sum(changed_pixels)
    )

    # ==========================
    # EXTRACT CLASSES
    # ==========================

    before_classes = seg_before[
        changed_pixels
    ]

    after_classes = seg_after[
        changed_pixels
    ]

    print("\n===== TRANSITION DEBUG =====")

    print(
        "Changed pixels count:",
        len(before_classes)
    )

    print(
        "Unique BEFORE in changed area:",
        np.unique(before_classes)
    )

    print(
        "Unique AFTER in changed area:",
        np.unique(after_classes)
    )

    print("============================\n")

    # ==========================
    # COUNT TRANSITIONS
    # ==========================

    transitions = {}

    for before_id, after_id in zip(
        before_classes,
        after_classes
    ):

        # Ignore unchanged classes
        if before_id == after_id:
            continue

        before_name = CLASS_NAMES.get(
            int(before_id),
            str(before_id)
        )

        after_name = CLASS_NAMES.get(
            int(after_id),
            str(after_id)
        )

        key = (
            f"{before_name}_to_{after_name}"
        )

        transitions[key] = (
            transitions.get(key, 0) + 1
        )

    # ==========================
    # NO TRANSITIONS FOUND
    # ==========================

    if len(transitions) == 0:

        transitions = {
            "no_transitions_detected": True
        }

        with open(
            "backend/outputs/transition_results.json",
            "w"
        ) as f:

            json.dump(
                transitions,
                f,
                indent=4
            )

        return transitions

    # ==========================
    # CONVERT TO PERCENTAGES
    # ==========================

    total = sum(
        transitions.values()
    )

    for key in transitions:

        transitions[key] = round(
            (
                transitions[key]
                / total
            ) * 100,
            2
        )

    # ==========================
    # SORT DESCENDING
    # ==========================

    transitions = dict(
        sorted(
            transitions.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

    # ==========================
    # SAVE RESULTS
    # ==========================

    with open(
        "backend/outputs/transition_results.json",
        "w"
    ) as f:

        json.dump(
            transitions,
            f,
            indent=4
        )

    print("\nTransition Results:")

    for key, value in transitions.items():

        print(
            f"{key}: {value}%"
        )

    return transitions