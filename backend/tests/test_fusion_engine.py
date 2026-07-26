from pprint import pprint

from backend.models.fusion_engine import FusionEngine


def main():

    fusion = FusionEngine()

    # --------------------------------------------------
    # Mock Prithvi
    # --------------------------------------------------

    prithvi_results = {
        "before": {
            "forest": 80,
            "road": 10,
            "river": 10,
        },
        "after": {
            "forest": 60,
            "road": 30,
            "river": 10,
        },
    }

    # --------------------------------------------------
    # Mock Dynamic World
    # --------------------------------------------------

    dynamic_world_results = {
        "trees": {
            "before": 82,
            "after": 63,
            "change": -19,
        },
        "built_area": {
            "before": 8,
            "after": 27,
            "change": 19,
        },
        "water": {
            "before": 10,
            "after": 10,
            "change": 0,
        },
    }

    # --------------------------------------------------
    # Mock ChangeStar
    # --------------------------------------------------

    changestar_results = {
        "change_percentage": 18.7
    }

    # --------------------------------------------------
    # Mock Grounding DINO
    # --------------------------------------------------

    grounding_dino_results = {

        "before": [
            {"label": "building"},
            {"label": "building"},
            {"label": "road"},
        ],

        "after": [
            {"label": "building"},
            {"label": "building"},
            {"label": "building"},
            {"label": "road"},
            {"label": "vehicle"},
        ],

        "statistics": {

            "before_counts": {
                "building": 2,
                "road": 1,
            },

            "after_counts": {
                "building": 3,
                "road": 1,
                "vehicle": 1,
            },

            "differences": {
                "building": 1,
                "vehicle": 1,
                "road": 0,
            },

            "total_before": 3,
            "total_after": 5,
        },
    }

    # --------------------------------------------------
    # Mock Semantic
    # --------------------------------------------------

    semantic_results = {
        "summary": "Forest converted into built-up area."
    }

    # --------------------------------------------------
    # Mock OSINT
    # --------------------------------------------------

    osint_results = {
        "summary": "Construction activity reported."
    }

    result = fusion.fuse(
        prithvi_results,
        dynamic_world_results,
        changestar_results,
        grounding_dino_results,
        semantic_results,
        osint_results,
    )

    print("\n")
    print("=" * 80)
    print("FUSION OUTPUT")
    print("=" * 80)

    pprint(result)


if __name__ == "__main__":
    main()