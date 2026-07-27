import json
import os
import shutil
from pathlib import Path

import cv2
import numpy as np
import rasterio
from skimage.exposure import match_histograms

from backend.services.sentinel_ingestion import SentinelIngestionService


SENTINEL_RGB_STATS = {
    "min": np.array([200.0, 200.0, 200.0], dtype=np.float32),
    "max": np.array([3500.0, 3500.0, 3500.0], dtype=np.float32),
    "mean": np.array([1100.0, 1250.0, 1400.0], dtype=np.float32),
    "std": np.array([650.0, 620.0, 610.0], dtype=np.float32),
}


def _write_json(path: str | Path, payload: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=4)


def _load_image_with_metadata(input_path: str):
    ext = Path(input_path).suffix.lower()

    if ext in [".tif", ".tiff"]:
        with rasterio.open(input_path) as src:
            image = src.read().astype(np.float32)
            metadata = {
                "path": str(input_path),
                "driver": src.driver,
                "crs": str(src.crs) if src.crs else None,
                "transform": list(src.transform),
                "width": src.width,
                "height": src.height,
                "count": src.count,
                "dtype": str(src.dtypes[0]),
            }

        image = np.moveaxis(image, 0, -1)
        return image, metadata

    image = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(input_path)

    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    elif image.shape[2] == 4:
        image = image[:, :, :3]

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
    metadata = {
        "path": str(input_path),
        "driver": "raster",
        "crs": None,
        "transform": None,
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "count": int(image.shape[2]),
        "dtype": str(image.dtype),
    }
    return image, metadata


def _ensure_rgb(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    if image.shape[2] > 3:
        image = image[:, :, :3]
    return image.astype(np.float32)


def _align_pair(before: np.ndarray, after: np.ndarray):
    height = min(before.shape[0], after.shape[0])
    width = min(before.shape[1], after.shape[1])

    before = cv2.resize(
        before,
        (width, height),
        interpolation=cv2.INTER_LINEAR,
    )
    after = cv2.resize(
        after,
        (width, height),
        interpolation=cv2.INTER_LINEAR,
    )
    return before, after


def _valid_mask(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3:
        return np.any(image > 1, axis=2)
    return image > 1


def _crop_black_borders(before: np.ndarray, after: np.ndarray):
    joint_valid = _valid_mask(before) & _valid_mask(after)

    if not np.any(joint_valid):
        return before, after, {
            "trimmed": False,
            "row_range": [0, int(before.shape[0])],
            "col_range": [0, int(before.shape[1])],
        }

    rows = np.where(np.any(joint_valid, axis=1))[0]
    cols = np.where(np.any(joint_valid, axis=0))[0]

    row_start, row_end = rows[0], rows[-1] + 1
    col_start, col_end = cols[0], cols[-1] + 1

    crop_meta = {
        "trimmed": True,
        "row_range": [int(row_start), int(row_end)],
        "col_range": [int(col_start), int(col_end)],
    }

    return (
        before[row_start:row_end, col_start:col_end],
        after[row_start:row_end, col_start:col_end],
        crop_meta,
    )


def _normalize_with_sentinel_stats(image: np.ndarray) -> np.ndarray:
    rgb = _ensure_rgb(image)
    result = np.zeros_like(rgb, dtype=np.float32)

    for channel in range(3):
        band = rgb[:, :, channel]

        if band.max() <= 255.0:
            lower = np.percentile(band, 2)
            upper = np.percentile(band, 98)
        else:
            lower = SENTINEL_RGB_STATS["min"][channel]
            upper = SENTINEL_RGB_STATS["max"][channel]

        if upper <= lower:
            lower = float(band.min())
            upper = float(band.max()) + 1.0

        band = np.clip(band, lower, upper)
        band = (band - lower) / (upper - lower + 1e-6)
        result[:, :, channel] = band

    return np.clip(result * 255.0, 0, 255).astype(np.uint8)


def _illumination_normalize(image: np.ndarray) -> np.ndarray:
    image = image.astype(np.float32)
    channel_means = image.reshape(-1, 3).mean(axis=0)
    global_mean = float(channel_means.mean())
    scale = global_mean / np.maximum(channel_means, 1.0)
    normalized = image * scale.reshape(1, 1, 3)
    return np.clip(normalized, 0, 255).astype(np.uint8)


def _apply_clahe(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    merged = cv2.merge([l_channel, a_channel, b_channel])
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)


def _histogram_match_pair(before: np.ndarray, after: np.ndarray):
    matched_after = match_histograms(
        after,
        before,
        channel_axis=-1,
    )
    return before, np.clip(matched_after, 0, 255).astype(np.uint8)


def _compute_cloud_mask(image: np.ndarray) -> np.ndarray:
    rgb = image.astype(np.uint8)
    brightness = rgb.mean(axis=2)
    channel_std = rgb.std(axis=2)
    blue = rgb[:, :, 2].astype(np.float32)
    green = rgb[:, :, 1].astype(np.float32)
    red = rgb[:, :, 0].astype(np.float32)

    bright_cloud = brightness > 215
    white_cloud = (brightness > 185) & (channel_std < 20)
    cold_cloud = (blue > 185) & (green > 170) & (red > 160) & (brightness > 170)
    probable_cloud = bright_cloud | white_cloud | cold_cloud

    mask = probable_cloud.astype(np.uint8) * 255
    kernel_small = np.ones((5, 5), np.uint8)
    kernel_large = np.ones((11, 11), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large)
    mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=1)
    return mask


def _compute_water_mask(image: np.ndarray) -> np.ndarray:
    rgb = image.astype(np.uint8)
    blue = rgb[:, :, 2].astype(np.float32)
    green = rgb[:, :, 1].astype(np.float32)
    red = rgb[:, :, 0].astype(np.float32)
    brightness = rgb.mean(axis=2)

    blue_dominant = (blue > green + 5) & (green > red)
    dark_water = brightness < 140
    coastal_water = (blue > red + 12) & (green > red + 5) & (brightness < 175)
    mask = (blue_dominant & dark_water) | coastal_water

    mask = mask.astype(np.uint8) * 255
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def _apply_cloud_mask_for_models(image: np.ndarray, cloud_mask: np.ndarray) -> np.ndarray:
    if not np.any(cloud_mask):
        return image

    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    repaired = cv2.inpaint(
        bgr,
        cloud_mask.astype(np.uint8),
        5,
        cv2.INPAINT_TELEA,
    )
    return cv2.cvtColor(repaired, cv2.COLOR_BGR2RGB)


def _save_rgb(path: str | Path, image: np.ndarray):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))


def _save_mask(path: str | Path, mask: np.ndarray):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), mask.astype(np.uint8))


def _resolve_output_paths(output_paths: dict | None):
    if output_paths is None:
        before_png = "datasets/change_detection/before_geotiff.png"
        after_png = "datasets/change_detection/after_geotiff.png"
        before_model = "datasets/change_detection/before_model_input.png"
        after_model = "datasets/change_detection/after_model_input.png"
        before_cloud = "datasets/change_detection/before_cloud_mask.png"
        after_cloud = "datasets/change_detection/after_cloud_mask.png"
        before_water = "datasets/change_detection/before_water_mask.png"
        after_water = "datasets/change_detection/after_water_mask.png"
        preprocessing_json = "datasets/change_detection/preprocessing_metadata.json"
    else:
        before_png = str(Path(output_paths["before_image"]).with_suffix(".png"))
        after_png = str(Path(output_paths["after_image"]).with_suffix(".png"))
        before_model = str(output_paths["before_model_input"])
        after_model = str(output_paths["after_model_input"])
        before_cloud = str(output_paths["before_cloud_mask"])
        after_cloud = str(output_paths["after_cloud_mask"])
        before_water = str(output_paths["before_water_mask"])
        after_water = str(output_paths["after_water_mask"])
        preprocessing_json = str(output_paths["preprocessing_metadata"])

    return {
        "before_png": before_png,
        "after_png": after_png,
        "before_model": before_model,
        "after_model": after_model,
        "before_cloud": before_cloud,
        "after_cloud": after_cloud,
        "before_water": before_water,
        "after_water": after_water,
        "preprocessing_json": preprocessing_json,
    }


def resolve_input(input_source):
    if input_source is None:
        return None

    input_path = Path(str(input_source))
    if input_path.exists():
        return str(input_path)

    if str(input_source).startswith("S2"):
        print(f"\nDetected Sentinel PRODUCT_ID: {input_source}")
        ingestion = SentinelIngestionService()
        return ingestion.ingest(str(input_source))

    raise FileNotFoundError(f"Unsupported input source: {input_source}")


def prepare_geotiff_inputs(
    before_input=None,
    after_input=None,
    output_paths=None,
    return_context: bool = False,
):
    if before_input is None or after_input is None:
        raise ValueError("before_input and after_input must be provided.")

    resolved = _resolve_output_paths(output_paths)

    before_input = resolve_input(before_input)
    after_input = resolve_input(after_input)

    before_raw, before_meta = _load_image_with_metadata(before_input)
    after_raw, after_meta = _load_image_with_metadata(after_input)

    before_rgb = _ensure_rgb(before_raw)
    after_rgb = _ensure_rgb(after_raw)
    before_rgb, after_rgb = _align_pair(before_rgb, after_rgb)
    before_rgb, after_rgb, crop_meta = _crop_black_borders(before_rgb, after_rgb)

    before_norm = _normalize_with_sentinel_stats(before_rgb)
    after_norm = _normalize_with_sentinel_stats(after_rgb)

    before_norm = _illumination_normalize(before_norm)
    after_norm = _illumination_normalize(after_norm)

    before_matched, after_matched = _histogram_match_pair(before_norm, after_norm)

    before_final = _apply_clahe(before_matched)
    after_final = _apply_clahe(after_matched)

    before_cloud_mask = _compute_cloud_mask(before_final)
    after_cloud_mask = _compute_cloud_mask(after_final)
    before_water_mask = _compute_water_mask(before_final)
    after_water_mask = _compute_water_mask(after_final)

    before_model_input = _apply_cloud_mask_for_models(before_final, before_cloud_mask)
    after_model_input = _apply_cloud_mask_for_models(after_final, after_cloud_mask)

    _save_rgb(resolved["before_png"], before_final)
    _save_rgb(resolved["after_png"], after_final)
    _save_rgb(resolved["before_model"], before_model_input)
    _save_rgb(resolved["after_model"], after_model_input)
    _save_mask(resolved["before_cloud"], before_cloud_mask)
    _save_mask(resolved["after_cloud"], after_cloud_mask)
    _save_mask(resolved["before_water"], before_water_mask)
    _save_mask(resolved["after_water"], after_water_mask)

    cloud_before_fraction = round(float(np.mean(before_cloud_mask > 0) * 100), 2)
    cloud_after_fraction = round(float(np.mean(after_cloud_mask > 0) * 100), 2)
    water_before_fraction = round(float(np.mean(before_water_mask > 0) * 100), 2)
    water_after_fraction = round(float(np.mean(after_water_mask > 0) * 100), 2)
    valid_fraction = round(float(np.mean(_valid_mask(before_rgb) & _valid_mask(after_rgb)) * 100), 2)

    preprocessing_context = {
        "before_source_path": before_input,
        "after_source_path": after_input,
        "before_display_path": resolved["before_png"],
        "after_display_path": resolved["after_png"],
        "before_model_input_path": resolved["before_model"],
        "after_model_input_path": resolved["after_model"],
        "before_cloud_mask_path": resolved["before_cloud"],
        "after_cloud_mask_path": resolved["after_cloud"],
        "before_water_mask_path": resolved["before_water"],
        "after_water_mask_path": resolved["after_water"],
        "cloud_fraction": {
            "before": cloud_before_fraction,
            "after": cloud_after_fraction,
            "average": round((cloud_before_fraction + cloud_after_fraction) / 2, 2),
        },
        "water_fraction": {
            "before": water_before_fraction,
            "after": water_after_fraction,
            "average": round((water_before_fraction + water_after_fraction) / 2, 2),
        },
        "image_quality": {
            "valid_fraction": valid_fraction,
            "trimmed_black_borders": crop_meta["trimmed"],
            "before_mean_brightness": round(float(before_final.mean()), 2),
            "after_mean_brightness": round(float(after_final.mean()), 2),
            "mean_brightness_delta": round(float(abs(before_final.mean() - after_final.mean())), 2),
        },
        "crop": crop_meta,
        "before_metadata": before_meta,
        "after_metadata": after_meta,
    }

    _write_json(
        resolved["preprocessing_json"],
        preprocessing_context,
    )
    preprocessing_context["metadata_path"] = resolved["preprocessing_json"]

    if return_context:
        return resolved["before_png"], resolved["after_png"], preprocessing_context

    return resolved["before_png"], resolved["after_png"]
