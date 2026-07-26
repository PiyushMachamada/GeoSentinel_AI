import json


def compare_segmentation(before_stats, after_stats):

    comparison = {}

    all_classes = set(
        before_stats.keys()
    ).union(
        set(after_stats.keys())
    )

    print("\nSegFormer Change Analysis")
    print("=" * 40)

    for cls in sorted(all_classes):

        before = before_stats.get(
            cls,
            0
        )

        after = after_stats.get(
            cls,
            0
        )

        delta = round(
            after - before,
            2
        )

        comparison[cls] = {
            "before": before,
            "after": after,
            "change": delta
        }

        sign = "+" if delta >= 0 else ""

        print(
            f"{cls}: "
            f"{before:.2f}% -> "
            f"{after:.2f}% "
            f"({sign}{delta:.2f}%)"
        )

    with open(
        "backend/outputs/segformer_report.json",
        "w"
    ) as file:

        json.dump(
            comparison,
            file,
            indent=4
        )

    print(
        "\nSegFormer report saved!"
    )

    return comparison