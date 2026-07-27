"""
dynamic_world_colorizer.py

Converts a Dynamic World label raster (TIF, 0-8 class integers)
into a colorized PNG using the official Google Dynamic World palette.

This is called immediately after DW export so the dashboard can
render meaningful land-cover maps instead of showing grayscale
label values that browsers cannot meaningfully display.
"""

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import rasterio


# ================================================================
# Official Google Dynamic World color palette (RGB)
# ================================================================
# Class 0: water           → blue
# Class 1: trees           → dark green
# Class 2: grass           → light green
# Class 3: flooded_veg     → teal
# Class 4: crops           → yellow-green
# Class 5: shrub_and_scrub → khaki
# Class 6: built_area      → red / brick
# Class 7: bare_ground     → tan
# Class 8: snow_and_ice    → light cyan / white

DW_COLORS_RGB = {
    0: (65,  155, 223),   # water           – blue
    1: (57,  125,  73),   # trees           – dark green
    2: (136, 176,  83),   # grass           – lime green
    3: (122, 135,  49),   # flooded_veg     – olive
    4: (228, 150,  53),   # crops           – orange-yellow
    5: (223, 195, 90),    # shrub_and_scrub – yellow-tan
    6: (196,  40,  27),   # built_area      – red-brick
    7: (165, 155, 143),   # bare_ground     – grey-tan
    8: (179, 159, 225),   # snow_and_ice    – lavender-white
}

DW_CLASS_NAMES = {
    0: "Water",
    1: "Trees",
    2: "Grass",
    3: "Flooded Vegetation",
    4: "Crops",
    5: "Shrub & Scrub",
    6: "Built Area",
    7: "Bare Ground",
    8: "Snow & Ice",
}


def colorize_dynamic_world(
    tif_path: str,
    output_png_path: str,
    add_legend: bool = True,
) -> Optional[str]:
    """
    Read a DW label TIF and write a colorized PNG.

    Parameters
    ----------
    tif_path : str
        Path to the single-band label TIF (values 0-8).
    output_png_path : str
        Destination PNG path.
    add_legend : bool
        Whether to overlay a small class-color legend.

    Returns
    -------
    str | None
        Path to the saved PNG, or None on failure.
    """
    tif_path = Path(tif_path)
    output_png_path = Path(output_png_path)

    if not tif_path.exists():
        print(f"[DW Colorizer] TIF not found: {tif_path}")
        return None

    try:
        with rasterio.open(tif_path) as src:
            labels = src.read(1).astype(np.int16)

        h, w = labels.shape
        color_image = np.zeros((h, w, 3), dtype=np.uint8)

        for class_id, (r, g, b) in DW_COLORS_RGB.items():
            mask = labels == class_id
            color_image[mask] = (r, g, b)

        # Pixels outside 0-8 treated as no-data → grey
        no_data_mask = (labels < 0) | (labels > 8)
        color_image[no_data_mask] = (80, 80, 80)

        if add_legend:
            color_image = _add_legend(color_image)

        output_png_path.parent.mkdir(parents=True, exist_ok=True)

        # OpenCV expects BGR
        bgr = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(output_png_path), bgr)

        print(f"[DW Colorizer] Saved: {output_png_path}")
        return str(output_png_path)

    except Exception as exc:
        print(f"[DW Colorizer] Error colorizing {tif_path}: {exc}")
        return None


def _add_legend(image: np.ndarray) -> np.ndarray:
    """Overlay a compact class-color legend in the bottom-left corner."""
    h, w = image.shape[:2]

    legend_item_h = 20
    legend_margin = 6
    n_classes = len(DW_COLORS_RGB)
    legend_h = n_classes * legend_item_h + 2 * legend_margin
    legend_w = 175
    swatch_w = 16

    # Only draw legend if image is big enough
    if h < legend_h + 40 or w < legend_w + 40:
        return image

    result = image.copy()

    # Semi-transparent background
    overlay = result.copy()
    legend_x = legend_margin
    legend_y = h - legend_h - legend_margin
    cv2.rectangle(
        overlay,
        (legend_x, legend_y),
        (legend_x + legend_w, legend_y + legend_h),
        (20, 20, 20),
        -1,
    )
    result = cv2.addWeighted(result, 0.6, overlay, 0.4, 0)

    for i, (class_id, (r, g, b)) in enumerate(DW_COLORS_RGB.items()):
        item_y = legend_y + legend_margin + i * legend_item_h
        # Color swatch
        cv2.rectangle(
            result,
            (legend_x + 4, item_y + 3),
            (legend_x + 4 + swatch_w, item_y + legend_item_h - 4),
            (b, g, r),  # BGR for OpenCV
            -1,
        )
        # Class name (BGR text)
        cv2.putText(
            result,
            DW_CLASS_NAMES.get(class_id, str(class_id)),
            (legend_x + 4 + swatch_w + 5, item_y + legend_item_h - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (220, 220, 220),
            1,
            cv2.LINE_AA,
        )

    return result


def generate_dw_png_pair(output_paths: dict) -> dict:
    """
    Generate colored PNGs for both before and after DW TIF files.
    Uses the standard output_manager key names.

    Returns
    -------
    dict
        {"before_png": str|None, "after_png": str|None}
    """
    before_tif = output_paths.get("dynamic_world_before")
    after_tif = output_paths.get("dynamic_world_after")

    before_png_path = output_paths.get("dynamic_world_before_png")
    after_png_path = output_paths.get("dynamic_world_after_png")

    before_png = colorize_dynamic_world(
        str(before_tif),
        str(before_png_path),
    ) if before_tif and before_png_path else None

    after_png = colorize_dynamic_world(
        str(after_tif),
        str(after_png_path),
    ) if after_tif and after_png_path else None

    return {
        "before_png": before_png,
        "after_png": after_png,
    }
