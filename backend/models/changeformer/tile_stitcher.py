import os
import cv2
import numpy as np


def stitch_tiles(
    prediction_folder,
    output_path,
    image_width,
    image_height,
    tile_size=256
):
    """
    Stitch ChangeFormer prediction tiles into one full-resolution mask.

    Expected filenames:

        tile_0000_0000.png
        tile_0000_0256.png
        tile_0256_0000.png
        ...

    Parameters
    ----------
    prediction_folder : str
        Folder containing predicted tile masks.

    output_path : str
        Path where the stitched mask will be saved.

    image_width : int
        Original image width.

    image_height : int
        Original image height.

    tile_size : int
        Tile size used during inference.
    """

    print("\n" + "=" * 60)
    print("Stitching ChangeFormer Tiles")
    print("=" * 60)

    canvas = np.zeros(
        (image_height, image_width),
        dtype=np.uint8
    )

    tile_count = 0

    prediction_files = sorted(
        [
            f for f in os.listdir(prediction_folder)
            if f.endswith(".png") and f.startswith("tile_")
        ]
    )

    print(f"Prediction Tiles Found : {len(prediction_files)}")

    for filename in prediction_files:

        parts = filename.replace(".png", "").split("_")

        if len(parts) != 3:
            print(f"Skipping invalid filename: {filename}")
            continue

        try:
            y = int(parts[1])
            x = int(parts[2])
        except ValueError:
            print(f"Invalid coordinates in {filename}")
            continue

        filepath = os.path.join(
            prediction_folder,
            filename
        )

        tile = cv2.imread(
            filepath,
            cv2.IMREAD_UNCHANGED
        )

        if tile is None:
            print(f"Failed to read: {filename}")
            continue

        # -------------------------------------------------
        # Convert to single channel if necessary
        # -------------------------------------------------

        if tile.ndim == 3:

            if tile.shape[2] == 1:

                tile = tile[:, :, 0]

            else:

                tile = cv2.cvtColor(
                    tile,
                    cv2.COLOR_BGR2GRAY
                )

        tile = np.squeeze(tile)

        if tile.ndim != 2:
            raise ValueError(
                f"Unexpected tile shape: {tile.shape}"
            )

        # -------------------------------------------------
        # Handle edge tiles
        # -------------------------------------------------

        h = min(tile_size, image_height - y)
        w = min(tile_size, image_width - x)

        canvas[
            y:y + h,
            x:x + w
        ] = tile[
            :h,
            :w
        ]

        tile_count += 1

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    print("\n==============================")
    print("STITCH DEBUG")
    print("==============================")
    print("Image Width  :", image_width)
    print("Image Height :", image_height)
    print("Canvas Shape :", canvas.shape)
    print("Output Path  :", output_path)

    cv2.imwrite(
        output_path,
        canvas
    )

    print("\n" + "-" * 40)
    print("Tile Stitching Complete")
    print("-" * 40)
    print(f"Tiles Stitched : {tile_count}")
    print(f"Saved To       : {output_path}")
    print("=" * 60)

    return output_path