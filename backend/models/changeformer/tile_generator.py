import os
import shutil
import cv2
import numpy as np


def generate_tiles(
    before_image_path,
    after_image_path,
    output_dataset_dir,
    tile_size=256,
    stride=256
):
    """
    Generate paired ChangeFormer tiles from two large images.

    Dataset structure produced:

    temp_dataset/
    ├── A/
    ├── B/
    ├── label/
    └── list/
        └── demo.txt
    """

    print("\n" + "=" * 60)
    print("Generating ChangeFormer Tiles")
    print("=" * 60)

    before = cv2.imread(before_image_path)
    after = cv2.imread(after_image_path)

    if before is None:
        raise FileNotFoundError(before_image_path)

    if after is None:
        raise FileNotFoundError(after_image_path)

    if before.shape != after.shape:
        raise ValueError(
            f"Image size mismatch:\n"
            f"Before: {before.shape}\n"
            f"After : {after.shape}"
        )

    height, width = before.shape[:2]

    print(f"Input Size : {width} x {height}")

    # ---------------------------------------------------------
    # Dataset folders
    # ---------------------------------------------------------

    folder_A = os.path.join(output_dataset_dir, "A")
    folder_B = os.path.join(output_dataset_dir, "B")
    folder_label = os.path.join(output_dataset_dir, "label")
    folder_list = os.path.join(output_dataset_dir, "list")

    # Remove previous dataset
    if os.path.exists(folder_A):
        shutil.rmtree(folder_A)

    if os.path.exists(folder_B):
        shutil.rmtree(folder_B)

    if os.path.exists(folder_label):
        shutil.rmtree(folder_label)

    if os.path.exists(folder_list):
        shutil.rmtree(folder_list)

    os.makedirs(folder_A, exist_ok=True)
    os.makedirs(folder_B, exist_ok=True)
    os.makedirs(folder_label, exist_ok=True)
    os.makedirs(folder_list, exist_ok=True)

    demo_txt = os.path.join(folder_list, "demo.txt")

    tile_count = 0

    with open(demo_txt, "w") as f:

        for y in range(0, height, stride):

            for x in range(0, width, stride):

                before_tile = before[
                    y:y + tile_size,
                    x:x + tile_size
                ]

                after_tile = after[
                    y:y + tile_size,
                    x:x + tile_size
                ]

                # -----------------------------------------
                # Pad edge tiles
                # -----------------------------------------

                h, w = before_tile.shape[:2]

                if h < tile_size or w < tile_size:

                    pad_bottom = tile_size - h
                    pad_right = tile_size - w

                    before_tile = cv2.copyMakeBorder(
                        before_tile,
                        0,
                        pad_bottom,
                        0,
                        pad_right,
                        cv2.BORDER_CONSTANT,
                        value=(0, 0, 0)
                    )

                    after_tile = cv2.copyMakeBorder(
                        after_tile,
                        0,
                        pad_bottom,
                        0,
                        pad_right,
                        cv2.BORDER_CONSTANT,
                        value=(0, 0, 0)
                    )

                filename = f"tile_{y:04d}_{x:04d}.jpg"

                cv2.imwrite(
                    os.path.join(folder_A, filename),
                    before_tile
                )

                cv2.imwrite(
                    os.path.join(folder_B, filename),
                    after_tile
                )

                f.write(filename + "\n")

                tile_count += 1

    print("\nTile Generation Complete")
    print("-" * 40)
    print(f"Image Width      : {width}")
    print(f"Image Height     : {height}")
    print(f"Tile Size        : {tile_size}")
    print(f"Stride           : {stride}")
    print(f"Tiles Generated  : {tile_count}")
    print(f"Dataset Location : {output_dataset_dir}")
    print("=" * 60)

    return {
        "width": width,
        "height": height,
        "tile_size": tile_size,
        "stride": stride,
        "tiles": tile_count
    }


if __name__ == "__main__":

    generate_tiles(
        before_image_path="datasets/change_detection/before_geotiff.png",
        after_image_path="datasets/change_detection/after_geotiff.png",
        output_dataset_dir="../../../ChangeFormer/temp_dataset",
        tile_size=256,
        stride=256
    )