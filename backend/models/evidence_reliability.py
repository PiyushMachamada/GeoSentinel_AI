from dataclasses import dataclass


@dataclass
class ReliabilityScore:
    model: str
    score: float
    reasoning: str


class EvidenceReliabilityEngine:
    """
    Computes reliability scores for every AI model contributing
    to GeoSentinel's intelligence pipeline.

    Reliability is independent of mission confidence.

    It answers:

        "How trustworthy is this model's evidence?"
    """

    def __init__(self):
        print("\nLoading Evidence Reliability Engine")

    def compute(
        self,
        grounding_dino_results,
        prithvi_results,
        dynamic_world_results,
        changestar_results,
    ):

        reliability = {}

        # --------------------------------------------------
        # Grounding DINO
        # --------------------------------------------------

        statistics = grounding_dino_results.get(
            "statistics",
            {},
        )

        gdino_score = statistics.get(
            "overall_average_confidence",
            0.5,
        )

        reliability["grounding_dino"] = ReliabilityScore(
            model="Grounding DINO",
            score=round(gdino_score, 2),
            reasoning="Based on average object detection confidence.",
        )

        # --------------------------------------------------
        # Prithvi EO 2
        # --------------------------------------------------

        dominant = max(
            prithvi_results["after"].values()
        )

        prithvi_score = dominant / 100

        reliability["prithvi"] = ReliabilityScore(
            model="Prithvi EO 2",
            score=round(prithvi_score, 2),
            reasoning="Based on dominant semantic segmentation confidence.",
        )

        # --------------------------------------------------
        # Dynamic World
        # --------------------------------------------------

        after = {}

        for cls, values in dynamic_world_results.items():
            after[cls] = values.get("after", 0)

        dw_score = max(after.values()) / 100

        reliability["dynamic_world"] = ReliabilityScore(
            model="Dynamic World",
            score=round(dw_score, 2),
            reasoning="Based on dominant Dynamic World land-cover percentage.",
        )

        # --------------------------------------------------
        # ChangeStar2
        # --------------------------------------------------

        changestar_score = float(
            changestar_results.get(
                "confidence",
                0.5,
            )
        )

        reliability["changestar"] = ReliabilityScore(
            model="ChangeStar2",
            score=round(changestar_score, 2),
            reasoning="Based on ChangeStar prediction confidence.",
        )

        # --------------------------------------------------
        # Overall Reliability
        # --------------------------------------------------

        scores = [
            item.score
            for item in reliability.values()
        ]

        overall = round(
            sum(scores) / len(scores),
            2,
        )

        reliability["overall"] = ReliabilityScore(
            model="Overall",
            score=overall,
            reasoning="Average reliability across all AI models.",
        )

        return reliability