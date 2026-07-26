from fastapi import APIRouter

router = APIRouter(
    prefix="/change-detection",
    tags=["Change Detection"]
)

@router.get("/analyze")
def analyze_change():
    return {
        "status": "Analysis Complete",
        "detected_changes": 12,
        "confidence": 0.94
    }