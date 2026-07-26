class EvidenceFormatter:
    """
    Converts the Fusion Engine output into a human-readable
    intelligence evidence brief for Qwen.
    """

    def format(self, fusion_results):

        sections = [

            self._format_mission_summary(fusion_results),

            self._format_land_cover(fusion_results),

            self._format_change(fusion_results),

            self._format_objects(fusion_results),

            self._format_agreement(fusion_results),

            self._format_conflicts(fusion_results),

            self._format_osint(fusion_results),

        ]

        return "\n\n".join(
            section for section in sections if section
        )

    # =====================================================
    # Mission Summary
    # =====================================================

    def _format_mission_summary(self, fusion_results):

        summary = fusion_results.get(
            "mission_summary",
            "Mission summary unavailable."
        )

        return f"""
==================================================
MISSION SUMMARY
==================================================

{summary}
""".strip()

    # =====================================================
    # Land Cover
    # =====================================================

    def _format_land_cover(self, fusion_results):

        evidence = fusion_results.get(
            "land_cover_evidence",
            {}
        )

        prithvi = evidence.get("prithvi", {})
        dynamic = evidence.get("dynamic_world", {})

        agreement = "Yes" if evidence.get(
            "agreement",
            False
        ) else "No"

        return f"""
==================================================
LAND COVER EVIDENCE
==================================================

Prithvi EO 2.0

Dominant Class : {prithvi.get("dominant_class","Unknown")}
Coverage       : {prithvi.get("coverage",0)}%

Dynamic World

Dominant Class : {dynamic.get("dominant_class","Unknown")}
Coverage       : {dynamic.get("coverage",0)}%

Agreement : {agreement}
""".strip()

    # =====================================================
    # Structural Change
    # =====================================================

    def _format_change(self, fusion_results):

        change = fusion_results.get(
            "change_evidence",
            {}
        )

        return f"""
==================================================
STRUCTURAL CHANGE
==================================================

Change Percentage : {change.get("change_percentage",0)}%

Severity          : {change.get("severity","Unknown")}

Transition        : {change.get("transition","Unknown")}
""".strip()

    # =====================================================
    # Objects
    # =====================================================

    def _format_objects(self, fusion_results):

        statistics = (
            fusion_results
            .get("object_evidence", {})
            .get("statistics", {})
        )

        before = statistics.get(
            "before_counts",
            {}
        )

        after = statistics.get(
            "after_counts",
            {}
        )

        differences = statistics.get(
            "differences",
            {}
        )

        lines = [

            "==================================================",
            "OBJECT DETECTIONS",
            "==================================================",
            "",
            "BEFORE",
            ""
        ]

        if before:

            for obj, count in sorted(before.items()):

                lines.append(
                    f"{obj.title():<20} : {count}"
                )

        else:

            lines.append("None")

        lines.extend([
            "",
            "AFTER",
            ""
        ])

        if after:

            for obj, count in sorted(after.items()):

                diff = differences.get(obj, 0)

                if diff > 0:

                    delta = f"(+{diff})"

                elif diff < 0:

                    delta = f"({diff})"

                else:

                    delta = ""

                lines.append(
                    f"{obj.title():<20} : {count} {delta}"
                )

        else:

            lines.append("None")

        return "\n".join(lines)

    # =====================================================
    # Agreement
    # =====================================================

    def _format_agreement(self, fusion_results):

        return f"""
==================================================
MODEL AGREEMENT
==================================================

Agreement Score : {fusion_results.get("agreement_score",0)}

Overall Score   : {fusion_results.get("model_agreement_score",0)}

Assessment      : {fusion_results.get("assessment","Unknown")}
""".strip()

    # =====================================================
    # Conflicts
    # =====================================================

    def _format_conflicts(self, fusion_results):

        conflicts = fusion_results.get(
            "conflicts",
            []
        )

        lines = [

            "==================================================",

            "CONFLICTS",

            "==================================================",

            ""
        ]

        if conflicts:

            for conflict in conflicts:

                lines.append(f"- {conflict}")

        else:

            lines.append("No significant conflicts detected.")

        return "\n".join(lines)

    # =====================================================
    # OSINT
    # =====================================================

    def _format_osint(self, fusion_results):

        osint = fusion_results.get(
            "osint_evidence",
            {}
        )

        summary = osint.get(
            "summary",
            "No supporting OSINT available."
        )

        return f"""
==================================================
OPEN SOURCE INTELLIGENCE
==================================================

{summary}
""".strip()