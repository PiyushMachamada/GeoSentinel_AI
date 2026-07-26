class OSINTQueryBuilder:

    def __init__(self):
        print("OSINT Query Builder Initialized")

    def build(
        self,
        prithvi_results,
        dynamic_world_results,
        transition_results,
        geospatial_results
    ):

        # =====================================================
        # LOCATION
        # =====================================================

        location = ""

        if isinstance(geospatial_results, dict):
            location = geospatial_results.get(
                "location",
                ""
            )

        # =====================================================
        # EVENT DETECTION (Dynamic World has highest priority)
        # =====================================================

        event = "Satellite Event"

        if (
            isinstance(dynamic_world_results, dict)
            and len(dynamic_world_results) > 0
        ):

            dominant = max(
                dynamic_world_results,
                key=lambda x: abs(
                    dynamic_world_results[x].get(
                        "change",
                        0
                    )
                )
            ).lower()

            if "water" in dominant:
                event = "Flood"

            elif "tree" in dominant:
                event = "Forest Change"

            elif "grass" in dominant:
                event = "Wildfire"

            elif "built" in dominant:
                event = "Urban Development"

            elif "crop" in dominant:
                event = "Agricultural Change"

        # =====================================================
        # FALLBACK TO PRITHVI IF DYNAMIC WORLD IS UNAVAILABLE
        # =====================================================

        elif (
            isinstance(prithvi_results, dict)
            and "comparison" in prithvi_results
        ):

            comparison = prithvi_results["comparison"]

            if len(comparison) > 0:

                dominant = max(
                    comparison,
                    key=lambda x: abs(comparison[x])
                ).lower()

                if "river" in dominant:
                    event = "Flood"

                elif "forest" in dominant:
                    event = "Forest Change"

                elif "road" in dominant:
                    event = "Road Construction"

                elif "residential" in dominant:
                    event = "Urban Expansion"

                elif "agricultural" in dominant:
                    event = "Agricultural Change"

        # =====================================================
        # SEMANTIC TRANSITION
        # =====================================================

        transition = ""

        if (
            isinstance(transition_results, dict)
            and len(transition_results) > 0
        ):

            dominant_transition = max(
                transition_results,
                key=transition_results.get
            )

            transition = dominant_transition.replace(
                "_",
                " "
            )

        # =====================================================
        # FINAL QUERY
        # =====================================================

        query_parts = [
            event,
            transition,
            location
        ]

        query = " ".join(
            part.strip()
            for part in query_parts
            if part and part.strip()
        )

        return query