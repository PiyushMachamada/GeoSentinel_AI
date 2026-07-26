from backend.services.sentinel import SentinelService


class GeoSentinelDataProvider:
    """
    Provides AI-ready imagery for the GeoSentinel pipeline.
    """

    def __init__(self):
        self.sentinel = SentinelService()

    def get_latest_rgb(
        self,
        latitude,
        longitude,
        radius_km=5,
    ):
        """
        Returns the latest RGB GeoTIFF.

        Returns
        -------
        dict
        {
            "image_path": "...",
            "date": "...",
            "product_id": "...",
            "metadata": {...}
        }
        """

        result = self.sentinel.get_latest_geotiff(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        if result is None:
            return None

        return {
            "image_path": result["geotiff"],
            "date": result["date"],
            "product_id": result["product_id"],
            "metadata": result["metadata"],
        }