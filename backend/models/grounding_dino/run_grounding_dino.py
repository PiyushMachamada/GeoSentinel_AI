from pathlib import Path
from backend.monitoring.aoi_manager import AOIManager
from backend.models.grounding_dino.grounding_dino_model import (
    GroundingDINOModel,
)

# ==========================================================
# Configuration
# ==========================================================

ROOT = Path(__file__).resolve().parents[3]

IMAGE = (
    ROOT
    / "backend"
    / "outputs"
    / "model_inputs"
    / "before_geotiff.png"
)

ANNOTATED_OUTPUT = (
    ROOT
    / "backend"
    / "outputs"
    / "grounding_dino_before.png"
)

JSON_OUTPUT = (
    ROOT
    / "backend"
    / "outputs"
    / "grounding_dino_before.json"
)

# ==========================================================
# AOI Configuration
# ==========================================================

TEST_AOI = "AOI001"

# ==========================================================
# Main
# ==========================================================


def main():

    aoi = AOIManager().get_by_id(TEST_AOI)

    if aoi is None:
        raise ValueError(f"Unknown AOI: {TEST_AOI}")

    print("\n" + "=" * 70)
    print("GROUNDING DINO TEST")
    print("=" * 70)
    print(f"AOI ID       : {aoi.id}")
    print(f"AOI Name     : {aoi.name}")
    print(f"Mission Type : {aoi.mission_type}")
    print(f"Image        : {IMAGE}")
    print("=" * 70)

    model = GroundingDINOModel()

    detections = model.predict(
        image_path=str(IMAGE),
        aoi_type=aoi.mission_type,
    )

    print("\n===== DETECTIONS =====")

    if not detections:

        print("No detections found.")

    else:

        print(f"\nTotal Objects Detected : {len(detections)}\n")

        for index, detection in enumerate(
            detections,
            start=1,
        ):

            print(f"{index}. {detection}")

            JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            ANNOTATED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------
    # Save JSON
    # ------------------------------------------------------

    model.save_detections_json(
        detections=detections,
        output_path=str(JSON_OUTPUT),
    )

    print("\nDetection JSON saved:")
    print(JSON_OUTPUT)

    # ------------------------------------------------------
    # Save Annotated Image
    # ------------------------------------------------------

    model.save_annotated_image(
        image_path=str(IMAGE),
        detections=detections,
        output_path=str(ANNOTATED_OUTPUT),
    )

    print("\nAnnotated image saved:")
    print(ANNOTATED_OUTPUT)

    print("\n" + "=" * 70)
    print("GROUNDING DINO TEST COMPLETE")
    print("=" * 70)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()