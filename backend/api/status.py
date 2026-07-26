from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def get_status():
    return {
        "platform": "GeoSentinel AI",
        "status": "Running",
        "version": "1.0.0"
    }