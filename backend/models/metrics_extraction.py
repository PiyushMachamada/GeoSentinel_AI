def extract_metrics(
    segformer_results,
    changeformer_results,
    transition_results,
    fusion_results
):

    metrics = {}

    # -----------------------------
    # SegFormer Changes
    # -----------------------------

    for class_name, values in segformer_results.items():

        before = values.get("before", 0)
        after = values.get("after", 0)

        metrics[f"{class_name}_before"] = before
        metrics[f"{class_name}_after"] = after
        metrics[f"{class_name}_change"] = round(
            after - before,
            2
        )

    # -----------------------------
    # ChangeFormer
    # -----------------------------

    metrics["change_percentage"] = (
        changeformer_results.get(
            "change_percentage",
            0
        )
    )

    # -----------------------------
    # Dominant Transition
    # -----------------------------

    if transition_results:

        dominant_transition = max(
            transition_results,
            key=transition_results.get
        )

        metrics["dominant_transition"] = (
            dominant_transition
        )

        metrics["dominant_transition_percent"] = (
            transition_results[dominant_transition]
        )

    # -----------------------------
    # Fusion
    # -----------------------------

    metrics["changed_pixels"] = (
        fusion_results.get(
            "total_changed_pixels",
            0
        )
    )

    return metrics