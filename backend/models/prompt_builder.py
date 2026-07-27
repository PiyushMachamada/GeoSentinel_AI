from backend.models.evidence_formatter import EvidenceFormatter


def build_intelligence_prompt(
    prithvi_results,
    changestar_results,
    fusion_results,
    transition_results,
    geospatial_results,
    dynamic_world_results,
    dynamic_world_transition_results,
    osint_summary,
    mission_confidence,
    reliability_results,
    mission_assessment,
    historical_results,
    aoi_context=None,
):
    """
    Build the intelligence prompt for Qwen.

    The prompt is designed as a structured intelligence briefing rather
    than a collection of raw model outputs.
    """

    formatter = EvidenceFormatter()

    sections = []

    # ==========================================================
    # SYSTEM ROLE
    # ==========================================================

    sections.append("""
You are the Senior Geospatial Intelligence (GEOINT) Analyst for GeoSentinel AI.

Your responsibility is to analyze multi-source Earth Observation evidence and produce a professional intelligence assessment.

Use ONLY the supplied evidence.

Never invent:

- observations
- objects
- land-cover classes
- transitions
- confidence
- activities

If evidence conflicts,
explicitly explain the disagreement.

Never interpret pixel difference as confirmed structural change without corroboration.

If water level, tide, sediment, clouds, seasonality, or vegetation cycle could explain an observation,
state that explicitly.

If models disagree, use the exact phrase:
"Evidence is conflicting."

If evidence is insufficient,
recommend continued monitoring.

Your writing style must be:

- objective
- concise
- scientific
- intelligence focused
""")

    if aoi_context:
        sections.append(f"""
==================================================
AOI CONTEXT
==================================================

AOI ID:
{aoi_context.get("id", "Unknown")}

AOI Name:
{aoi_context.get("name", "Unknown")}

AOI Category:
{aoi_context.get("mission_type", "Unknown")}

AOI-specific reasoning priorities:
- airport: runway, terminal, aircraft, hangar, fuel infrastructure, cargo activity
- port: ships, containers, cranes, docks, dredging, oil storage
- urban: roads, buildings, parking, construction, industrial expansion
- forest: clearing, logging roads, burn scars, vehicles, pipelines
- military: aircraft, bunkers, missile systems, vehicles, radar, logistics
""")

    # ==========================================================
    # MISSION CONTEXT
    # ==========================================================

    sections.append("""
==================================================
MISSION CONTEXT
==================================================

Mission Type:
Persistent Earth Observation

Objective:
Detect meaningful environmental or infrastructure changes
between two satellite observations.

Evidence Sources:

• Prithvi EO 2
• ChangeStar2
• Dynamic World
• Grounding DINO
• Semantic Change Analysis
• Geospatial Metadata
• Open Source Intelligence
• Fusion Engine

The Fusion Engine has already performed cross-model reasoning.
Prioritize the fusion assessment whenever multiple models agree.
""")

    # ==========================================================
    # EXECUTIVE EVIDENCE SUMMARY
    # ==========================================================

    sections.append("""
==================================================
EXECUTIVE EVIDENCE SUMMARY
==================================================
""")

    if fusion_results:

        mission_summary = fusion_results.get(
            "mission_summary",
            "No mission summary available."
        )

        assessment = fusion_results.get(
            "assessment",
            "Unknown"
        )

        agreement_score = fusion_results.get(
            "model_agreement_score",
            0
        )

        structural_change = fusion_results.get(
            "structural_change",
            0,
        )

        mission_change = fusion_results.get(
            "change_percentage",
            0,
        )

        sections.append(
            f"Mission Summary:\n{mission_summary}\n"
        )

        sections.append(
            f"Overall Assessment: {assessment}"
        )

        sections.append(
            f"Model Agreement Score: {agreement_score:.2f}%"
        )

        sections.append(
            f"Overall Evidence Score: {fusion_results.get('overall_evidence_score',0):.2f}%"
        )

        sections.append(
            f"Estimated Structural Change: {structural_change:.2f}%"
        )

        sections.append(
            f"Combined Mission Change Estimate: {mission_change:.2f}%"
        )
        sections.append(
            f"Cloud Coverage: {fusion_results.get('preprocessing', {}).get('cloud_fraction', {}).get('average', 0):.2f}%"
        )
        sections.append(
            f"Water Influence: {fusion_results.get('preprocessing', {}).get('water_fraction', {}).get('average', 0):.2f}%"
        )

    else:

        sections.append(
            "Fusion summary unavailable."
        )

    # ==========================================================
    # CHANGE EVIDENCE
    # ==========================================================

    sections.append("""
    ==================================================
    CHANGE EVIDENCE
    ==================================================
    """)

    if fusion_results:

        structural_change = fusion_results.get(
            "structural_change",
            changestar_results.get(
                "change_percentage",
                0,
            ),
        )

        pixel_change = fusion_results.get(
            "ssim_change_percentage",
            0,
        )

        mission_change = fusion_results.get(
            "change_percentage",
            0,
        )

        sections.append(
            f"Structural Change (ChangeStar2): {structural_change:.2f}%"
        )

        sections.append(
            f"Pixel-Level Change (SSIM): {pixel_change:.2f}%"
        )

        sections.append(
            f"Combined Mission Change Estimate: {mission_change:.2f}%"
        )

        sections.append("""

    REPORTING RULES

    • Structural Change refers ONLY to ChangeStar2.

    • Pixel-Level Change refers ONLY to SSIM.

    • Combined Mission Change Estimate is the overall mission change.

    Never describe Structural Change as the overall mission change.

    The Executive Summary MUST report the Combined Mission Change Estimate.

    When discussing infrastructure or land-cover evolution,
    reference the Structural Change value.

    When discussing image differences,
    reference the Pixel-Level Change value.

    """)

    else:

        sections.append(
            "No change evidence available."
        )

    # ==========================================================
    # VALIDATED INTELLIGENCE
    # ==========================================================

    sections.append("""
    ==================================================
    VALIDATED INTELLIGENCE
    ==================================================
    """)

    if fusion_results:

        sections.append(
            f"Mission Summary: {fusion_results.get('mission_summary','Unknown')}"
        )

        sections.append(
            f"Fusion Assessment: {fusion_results.get('assessment','Unknown')}"
        )

        sections.append(
            f"Model Agreement Score: {fusion_results.get('model_agreement_score',0):.2f}%"
        )

        sections.append(
            "Treat the Fusion Engine assessment as the primary intelligence conclusion."
        )

    else:

        sections.append(
            "Validated intelligence unavailable."
        )

    # ==========================================================
    # MODEL AGREEMENT
    # ==========================================================

    sections.append("""
==================================================
MODEL AGREEMENT
==================================================
""")

    if fusion_results:

        agreement = fusion_results.get(
            "agreement",
            False
        )

        conflicts = fusion_results.get(
            "conflicts",
            []
        )

        if agreement:

            sections.append(
                "Prithvi EO and Dynamic World show strong agreement."
            )

        else:

            sections.append(
                "Prithvi EO and Dynamic World disagree."
            )

        if conflicts:

            sections.append("\nDetected Conflicts:")

            for conflict in conflicts:

                sections.append(
                    f"- {conflict}"
                )

        else:

            sections.append(
                "No significant conflicts detected."
            )

    else:

        sections.append(
            "Agreement analysis unavailable."
        )

    # ==========================================================
    # FUSION ENGINE SUMMARY
    # ==========================================================

    sections.append("""
==================================================
FUSION ENGINE SUMMARY
==================================================
""")

    if fusion_results:

        sections.append(
            formatter.format(fusion_results)
        )

    else:

        sections.append(
            "Fusion evidence unavailable."
        )


        # ==========================================================
    # LAND COVER EVIDENCE
    # ==========================================================

    sections.append("""
==================================================
LAND COVER EVIDENCE
==================================================
""")

    if prithvi_results:

        sections.append("Prithvi EO 2.0")

        before = prithvi_results.get("before", {})
        after = prithvi_results.get("after", {})
        comparison = prithvi_results.get("comparison", {})

        sections.append("\nCurrent Land Cover")

        for cls, value in sorted(
            after.items(),
            key=lambda x: x[1],
            reverse=True
        ):

            sections.append(
                f"{cls}: {value:.2f}%"
            )

        sections.append("\nDetected Change")

        for cls, value in sorted(
            comparison.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        ):

            sign = "+" if value >= 0 else ""

            sections.append(
                f"{cls}: {sign}{value:.2f}%"
            )

    else:

        sections.append(
            "No Prithvi EO analysis available."
        )

    # ==========================================================
    # CHANGE DETECTION EVIDENCE
    # ==========================================================

    sections.append("""
==================================================
CHANGESTAR2 CHANGE DETECTION
==================================================
""")

    if changestar_results:

        sections.append(
            f"Estimated Structural Change: "
            f"{changestar_results.get('change_percentage',0):.2f}%"
        )

        sections.append(
            f"Model Confidence: "
            f"{changestar_results.get('confidence',0):.2f}"
        )

    else:

        sections.append(
            "No ChangeStar evidence available."
        )

    # ==========================================================
    # SEMANTIC CHANGE
    # ==========================================================

    sections.append("""
==================================================
SEMANTIC CHANGE ANALYSIS
==================================================
""")

    if transition_results:

        sections.append(
            "Detected Semantic Transitions"
        )

        for transition, percentage in sorted(

            transition_results.items(),

            key=lambda x: x[1],

            reverse=True

        )[:10]:

            sections.append(
                f"{transition}: {percentage:.2f}%"
            )

    else:

        sections.append(
            "No semantic transitions detected."
        )

    # ==========================================================
    # DYNAMIC WORLD
    # ==========================================================

    sections.append("""
==================================================
DYNAMIC WORLD LAND COVER
==================================================
""")

    if dynamic_world_results:

        for cls, values in dynamic_world_results.items():

            if isinstance(values, dict):

                before = values.get(
                    "before",
                    0
                )

                after = values.get(
                    "after",
                    0
                )

                change = values.get(
                    "change",
                    0
                )

                sign = "+" if change >= 0 else ""

                sections.append(

                    f"{cls}: "

                    f"{before:.2f}% → "

                    f"{after:.2f}% "

                    f"({sign}{change:.2f}%)"

                )

    else:

        sections.append(
            "No Dynamic World analysis available."
        )

    # ==========================================================
    # DYNAMIC WORLD TRANSITIONS
    # ==========================================================

    sections.append("""
==================================================
DYNAMIC WORLD TRANSITIONS
==================================================
""")

    if (
        isinstance(dynamic_world_transition_results, dict)
        and
        "summary" in dynamic_world_transition_results
    ):

        summary = dynamic_world_transition_results["summary"]

        sections.append(
            f"Overall Change: "
            f"{summary.get('change_percentage',0):.2f}%"
        )

        sections.append(
            f"Changed Pixels: "
            f"{summary.get('changed_pixels',0)}"
        )

        sections.append(
            f"Dominant Transition: "
            f"{summary.get('dominant_transition','Unknown')}"
        )

        sections.append("")

        transitions = dynamic_world_transition_results.get(
            "transitions",
            {}
        )

        for transition, percentage in sorted(

            transitions.items(),

            key=lambda x: x[1],

            reverse=True

        )[:10]:

            sections.append(
                f"{transition}: {percentage:.2f}%"
            )

    else:

        sections.append(
            "No Dynamic World transition evidence available."
        )

    # ==========================================================
    # OBJECT DETECTION EVIDENCE
    # ==========================================================

    sections.append("""
==================================================
OBJECT DETECTION EVIDENCE
==================================================
""")

    if fusion_results:

        object_evidence = fusion_results.get(
            "object_evidence",
            {}
        )

        statistics = object_evidence.get(
            "statistics",
            {}
        )

        if statistics:

            sections.append(
                "Detected Object Statistics"
            )

            for label, value in statistics.items():

                if isinstance(value, (int, float)):

                    sections.append(
                        f"{label}: {value}"
                    )

                elif isinstance(value, dict):

                    before = value.get("before", 0)
                    after = value.get("after", 0)

                    sections.append(
                        f"{label}: before={before}, after={after}"
                    )
        else:

            before_objects = object_evidence.get(
                "before",
                []
            )

            after_objects = object_evidence.get(
                "after",
                []
            )

            sections.append(
                f"Objects BEFORE: {len(before_objects)}"
            )

            sections.append(
                f"Objects AFTER : {len(after_objects)}"
            )

    else:

        sections.append(
            "No Grounding DINO evidence available."
        )

        # ==========================================================
    # GEOSPATIAL CONTEXT
    # ==========================================================

    sections.append("""
==================================================
GEOSPATIAL CONTEXT
==================================================
""")

    if geospatial_results:

        for key, value in geospatial_results.items():

            sections.append(
                f"{key}: {value}"
            )

    else:

        sections.append(
            "No geospatial metadata available."
        )

    # ==========================================================
    # OPEN SOURCE INTELLIGENCE
    # ==========================================================

    sections.append("""
==================================================
OPEN SOURCE INTELLIGENCE
==================================================
""")

    if isinstance(osint_summary, dict):

        google_news = len(
            osint_summary.get("google_news", [])
        )

        government = len(
            osint_summary.get("government", [])
        )

        twitter = len(
            osint_summary.get("twitter", [])
        )

        sections.append(
            f"Google News Articles: {google_news}"
        )

        sections.append(
            f"Government Reports: {government}"
        )

        sections.append(
            f"Twitter/X Posts: {twitter}"
        )

    else:

        sections.append(
            "No OSINT evidence available."
        )

    # ==========================================================
    # CONFIDENCE BASIS
    # ==========================================================

    sections.append("""
==================================================
CONFIDENCE BASIS
==================================================

Base your confidence assessment ONLY on the evidence provided.

Consider:

• Agreement between Prithvi EO and Dynamic World

• Structural change detected by ChangeStar2

• Semantic transition consistency

• Grounding DINO object detections

• Fusion Engine reasoning

• Geospatial consistency

• Supporting OSINT evidence

Never invent confidence.

If multiple independent sources agree,
confidence should increase.

If evidence conflicts,
confidence should decrease and explain why.
""")
    

    # ==========================================================
    # EVIDENCE RELIABILITY
    # ==========================================================

    sections.append("""
    ==================================================
    EVIDENCE RELIABILITY
    ==================================================
    """)

    if reliability_results:

        overall = reliability_results.get("overall")

        for key, result in reliability_results.items():

            if key == "overall":
                continue

            sections.append(
                f"{result.model}: {result.score * 100:.1f}%"
            )

        if overall:

            sections.append(
                f"\nOverall Evidence Reliability: {overall.score * 100:.1f}%"
            )

    else:

        sections.append(
            "Evidence reliability unavailable."
    )

    # ==========================================================
    # MISSION CONFIDENCE
    # ==========================================================

    sections.append(f"""
    ==================================================
    MISSION CONFIDENCE
    ==================================================

    Mission Confidence Score : {mission_confidence.score:.2f}%

    Confidence Level : {mission_confidence.level}

    Reasoning :
    {mission_confidence.reasoning}

    This confidence assessment has already been validated
    by the GeoSentinel pipeline.

    Do NOT assign a different confidence level.

    Explain this confidence using the supplied evidence.
    """)

    # ==========================================================
    # FINAL TASK
    # ==========================================================

    sections.append("""
==================================================
TASK
==================================================

Generate a professional GEOINT intelligence report.

The report MUST contain the following sections exactly.

1. Executive Summary

Provide a concise overview of the mission and the most important observations.

-----------------------------------------

2. Key Findings

Summarize the major observations supported by multiple evidence sources.

Mention important agreements and disagreements.

-----------------------------------------

3. Land Cover Assessment

Discuss the observed land-cover characteristics.

Use both:

- Prithvi EO
- Dynamic World

Explain whether they agree.

-----------------------------------------

4. Change Assessment

Discuss all three independently:

• Structural Change (ChangeStar2)

• Pixel-Level Change (SSIM)

• Combined Mission Change Estimate

Explain why these values may differ.

Do not replace one metric with another.

Describe the most likely change process.

Avoid unsupported conclusions.

-----------------------------------------

5. Confidence Assessment

Use ONLY one of the following:

Very High

High

Moderate

Low

Very Low

Do NOT generate a percentage.

Explain WHY this confidence level was assigned.

-----------------------------------------

6. Recommendations

Provide practical recommendations.

Possible examples:

- Continue monitoring

- Acquire higher-resolution imagery

- Compare future observations

- Verify with field observations

- Monitor infrastructure development

Recommendations must be supported by the evidence.

-----------------------------------------

Writing Style

Write like a professional GEOINT analyst.

Be:

• concise

• objective

• scientific

• evidence driven

Do NOT:

• invent observations

• invent detected objects

• invent land-cover classes

• invent transitions

• invent activities

If evidence is insufficient,
clearly state the uncertainty.

Always prioritize the Fusion Engine assessment when independent models agree.

The report should read as a professional intelligence assessment rather than a list of model outputs.
""")

    return "\n\n".join(sections)