from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.database.dashboard_queries import (
    get_latest_analysis,
    get_analysis_history,
    get_analysis_timeline,
    get_analysis_by_id,
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
# Serve Any Analysis File
#
# Used by the frontend to display images stored in SQLite.
#
# Example:
# /dashboard/file?path=backend/outputs/AOI001/20260719_183500/changestar_prediction.png
# ==========================================================

@router.get("/file")
def get_analysis_file(path: str):

    file_path = Path(path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}"
        )

    return FileResponse(file_path)