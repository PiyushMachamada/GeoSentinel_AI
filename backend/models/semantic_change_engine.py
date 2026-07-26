import json
import numpy as np
from pathlib import Path


CLASS_NAMES = {
    0: "background",
    1: "residential_area",
    2: "road",
    3: "river",
    4: "forest",
    5: "unused_land",
    6: "agricultural_area"
}

SEMANTIC_RULES = {

    "Urban Expansion": [
        "forest_to_residential_area",
        "unused_land_to_residential_area",
        "forest_to_road",
        "unused_land_to_road"
    ],

    "Deforestation": [
        "forest_to_unused_land",
        "forest_to_agricultural_area"
    ],

    "Agricultural Expansion": [
        "unused_land_to_agricultural_area",
        "forest_to_agricultural_area"
    ],

    "Flooding": [
        "road_to_river",
        "forest_to_river",
        "agricultural_area_to_river"
    ],

    "River Expansion": [
        "forest_to_river",
        "unused_land_to_river"
    ],

    "Urban Redevelopment": [
        "residential_area_to_road",
        "road_to_residential_area"
    ]
}


class SemanticChangeEngine:

    def __init__(self):
        print("\nLoading Semantic Change Engine...")

    def analyze(self):

        print("\nRunning Semantic Change Analysis...")

        seg_before = np.load("backend/outputs/segmask_before.npy")
        seg_after = np.load("backend/outputs/segmask_after.npy")

        if seg_before.shape != seg_after.shape:
            raise ValueError("Segmentation masks have different sizes.")

        transitions = {}

        changed_pixels = 0

        h, w = seg_before.shape

        for y in range(h):
            for x in range(w):

                before = int(seg_before[y, x])
                after = int(seg_after[y, x])

                if before == after:
                    continue

                changed_pixels += 1

                before_name = CLASS_NAMES.get(before, str(before))
                after_name = CLASS_NAMES.get(after, str(after))

                key = f"{before_name}_to_{after_name}"

                transitions[key] = transitions.get(key, 0) + 1

        total_pixels = h * w

        semantic_change_percentage = round(
            (changed_pixels / total_pixels) * 100,
            2
        )

        if changed_pixels == 0:

            results = {
                "semantic_change_percentage": 0,
                "dominant_transition": None,
                "transitions": {}
            }

        else:

            total_transition_pixels = sum(transitions.values())

            for key in transitions:
                transitions[key] = round(
                    transitions[key] /
                    total_transition_pixels * 100,
                    2
                )

            transitions = dict(
                sorted(
                    transitions.items(),
                    key=lambda item: item[1],
                    reverse=True
                )
            )

            dominant = next(iter(transitions))

            scene = self.interpret_scene(
                transitions
            )

        results = {

            "semantic_change_percentage":
                semantic_change_percentage,

            "dominant_transition":
                dominant,

            "scene_interpretation":
                scene,

            "transitions":
                transitions
        }

        output_dir = Path("backend/outputs")
        output_dir.mkdir(exist_ok=True)

        with open(
            output_dir / "semantic_change_results.json",
            "w"
        ) as f:

            json.dump(results, f, indent=4)

        print("\nSemantic Change Results")

        print(
            f"Semantic Change: "
            f"{semantic_change_percentage}%"
        )

        if results["dominant_transition"]:

            print(
                f"Dominant Transition: "
                f"{results['dominant_transition']}"
            )

        return results
    
    def interpret_scene(self, transitions):

        scores = {}

        for event, rules in SEMANTIC_RULES.items():

            score = 0

            reasons = []

            for rule in rules:

                if rule in transitions:

                    score += transitions[rule]

                    reasons.append(rule)

            scores[event] = {
                "score": round(score, 2),
                "matched_rules": reasons
            }

        if not scores:
            return None

        best_event = max(
            scores,
            key=lambda x: scores[x]["score"]
        )

        return {

            "event": best_event,

            "confidence": round(
                scores[best_event]["score"],
                2
            ),

            "matched_rules":
                scores[best_event]["matched_rules"]

        }