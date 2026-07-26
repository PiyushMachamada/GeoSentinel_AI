import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import rasterio

from backend.services.sentinel_ingestion import SentinelIngestionService


def normalize_band(band: np.ndarray) -> np.ndarray:
    """
    Adaptive percentile stretch for Sentinel imagery.

    Uses the 2nd and 98th percentiles instead of assuming
    all scenes occupy the full 0–10000 reflectance range.
    """

    band = band.astype(np.float32)

    p2 = np.percentile(band, 2)
    p98 = np.percentile(band, 98)

    if p98 <= p2:
        p2 = band.min()
        p98 = band.max()

    band = np.clip(band, p2, p98)

    band = (band - p2) / (p98 - p2 + 1e-6)

    band = band * 255.0

    return band.astype(np.uint8)

def geotiff_to_png(
    input_path: str,
    output_png: str,
    debug_dir: str | None = None,
):
    """
    Convert GeoTIFF or RGB image into a PNG suitable for
    downstream computer vision models.
    """

    ext = Path(input_path).suffix.lower()

    # -------------------------------------------------
    # Read GeoTIFF
    # -------------------------------------------------

    if ext in [".tif", ".tiff"]:

        with rasterio.open(input_path) as src:

            image = src.read()

            print("\n===================================")
            print("RAW GEOTIFF STATISTICS")
            print("===================================")

            print("Image dtype :", image.dtype)
            print("Global Min  :", image.min())
            print("Global Max  :", image.max())
            print("Global Mean :", image.mean())

            for i in range(src.count):
                band = image[i]

                print(f"\nBand {i+1}")
                print("Min :", band.min())
                print("Max :", band.max())
                print("Mean:", band.mean())

                print(
                    "Percentiles:",
                    np.percentile(
                        band,
                        [0, 1, 2, 5, 25, 50, 75, 95, 98, 99, 100]
                    )
                )

            print("\nGLOBAL IMAGE")
            print("dtype :", image.dtype)
            print("Min   :", image.min())
            print("Max   :", image.max())
            print("Mean  :", image.mean())

            for i in range(src.count):
                print(
                    f"Band {i+1}:",
                    image[i].min(),
                    image[i].max(),
                    image[i].mean(),
                )

            print("\n==============================")
            print("GeoTIFF Debug")
            print("==============================")
            print("Input :", input_path)
            print("Shape :", image.shape)
            print("Bands :", src.count)
            print("CRS   :", src.crs)
            print("dtype :", image.dtype)

            print("\n===== Raster Statistics =====")

            for i in range(src.count):

                print(
                    f"Band {i+1}: "
                    f"Min={image[i].min()} "
                    f"Max={image[i].max()} "
                    f"Mean={image[i].mean():.2f}"
                )

        image = np.moveaxis(image, 0, -1)

    # -------------------------------------------------
    # Read JPG / PNG
    # -------------------------------------------------

    else:

        image = cv2.imread(
            input_path,
            cv2.IMREAD_UNCHANGED,
        )

        if image is None:
            raise FileNotFoundError(input_path)

        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

    # -------------------------------------------------
    # Ensure RGB
    # -------------------------------------------------

    if image.ndim == 2:

        image = np.stack(
            [image] * 3,
            axis=-1,
        )

    elif image.shape[2] == 1:

        image = np.repeat(
            image,
            3,
            axis=2,
        )

    elif image.shape[2] > 3:

        image = image[:, :, :3]

    # -------------------------------------------------
    # Normalize channels
    # -------------------------------------------------

    rgb = np.zeros(
        image.shape,
        dtype=np.uint8,
    )

    for c in range(3):

        rgb[:, :, c] = normalize_band(
            image[:, :, c]
        )

    # -------------------------------------------------
    # PNG Statistics
    # -------------------------------------------------

    print("\nPNG DEBUG")
    print("-------------------------")
    print("Shape :", rgb.shape)
    print("dtype :", rgb.dtype)
    print("Min   :", rgb.min())
    print("Max   :", rgb.max())
    print("Mean  :", rgb.mean())

    for c, name in enumerate(["Red", "Green", "Blue"]):
        print(
            f"{name}: "
            f"min={rgb[:,:,c].min()} "
            f"max={rgb[:,:,c].max()} "
            f"mean={rgb[:,:,c].mean():.2f}"
        )
    bgr = cv2.cvtColor(
        rgb,
        cv2.COLOR_RGB2BGR,
    )

    os.makedirs(
        os.path.dirname(output_png),
        exist_ok=True,
    )

    cv2.imwrite(
        output_png,
        bgr,
    )

    if debug_dir is not None:

        os.makedirs(
            debug_dir,
            exist_ok=True,
        )

        shutil.copy(
            output_png,
            os.path.join(
                debug_dir,
                os.path.basename(output_png),
            ),
        )

    print(f"\nSaved: {output_png}")


def resolve_input(input_source):
    """
    Resolve supported inputs into a local image path.

    Supported:
        - JPG
        - PNG
        - TIFF
        - Sentinel PRODUCT_ID
    """

    if input_source is None:
        return None

    input_path = Path(str(input_source))

    if input_path.exists():
        return str(input_path)

    if str(input_source).startswith("S2"):

        print(
            f"\nDetected Sentinel PRODUCT_ID: {input_source}"
        )

        ingestion = SentinelIngestionService()

        return ingestion.ingest(
            str(input_source)
        )

    raise FileNotFoundError(
        f"Unsupported input source: {input_source}"
    )


def prepare_geotiff_inputs(
    before_input=None,
    after_input=None,
    output_paths=None,
):
    """
    Prepare two images for the GeoSentinel pipeline.

    Returns:
        before_png,
        after_png
    """

    if before_input is None or after_input is None:

        raise ValueError(
            "before_input and after_input must be provided."
        )

    # -------------------------------------------------
    # Output paths
    # -------------------------------------------------

    if output_paths is None:

        before_png = "datasets/change_detection/before_geotiff.png"
        after_png = "datasets/change_detection/after_geotiff.png"

        debug_dir = None

    else:

        before_png = str(
            Path(
                output_paths["before_image"]
            ).with_suffix(".png")
        )

        after_png = str(
            Path(
                output_paths["after_image"]
            ).with_suffix(".png")
        )

        debug_dir = (
            Path(before_png).parent
            / "debug"
        )

    # -------------------------------------------------
    # Resolve inputs
    # -------------------------------------------------

    before_input = resolve_input(before_input)
    after_input = resolve_input(after_input)

    # -------------------------------------------------
    # BEFORE image
    # -------------------------------------------------

    before_ext = Path(before_input).suffix.lower()

    if before_ext in [".tif", ".tiff"]:

        geotiff_to_png(
            before_input,
            before_png,
            debug_dir,
        )

    elif before_ext in [
        ".jpg",
        ".jpeg",
        ".png",
    ]:

        shutil.copy(
            before_input,
            before_png,
        )

    else:

        raise ValueError(
            f"Unsupported file type: {before_ext}"
        )

    # -------------------------------------------------
    # AFTER image
    # -------------------------------------------------

    after_ext = Path(after_input).suffix.lower()

    if after_ext in [".tif", ".tiff"]:

        geotiff_to_png(
            after_input,
            after_png,
            debug_dir,
        )

    elif after_ext in [
        ".jpg",
        ".jpeg",
        ".png",
    ]:

        shutil.copy(
            after_input,
            after_png,
        )

    else:

        raise ValueError(
            f"Unsupported file type: {after_ext}"
        )

    return before_png, after_png