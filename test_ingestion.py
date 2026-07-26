from backend.services.sentinel import SentinelService

service = SentinelService()

pair = service.get_image_pair(
    latitude=18.943,
    longitude=72.949,
    radius_km=8,
)

downloads = service.download_pair(pair)

print(downloads)