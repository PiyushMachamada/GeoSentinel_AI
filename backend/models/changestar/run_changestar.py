import json
import sys
from pathlib import Path

from backend.models.changestar.changestar_model import ChangeStarModel


def main():

    if len(sys.argv) not in (3, 4):
        print("Usage:")
        print(
            "python -m backend.models.changestar.run_changestar "
            "before.png after.png [output_directory]"
        )
        return

    before = sys.argv[1]
    after = sys.argv[2]

    # Optional output directory
    if len(sys.argv) != 4:
        raise ValueError(
            "Output directory must be provided by GeoSentinelPipeline."
        )

    output_dir = Path(sys.argv[3])

    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = {
        "changestar_prediction": output_dir / "changestar_prediction.png",
        "changestar_probability": output_dir / "changestar_probability.npy",
    }

    model = ChangeStarModel()

    result = model.predict(
        before,
        after,
        output_paths,
    )

    output = {
        "change_percentage": result["change_percentage"],
        "confidence": result["confidence"],
        "model": result["model"],
        "mask_path": result["mask_path"],
        "probability_map": result["probability_map"],
    }

    json_path = output_dir / "changestar_result.json"

    with open(json_path, "w") as f:
        json.dump(output, f, indent=4)

    print("\n===================================")
    print("ChangeStar2 Complete")
    print("===================================")
    print(json.dumps(output, indent=4))
    print(f"\nSaved metadata to: {json_path}")


if __name__ == "__main__":
    main()