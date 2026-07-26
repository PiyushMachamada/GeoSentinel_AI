from fastapi import APIRouter

router = APIRouter(prefix="/satellite", tags=["Satellite"])

@router.get("/info")
def satellite_info():
    return {
        "mission": "Sentinel-2",
        "provider": "Copernicus",
        "resolution": "10m",
        "status": "Available"
    }