from fastapi import APIRouter

from backend.services.sentinel import get_sentinel_images
from backend.services.web_scraper import collect_reports
from backend.services.twitter import get_social_data

from backend.database.storage import save_satellite_data
from backend.database.storage import save_text_report
from backend.database.storage import save_social_post


router = APIRouter()


@router.get("/data/collect")
def collect_data(region: str):

    satellite_data = get_sentinel_images(
        region,
        "2026-06-15"
    )

    text_data = collect_reports(
        region
    )

    social_data = get_social_data(
        region
    )

    save_satellite_data(satellite_data)
    save_text_report(text_data)
    save_social_post(social_data)

    return {
        "region": region,
        "satellite_data": satellite_data,
        "text_data": text_data,
        "social_data": social_data,
        "storage_status": "saved_to_database"
    }