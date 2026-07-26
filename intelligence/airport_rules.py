"""
airport_rules.py

Airport-specific intelligence rules.
"""

from intelligence.rule_engine import IntelligenceEvent


def evaluate(
    evidence_collection,
):
    """
    Evaluate airport intelligence rules.
    """

    events = []

    # --------------------------------------------------
    # Aircraft Activity
    # --------------------------------------------------

    aircraft = [

        e

        for e in evidence_collection.by_category(
            "Object Detection"
        )

        if e.metadata.get(
            "label"
        ) in [

            "airplane",

            "helicopter"

        ]

    ]

    if aircraft:

        events.append(

            IntelligenceEvent(

                name="Aircraft Activity",

                confidence=0.90,

                explanation=(
                    f"{len(aircraft)} aircraft detected."
                ),

                supporting_models=[
                    "Grounding DINO"
                ],

                supporting_evidence=aircraft,

            )

        )

    # --------------------------------------------------
    # Airport Expansion
    # --------------------------------------------------

    change = evidence_collection.by_source(
        "ChangeStar"
    )

    if change:

        cp = change[0].metadata.get(
            "change_percentage",
            0
        )

        if cp > 15:

            events.append(

                IntelligenceEvent(

                    name="Airport Expansion",

                    confidence=0.88,

                    explanation=(
                        f"{cp:.2f}% structural change detected."
                    ),

                    supporting_models=[
                        "ChangeStar"
                    ],

                    supporting_evidence=change,

                )

            )

    return events