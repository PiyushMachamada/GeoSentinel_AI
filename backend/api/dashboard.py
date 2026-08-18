from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from backend.config import OUTPUT_DIR
from backend.database.dashboard_queries import (
    get_latest_analysis,
    get_analysis_history,
    get_analysis_timeline,
    get_analysis_by_id,
)
from backend.database.trend_queries import (
    get_aoi_trend,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ==========================================================
# Dashboard Status
# ==========================================================

@router.get("/")
def dashboard_status():
    return {
        "status": "Dashboard API Ready"
    }


# ==========================================================
# Latest Analysis
# ==========================================================

@router.get("/latest/{aoi_id}")
def latest_analysis(aoi_id: str):

    result = get_latest_analysis(aoi_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this AOI."
        )

    return result


# ==========================================================
# Analysis By ID
# ==========================================================

@router.get("/analysis/{analysis_id}")
def analysis_by_id(analysis_id: int):

    result = get_analysis_by_id(analysis_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found."
        )

    return result


# ==========================================================
# Analysis History
# ==========================================================

@router.get("/history/{aoi_id}")
def analysis_history(aoi_id: str):

    results = get_analysis_history(aoi_id)

    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail="No analysis history found for this AOI."
        )

    return results


# ==========================================================
# Timeline
# ==========================================================

@router.get("/timeline/{aoi_id}")
def analysis_timeline(aoi_id: str):

    results = get_analysis_timeline(aoi_id)

    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail="No timeline available for this AOI."
        )

    return results


# ==========================================================
# Historical Trend
# ==========================================================

@router.get("/trend/{aoi_id}")
def aoi_trend(aoi_id: str):
    """
    Returns aggregated historical trend metrics for an AOI:
    change trend, confidence trend, timestamps, and growth rates.
    """
    trend = get_aoi_trend(aoi_id)
    return JSONResponse(content=trend)


# ==========================================================
# Output Health
# Returns a lightweight health summary for the latest run.
# ==========================================================

@router.get("/health/{aoi_id}")
def analysis_health(aoi_id: str):
    """
    Returns a health summary for the latest analysis.
    Reads the output_validation.json if present.
    """
    result = get_latest_analysis(aoi_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this AOI."
        )

    analysis_dir = result.get("analysis_directory")
    if not analysis_dir:
        return {"aoi_id": aoi_id, "health": "unknown", "detail": "No analysis directory"}

    validation_path = Path(analysis_dir) / "reports" / "output_validation.json"
    if validation_path.exists():
        import json
        try:
            with open(validation_path, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass

    return {
        "aoi_id": aoi_id,
        "health": "unknown",
        "detail": "Validation report not yet generated",
    }


# ==========================================================
# Serve Any Analysis File
#
# Used by the frontend to display images stored in SQLite.
#
# Example:
# /dashboard/file?path=backend/outputs/AOI001/20260719_183500/changestar_prediction.png
# ==========================================================

@router.get("/file")
def get_analysis_file(path: str):

    if not path or not path.strip():
        raise HTTPException(
            status_code=400,
            detail="Path query parameter is required.",
        )

    repo_root = Path(__file__).resolve().parents[2]
    configured_output = Path(OUTPUT_DIR)
    outputs_root = (
        configured_output.resolve()
        if configured_output.is_absolute()
        else (repo_root / configured_output).resolve()
    )

    normalized_input = path.replace("\\", "/").strip()
    requested_path = Path(normalized_input)

    # ------------------------------------------------------------------
    # Determine relative_parts (path segments under outputs_root).
    # Absolute paths are stored in the database by the pipeline; relative
    # paths may be supplied by the frontend.  Both must resolve under
    # outputs_root after normalization.
    # ------------------------------------------------------------------

    if requested_path.is_absolute():
        # Strip any ".." from the supplied parts before comparing prefixes.
        abs_parts = tuple(
            p for p in requested_path.parts if p not in (".", "")
        )
        if any(p == ".." for p in abs_parts):
            raise HTTPException(
                status_code=400,
                detail="Parent-directory references are not allowed.",
            )
        outputs_parts = outputs_root.parts
        n = len(outputs_parts)
        if abs_parts[:n] != outputs_parts:
            raise HTTPException(
                status_code=403,
                detail="Access to requested file path is not allowed.",
            )
        relative_parts = list(abs_parts[n:])
    else:
        normalized_parts = [part for part in requested_path.parts if part not in (".", "")]
        if any(part == ".." for part in normalized_parts):
            raise HTTPException(
                status_code=400,
                detail="Parent-directory references are not allowed.",
            )

        if normalized_parts[:2] == ["backend", "outputs"]:
            relative_parts = normalized_parts[2:]
        elif normalized_parts[:1] == ["outputs"]:
            relative_parts = normalized_parts[1:]
        else:
            raise HTTPException(
                status_code=403,
                detail="Requested file must be inside the configured outputs directory.",
            )

    file_path = (outputs_root / Path(*relative_parts)).resolve()

    try:
        file_path.relative_to(outputs_root)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access to requested file path is not allowed.",
        )

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Requested file was not found."
        )

    return FileResponse(file_path)
