class EvidenceReasoner:

    """
    Performs cross-model evidence reasoning.
    """

    def __init__(self):

        self.class_mapping = {
            "forest": "trees",
            "river": "water",
            "agricultural_area": "crops",
            "residential_area": "built_area",
            "road": "built_area",
            "unused_land": "bare_ground",
            "background": "unknown",
        }

    def reason(
        self,
        evidence_items,
        semantic_results,
        changestar_results,
    ):

        prithvi = None
        dynamic_world = None
        changestar = None

        # ---------------------------------------
        # Locate evidence
        # ---------------------------------------

        for item in evidence_items:

            if item["source"] == "Prithvi EO 2.0":
                prithvi = item

            elif item["source"] == "Dynamic World":
                dynamic_world = item

            elif item["source"] == "ChangeStar2":
                changestar = item

        # ---------------------------------------
        # Prithvi ↔ Dynamic World
        # ---------------------------------------

        if prithvi and dynamic_world:

            expected = self.class_mapping.get(
                prithvi["details"]["class"],
                prithvi["details"]["class"]
            )

            actual = dynamic_world["details"]["class"]

            if expected == actual:

                prithvi["corroborated_by"].append("Dynamic World")
                dynamic_world["corroborated_by"].append("Prithvi EO 2.0")

                prithvi["weight"] += 0.10
                dynamic_world["weight"] += 0.10

            else:

                prithvi["contradicted_by"].append("Dynamic World")
                dynamic_world["contradicted_by"].append("Prithvi EO 2.0")

                prithvi["weight"] -= 0.10
                dynamic_world["weight"] -= 0.10

        # ---------------------------------------
        # ChangeStar corroboration
        # ---------------------------------------

        if changestar:

            change_percentage = float(
                changestar_results.get("change_percentage", 0)
            )

            if change_percentage >= 20:

                changestar["corroborated_by"].append(
                    "Semantic Change Analysis"
                )

                changestar["weight"] += 0.05

            elif change_percentage < 5:

                changestar["uncertainty"] = min(
                    1.0,
                    changestar["uncertainty"] + 0.10
                )

        # ---------------------------------------
        # Semantic reasoning
        # ---------------------------------------

        if semantic_results:

            for item in evidence_items:

                item.setdefault("semantic_support", semantic_results)

        # ---------------------------------------
        # Clamp weights
        # ---------------------------------------

        for item in evidence_items:

            item["weight"] = round(
                max(0.0, min(1.0, item["weight"])),
                2
            )

            item["uncertainty"] = round(
                max(0.0, min(1.0, item["uncertainty"])),
                2
            )

        return evidence_items