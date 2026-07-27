"""
output_validation.py

GeoSentinel AI — Post-pipeline output health check.

After every pipeline run, call validate_outputs() to:
  1. Verify every expected image/JSON exists on disk.
  2. Log missing artifacts.
  3. Attempt to regenerate only the missing ones.
  4. Return a structured validation report.

Never reruns the full pipeline — only fixes missing artifacts.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ================================================================
# Expected artifacts per category
# (key in output_paths → human label)
# ================================================================

REQUIRED_IMAGES = {
    "before_model_input":   "Before model input PNG",
    "after_model_input":    "After model input PNG",
    "prithvi_before":       "Prithvi segmentation (before)",
    "prithvi_after":        "Prithvi segmentation (after)",
    "grounding_dino_before": "Grounding DINO (before)",
    "grounding_dino_after":  "Grounding DINO (after)",
    "changestar_prediction": "ChangeStar prediction",
    "change_binary":         "Binary change map",
    "change_map":            "Change map",
}

OPTIONAL_IMAGES = {
    "dynamic_world_before_png": "Dynamic World colorized (before)",
    "dynamic_world_after_png":  "Dynamic World colorized (after)",
    "dynamic_world_transition": "Dynamic World transition map",
    "before_cloud_mask":        "Cloud mask (before)",
    "after_cloud_mask":         "Cloud mask (after)",
    "agreement_map":            "Agreement map",
    "uncertainty_map":          "Uncertainty map",
    "evidence_map":             "Evidence map",
    "prithvi_before_confidence": "Segmentation confidence (before)",
    "prithvi_after_confidence":  "Segmentation confidence (after)",
}

REQUIRED_REPORTS = {
    "intelligence_report": "Intelligence report",
    "semantic_change_results": "Semantic change results JSON",
}

OPTIONAL_REPORTS = {
    "preprocessing_metadata": "Preprocessing metadata JSON",
    "model_agreement_json":   "Model agreement JSON",
    "fusion_json":            "Fusion results JSON",
    "analysis_json":          "Analysis JSON",
    "mission_summary_json":   "Mission summary JSON",
    "evidence_json":          "Evidence JSON",
    "trend_json":             "Trend JSON",
    "confidence_json":        "Confidence JSON",
    "report_md":              "Markdown report",
    "report_html":            "HTML report",
}


def _check_paths(
    output_paths: dict,
    keys: dict,
    required: bool,
) -> dict:
    """
    Check whether artifact files exist on disk.

    Returns
    -------
    dict
        {key: {"label": str, "path": str, "exists": bool, "required": bool}}
    """
    results = {}
    for key, label in keys.items():
        path = output_paths.get(key)
        if path is None:
            results[key] = {
                "label": label,
                "path": None,
                "exists": False,
                "required": required,
            }
            continue

        path = Path(path)
        results[key] = {
            "label": label,
            "path": str(path),
            "exists": path.exists() and path.stat().st_size > 0,
            "required": required,
        }
    return results


def validate_outputs(
    output_paths: dict,
    aoi_id: str = "",
    attempt_regeneration: bool = True,
) -> dict:
    """
    Validate that all expected artifacts exist.

    Parameters
    ----------
    output_paths : dict
        The dictionary returned by OutputManager.default_files().
    aoi_id : str
        For logging.
    attempt_regeneration : bool
        If True, try to regenerate missing optional artifacts.

    Returns
    -------
    dict
        Validation report with per-artifact status and overall health.
    """
    tag = f"[{aoi_id}]" if aoi_id else ""

    checks = {}
    checks.update(_check_paths(output_paths, REQUIRED_IMAGES, required=True))
    checks.update(_check_paths(output_paths, OPTIONAL_IMAGES, required=False))
    checks.update(_check_paths(output_paths, REQUIRED_REPORTS, required=True))
    checks.update(_check_paths(output_paths, OPTIONAL_REPORTS, required=False))

    missing_required = [
        k for k, v in checks.items()
        if v["required"] and not v["exists"]
    ]
    missing_optional = [
        k for k, v in checks.items()
        if not v["required"] and not v["exists"]
    ]
    regenerated = []

    if attempt_regeneration:
        regenerated = _regenerate_missing(
            output_paths,
            missing_optional,
            tag,
        )
        # Re-check after regeneration
        for key in regenerated:
            path = output_paths.get(key)
            if path and Path(path).exists():
                checks[key]["exists"] = True

    total = len(checks)
    existing = sum(1 for v in checks.values() if v["exists"])
    health = round(existing / total * 100, 1) if total else 0.0

    overall_ok = len(missing_required) == 0

    report = {
        "aoi_id": aoi_id,
        "overall_ok": overall_ok,
        "health_percentage": health,
        "total_artifacts": total,
        "existing_artifacts": existing,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "regenerated": regenerated,
        "artifacts": checks,
    }

    if overall_ok:
        logger.info("%s Output validation passed (%.1f%% health)", tag, health)
    else:
        logger.warning(
            "%s Output validation: MISSING required artifacts: %s",
            tag,
            missing_required,
        )

    # Save validation report
    validation_path = output_paths.get("validation_json")
    if validation_path:
        try:
            Path(validation_path).parent.mkdir(parents=True, exist_ok=True)
            with open(validation_path, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=4, default=str)
        except Exception as exc:
            logger.warning("%s Could not save validation report: %s", tag, exc)

    return report


def _regenerate_missing(
    output_paths: dict,
    missing_keys: list,
    tag: str,
) -> list:
    """
    Attempt to regenerate specific missing artifacts.
    Only regenerates things that can be derived from already-existing files.

    Returns list of keys that were successfully regenerated.
    """
    regenerated = []

    for key in missing_keys:
        try:
            if key in ("dynamic_world_before_png", "dynamic_world_after_png"):
                regenerated += _regen_dw_pngs(output_paths, tag)
                break  # Both handled at once

        except Exception as exc:
            logger.warning("%s Could not regenerate %s: %s", tag, key, exc)

    # Regenerate quality maps from preprocessing/fusion artifacts if possible
    for key in missing_keys:
        try:
            if key == "after_cloud_mask" or key == "before_cloud_mask":
                # Fallback: create a minimal placeholder to avoid broken UI
                _create_placeholder_image(
                    output_paths.get(key),
                    label="Cloud data unavailable",
                )
                regenerated.append(key)

            elif key in ("agreement_map", "uncertainty_map", "evidence_map"):
                # Fallback: create informative placeholder
                label_map = {
                    "agreement_map": "Agreement map not generated",
                    "uncertainty_map": "Uncertainty map not generated",
                    "evidence_map": "Evidence map not generated",
                }
                _create_placeholder_image(
                    output_paths.get(key),
                    label=label_map.get(key, "Unavailable"),
                )
                regenerated.append(key)

        except Exception as exc:
            logger.warning(
                "%s Placeholder generation failed for %s: %s",
                tag,
                key,
                exc,
            )

    return regenerated


def _regen_dw_pngs(output_paths: dict, tag: str) -> list:
    """Regenerate DW colored PNGs from existing TIF files."""
    from backend.models.dynamic_world_colorizer import colorize_dynamic_world

    regenerated = []

    before_tif = output_paths.get("dynamic_world_before")
    after_tif = output_paths.get("dynamic_world_after")
    before_png = output_paths.get("dynamic_world_before_png")
    after_png = output_paths.get("dynamic_world_after_png")

    if before_tif and before_png and Path(before_tif).exists():
        result = colorize_dynamic_world(str(before_tif), str(before_png))
        if result:
            regenerated.append("dynamic_world_before_png")
            logger.info("%s Regenerated DW PNG (before)", tag)

    if after_tif and after_png and Path(after_tif).exists():
        result = colorize_dynamic_world(str(after_tif), str(after_png))
        if result:
            regenerated.append("dynamic_world_after_png")
            logger.info("%s Regenerated DW PNG (after)", tag)

    return regenerated


def _create_placeholder_image(
    path: Optional[str],
    label: str = "Unavailable",
    size: tuple = (400, 300),
) -> None:
    """Create a grey placeholder PNG with a centered status label."""
    import cv2
    import numpy as np

    if path is None:
        return

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    h, w = size[1], size[0]
    img = np.full((h, w, 3), 50, dtype=np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.55
    thickness = 1
    (text_w, text_h), _ = cv2.getTextSize(
        label, font, font_scale, thickness
    )
    x = max(0, (w - text_w) // 2)
    y = max(text_h, (h + text_h) // 2)

    cv2.putText(
        img,
        label,
        (x, y),
        font,
        font_scale,
        (160, 160, 160),
        thickness,
        cv2.LINE_AA,
    )

    cv2.imwrite(str(path), img)
