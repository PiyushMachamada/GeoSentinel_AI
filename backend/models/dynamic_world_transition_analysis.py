import json
from pathlib import Path

import cv2
import numpy as np
import rasterio


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


# BGR colors (OpenCV)
TRANSITION_COLORS = {
    ("trees", "grass"): (0, 255, 0),
    ("trees", "built_area"): (0, 165, 255),
    ("trees", "water"): (255, 0, 0),
    ("grass", "built_area"): (0, 255, 255),
    ("grass", "water"): (255, 255, 0),
    ("water", "built_area"): (255, 0, 255),
    ("crops", "built_area"): (0, 0, 255),
    ("shrub_and_scrub", "trees"): (34, 139, 34),
    ("bare_ground", "built_area"): (128, 128, 128),
}


def analyze_dynamic_world_transitions(
    before_path,
    after_path,
    output_paths,
):

    print("\nAnalyzing Dynamic World Transitions...")

    with rasterio.open(before_path) as src:
        before = src.read(1)

    with rasterio.open(after_path) as src:
        after = src.read(1)

    print(f"Before Shape: {before.shape}")
    print(f"After Shape : {after.shape}")

    if before.shape != after.shape:
        raise ValueError(
            "Before and After Dynamic World rasters have different shapes."
        )

    changed_mask = before != after

    total_pixels = before.size
    total_changed_pixels = int(np.sum(changed_mask))

    print(f"Total Pixels        : {total_pixels}")
    print(f"Changed Pixels      : {total_changed_pixels}")

    if total_changed_pixels == 0:

        print("No Dynamic World transitions detected.")

        return {
            "summary": {
                "changed_pixels": 0,
                "change_percentage": 0.0,
                "dominant_transition": None,
                "dominant_percentage": 0.0
            },
            "transitions": {}
        }

    transition_map = np.zeros(
        (before.shape[0], before.shape[1], 3),
        dtype=np.uint8
    )

    transitions = {}

    rows, cols = np.where(changed_mask)

    for row, col in zip(rows, cols):

        before_class = int(before[row, col])
        after_class = int(after[row, col])

        before_name = CLASS_NAMES.get(
            before_class,
            f"unknown_{before_class}"
        )

        after_name = CLASS_NAMES.get(
            after_class,
            f"unknown_{after_class}"
        )

        transition = f"{before_name}_to_{after_name}"

        transitions[transition] = (
            transitions.get(transition, 0) + 1
        )

        color = TRANSITION_COLORS.get(
            (before_name, after_name),
            (255, 255, 255)
        )

        transition_map[row, col] = color

    for transition in transitions:

        transitions[transition] = round(
            (transitions[transition] / total_changed_pixels) * 100,
            2
        )

    transitions = dict(
        sorted(
            transitions.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )

    dominant_transition = next(iter(transitions))
    dominant_percentage = transitions[dominant_transition]

    summary = {

        "changed_pixels": total_changed_pixels,

        "change_percentage": round(
            (total_changed_pixels / total_pixels) * 100,
            2
        ),

        "dominant_transition": dominant_transition,

        "dominant_percentage": dominant_percentage
    }

    final_results = {

        "summary": summary,

        "transitions": transitions

    }

    transition_map_path = output_paths["dynamic_world_transition"]

    json_path = output_paths["dynamic_world_transition_json"]

    cv2.imwrite(
        str(transition_map_path),
        transition_map
    )

    with open(
        json_path,
        "w"
    ) as f:

        json.dump(
            final_results,
            f,
            indent=4
        )

    print("\nDynamic World Transition Results\n")

    for transition, percentage in transitions.items():

        print(
            f"{transition}: {percentage}%"
        )

    print(
        f"\nTransition Map Saved : {transition_map_path}"
    )

    print(
        f"Transition JSON Saved: {json_path}"
    )

    return final_results


if __name__ == "__main__":

    results = analyze_dynamic_world_transitions()

    print("\n========== FINAL RESULTS ==========\n")

    print(json.dumps(results, indent=4))