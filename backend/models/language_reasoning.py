def generate_report(
    segformer_results,
    changeformer_results,
    fusion_results,
    transition_results,
    geospatial_results
):

    report = []

    report.append(
        "GeoSentinel Intelligence Report"
    )

    report.append("=" * 50)
    report.append("")

    # ==================================
    # GEOSPATIAL INFORMATION
    # ==================================

    report.append(
        "Geospatial Information"
    )

    report.append("-" * 50)

    report.append(
        f"CRS: "
        f"{geospatial_results.get('crs', 'Unknown')}"
    )

    report.append(
        f"Image Size: "
        f"{geospatial_results.get('width', 0)} x "
        f"{geospatial_results.get('height', 0)}"
    )

    report.append(
        f"Bands: "
        f"{geospatial_results.get('bands', 0)}"
    )

    report.append(
        f"Resolution X: "
        f"{geospatial_results.get('resolution_x', 0):.2f} m/pixel"
    )

    report.append(
        f"Resolution Y: "
        f"{geospatial_results.get('resolution_y', 0):.2f} m/pixel"
    )

    report.append("")

    report.append("Spatial Bounds")

    bounds = geospatial_results.get(
        "bounds",
        {}
    )

    for key, value in bounds.items():

        report.append(
            f"{key}: {value}"
        )

    report.append("")

    # ==================================
    # CHANGEFORMER
    # ==================================

    report.append(
        "ChangeFormer Analysis"
    )

    report.append("-" * 50)

    report.append(
        f"Detected Change Area: "
        f"{changeformer_results.get('change_percentage', 0)}%"
    )

    report.append(
        f"Status: "
        f"{changeformer_results.get('status', 'Unknown')}"
    )

    report.append("")

    # ==================================
    # FUSION ANALYSIS
    # ==================================

    report.append(
        "Fusion Analysis"
    )

    report.append("-" * 50)

    report.append(
        f"Total Changed Pixels: "
        f"{fusion_results.get('total_changed_pixels', 0)}"
    )

    report.append("")

    report.append(
        "Change Distribution"
    )

    distribution = fusion_results.get(
        "change_distribution",
        {}
    )

    for class_name, percentage in sorted(
        distribution.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        report.append(
            f"{class_name}: {percentage}%"
        )

    report.append("")

    # ==================================
    # TRANSITION ANALYSIS
    # ==================================

    report.append(
        "Land-Cover Transition Analysis"
    )

    report.append("-" * 50)

    top_transitions = sorted(
        transition_results.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    for transition, percentage in top_transitions:

        report.append(
            f"{transition}: {percentage:.2f}%"
        )

    report.append("")

    # ==================================
    # SEGFORMER SUMMARY
    # ==================================

    report.append(
        "SegFormer Land-Cover Analysis"
    )

    report.append("-" * 50)

    for class_name, values in segformer_results.items():

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

            report.append(
                f"{class_name}: "
                f"{before:.2f}% -> "
                f"{after:.2f}% "
                f"({change:+.2f}%)"
            )

    report.append("")

    # ==================================
    # INTELLIGENCE ASSESSMENT
    # ==================================

    report.append(
        "Intelligence Assessment"
    )

    report.append("-" * 50)

    change_percentage = (
        changeformer_results.get(
            "change_percentage",
            0
        )
    )

    forest_change = (
        segformer_results.get(
            "forest",
            {}
        ).get(
            "change",
            0
        )
    )

    agriculture_change = (
        segformer_results.get(
            "agricultural_area",
            {}
        ).get(
            "change",
            0
        )
    )

    road_change = (
        segformer_results.get(
            "road",
            {}
        ).get(
            "change",
            0
        )
    )

    river_change = (
        segformer_results.get(
            "river",
            {}
        ).get(
            "change",
            0
        )
    )

    report.append(
        f"ChangeFormer detected changes across "
        f"{change_percentage:.2f}% of the observed area."
    )

    report.append("")

    if forest_change < 0:

        report.append(
            f"Forest cover decreased by "
            f"{abs(forest_change):.2f}%."
        )

    if agriculture_change > 0:

        report.append(
            f"Agricultural land increased by "
            f"{agriculture_change:.2f}%."
        )

    if river_change > 0:

        report.append(
            f"Waterbody coverage increased by "
            f"{river_change:.2f}%."
        )

    if road_change > 0:

        report.append(
            f"Road infrastructure increased by "
            f"{road_change:.2f}%."
        )

    report.append("")

    if len(transition_results) > 0:

        dominant_transition = max(
            transition_results,
            key=transition_results.get
        )

        dominant_percentage = (
            transition_results[
                dominant_transition
            ]
        )

        report.append(
            f"The dominant land-cover transition "
            f"was {dominant_transition} "
            f"({dominant_percentage:.2f}%)."
        )

    report.append("")

    report.append(
        "Possible interpretations:"
    )

    if river_change > 10:

        report.append(
            "- Flooding, reservoir expansion, or water accumulation."
        )

    if agriculture_change > 10:

        report.append(
            "- Agricultural development or land conversion."
        )

    if road_change > 5:

        report.append(
            "- Infrastructure expansion and human activity."
        )

    if forest_change < -20:

        report.append(
            "- Significant vegetation loss requiring further monitoring."
        )

    report.append("")

    report.append(
        "Further temporal observations are recommended "
        "to determine whether these changes are seasonal, "
        "temporary, or permanent."
    )
    # ==================================
    # SAVE REPORT
    # ==================================

    final_report = "\n".join(
        report
    )

    print("\n")
    print(final_report)

    with open(
        "backend/outputs/intelligence_report.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            final_report
        )

    print(
        "\nIntelligence report saved!"
    )

    return final_report