from backend.models.prompt_builder import build_intelligence_prompt


def main():

    prithvi_results = {
        "comparison": {
            "forest": -20.0,
            "road": 15.0,
            "river": 5.0,
        }
    }

    changestar_results = {
        "change_percentage": 18.7,
        "confidence": 0.92,
    }

    fusion_results = {

        "mission_summary":
            "Moderate structural change detected. Forest cover decreased while built-up area increased.",

        "land_cover_evidence": {
            "prithvi": {
                "dominant_class": "forest",
                "coverage": 60,
            },
            "dynamic_world": {
                "dominant_class": "trees",
                "coverage": 63,
            },
            "agreement": True,
        },

        "change_evidence": {
            "change_percentage": 18.7,
            "severity": "Moderate",
            "transition": "forest → built_area",
        },

        "object_evidence": {
            "statistics": {
                "before_counts": {
                    "building": 2,
                },
                "after_counts": {
                    "building": 4,
                    "vehicle": 2,
                },
            }
        },

        "validated_evidence": [
            {
                "source": "Prithvi EO 2.0",
                "finding": "Forest dominant",
                "validation": {
                    "status": "validated"
                },
            }
        ],

        "reasoned_evidence": [
            {
                "source": "Fusion",
                "finding": "Urban expansion supported by multiple models.",
            }
        ],
    }

    transition_results = {
        "forest_to_built_area": 81.3
    }

    geospatial_results = {
        "crs": "EPSG:32643",
        "resolution": "10 m",
    }

    dynamic_world_results = {
        "trees": {
            "before": 80,
            "after": 60,
            "change": -20,
        },
        "built_area": {
            "before": 10,
            "after": 30,
            "change": 20,
        },
    }

    dynamic_world_transition_results = {
        "summary": {
            "changed_pixels": 1456,
            "change_percentage": 18.7,
            "dominant_transition": "trees_to_built_area",
            "dominant_percentage": 81.3,
        },
        "transitions": {
            "trees_to_built_area": 81.3
        },
    }

    osint_summary = {
        "summary":
            "Local news reports construction activity."
    }

    prompt = build_intelligence_prompt(
        prithvi_results,
        changestar_results,
        fusion_results,
        transition_results,
        geospatial_results,
        dynamic_world_results,
        dynamic_world_transition_results,
        osint_summary,
    )

    print("=" * 80)
    print("PROMPT")
    print("=" * 80)
    print(prompt)


if __name__ == "__main__":
    main()