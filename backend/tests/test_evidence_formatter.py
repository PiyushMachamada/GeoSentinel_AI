from backend.models.evidence_formatter import EvidenceFormatter

fusion_results = {
    "mission_summary": (
        "Moderate structural change detected. Forest cover "
        "decreased while built-up area increased."
    ),

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
            "differences": {
                "building": 2,
                "vehicle": 2,
            },
        }
    },

    "agreement_score": 100,

    "model_agreement_score": 98.7,

    "assessment": "Very High Agreement",

    "conflicts": [],

    "osint_evidence": {
        "summary": "Local news reports construction activity."
    },
}

formatter = EvidenceFormatter()

print("=" * 80)
print(formatter.format(fusion_results))