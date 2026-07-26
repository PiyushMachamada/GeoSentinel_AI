def analyze_land_cover_change(segformer_results):

    findings = []

    forest_change = segformer_results.get(
        "forest",
        {}
    ).get("change", 0)

    road_change = segformer_results.get(
        "road",
        {}
    ).get("change", 0)

    residential_change = segformer_results.get(
        "residential_area",
        {}
    ).get("change", 0)

    agriculture_change = segformer_results.get(
        "agricultural_area",
        {}
    ).get("change", 0)

    river_change = segformer_results.get(
        "river",
        {}
    ).get("change", 0)

    # Major forest loss

    if forest_change < -20:

        findings.append(
            "Significant reduction in forest cover detected."
        )

    # Residential expansion

    if residential_change > 1:

        findings.append(
            "Residential development increased."
        )

    # Road growth

    if road_change > 5:

        findings.append(
            "Road infrastructure expanded."
        )

    # Agriculture only if large

    if agriculture_change > 20:

        findings.append(
            "Agricultural land expanded."
        )

    # River only if very large

    if river_change > 30:

        findings.append(
            "Waterbody expansion detected."
        )

    # Combined interpretation

    if (
        forest_change < -20
        and road_change > 5
    ):

        findings.append(
            "The landscape appears to be transitioning from natural vegetation to developed land."
        )

    return findings

def analyze_change_mask_by_class(
    seg_before,
    seg_after,
    change_mask
):
    pass