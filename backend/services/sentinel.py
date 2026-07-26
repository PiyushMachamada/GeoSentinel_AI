import os
from datetime import datetime, timedelta

import ee
import requests
from google.oauth2 import service_account
from backend.services.sentinel_ingestion import SentinelIngestionService


class SentinelService:
    """
    Handles Sentinel-2 imagery retrieval from Google Earth Engine.
    """

    def __init__(self):
        self.project_id = "geosentinel-earthengine"

        service_account_file = (
            "credentials/earthengine-service-account.json"
        )

        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=[
                "https://www.googleapis.com/auth/earthengine",
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

        ee.Initialize(
            credentials=credentials,
            project=self.project_id,
        )

        print("✓ Earth Engine initialized with service account.")

        self.ingestion = SentinelIngestionService()

    def get_latest_image(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5,
        days: int = 365,
        max_cloud_cover: float = 100,
    ):
        """
        Returns metadata for the latest Sentinel-2 image covering the AOI.
        """

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        region = (
            ee.Geometry.Point([longitude, latitude])
            .buffer(radius_km * 1000)
        )

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(region)
            .filterDate(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    max_cloud_cover,
                )
            )
            .sort("system:time_start", False)
        )

        count = collection.size().getInfo()

        print(f"\nSentinel Images Found: {count}")

        if count == 0:
            return None

        image = collection.first()

        image_id = image.id().getInfo()

        properties = image.toDictionary().getInfo()

        timestamp = image.get("system:time_start").getInfo()

        acquisition_date = None

        if timestamp:
            acquisition_date = datetime.utcfromtimestamp(
                timestamp / 1000
            ).strftime("%Y-%m-%d")

        product_id = properties.get("PRODUCT_ID")

        return {
            "image": image,
            "image_id": image_id,
            "product_id": properties.get("PRODUCT_ID"),
            "date": acquisition_date,
            "cloud_cover": properties.get("CLOUDY_PIXEL_PERCENTAGE"),
            "properties": properties,
        }
    
    def get_previous_image(
        self,
        latitude: float,
        longitude: float,
        latest_date: str,
        radius_km: float = 5,
        lookback_days: int = 365,
        max_cloud_cover: float = 30,
    ):
        """
        Returns the newest Sentinel image BEFORE the supplied latest_date.
        """

        latest_dt = datetime.strptime(
            latest_date,    
            "%Y-%m-%d",
        )

        start_date = latest_dt - timedelta(days=lookback_days)

        region = (
            ee.Geometry.Point([longitude, latitude])
            .buffer(radius_km * 1000)
        )

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(region)
            .filterDate(
                start_date.strftime("%Y-%m-%d"),
                latest_dt.strftime("%Y-%m-%d"),
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    max_cloud_cover,
                )
            )
            .sort("system:time_start", False)
        )

        images = collection.toList(2)

        if collection.size().getInfo() < 2:
            return None

        image = ee.Image(images.get(1))

        properties = image.toDictionary().getInfo()

        timestamp = image.get("system:time_start").getInfo()

        acquisition_date = datetime.utcfromtimestamp(
            timestamp / 1000
        ).strftime("%Y-%m-%d")

        return {
            "image": image,
            "image_id": image.id().getInfo(),
            "product_id": properties.get("PRODUCT_ID"),
            "date": acquisition_date,
            "cloud_cover": properties.get("CLOUDY_PIXEL_PERCENTAGE"),
            "properties": properties,
        }
    
    def get_image_pair(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5,
        days: int = 365,
        max_cloud_cover: float = 30,
    ):
        """
        Returns the newest two Sentinel images.

        Returns
        -------
        {
            "before": {...},
            "after": {...}
        }
        """

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        region = (
            ee.Geometry.Point([longitude, latitude])
            .buffer(radius_km * 1000)
        )

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(region)
            .filterDate(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    max_cloud_cover,
                )
            )
            .sort("system:time_start", False)
        )

        if collection.size().getInfo() < 2:
            return None

        images = collection.toList(2)

        newest = ee.Image(images.get(0))
        previous = ee.Image(images.get(1))

        def metadata(image):

            props = image.toDictionary().getInfo()

            timestamp = image.get("system:time_start").getInfo()

            return {
                "image": image,
                "image_id": image.id().getInfo(),
                "product_id": props.get("PRODUCT_ID"),
                "date": datetime.utcfromtimestamp(
                    timestamp / 1000
                ).strftime("%Y-%m-%d"),
                "cloud_cover": props.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
                "properties": props,
            }

        return {
            "before": metadata(previous),
            "after": metadata(newest),
        }
    
    def download_pair(self, pair):
        """
        Downloads both images returned by get_image_pair().
        """

        return {
            "before": self.get_geotiff_from_metadata(
                pair["before"]
            ),
            "after": self.get_geotiff_from_metadata(
                pair["after"]
            ),
        }

    def download_pair_aoi(
        self,
        pair,
        latitude: float,
        longitude: float,
        radius_km: float,
        output_directory: str = "backend/outputs",
    ):
        """
        Downloads the before/after Sentinel images directly from
        Google Earth Engine clipped to the AOI.

        Returns
        -------
        {
            "before": {...},
            "after": {...}
        }
        """

        os.makedirs(output_directory, exist_ok=True)

        before_path = os.path.join(
            output_directory,
            "before_geotiff.tif",
        )

        after_path = os.path.join(
            output_directory,
            "after_geotiff.tif",
        )

        self.download_image(
            image=pair["before"]["image"],
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            output_path=before_path,
        )

        self.download_image(
            image=pair["after"]["image"],
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            output_path=after_path,
        )

        return {
            "before": {
                "geotiff": before_path,
                "image": pair["before"]["image"],
                "image_id": pair["before"]["image_id"],
                "product_id": pair["before"]["product_id"],
                "date": pair["before"]["date"],
                "cloud_cover": pair["before"]["cloud_cover"],
                "properties": pair["before"]["properties"],
            },
            "after": {
                "geotiff": after_path,
                "image": pair["after"]["image"],
                "image_id": pair["after"]["image_id"],
                "product_id": pair["after"]["product_id"],
                "date": pair["after"]["date"],
                "cloud_cover": pair["after"]["cloud_cover"],
                "properties": pair["after"]["properties"],
            },
        }
    
    def download_image(
        self,
        image,
        latitude: float,
        longitude: float,
        radius_km: float,
        output_path: str,
        scale: int = 10,
    ):
        """
        Downloads a Sentinel-2 RGB GeoTIFF directly from Earth Engine.
        """

        region = (
            ee.Geometry.Point([longitude, latitude])
            .buffer(radius_km * 1000)
        )

        image = (
            image
            .clip(region)
            .select(["B4", "B3", "B2"])
        )

        url = image.getDownloadURL(
            {
                "scale": scale,
                "region": region,
                "format": "GEO_TIFF",
                "filePerBand": False,
            }
        )

        print("\nDownloading Sentinel GeoTIFF...")

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True,
        )

        response = requests.get(
            url,
            stream=True,
        )

        response.raise_for_status()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(8192):
                file.write(chunk)

        print(f"\nGeoTIFF saved to:\n{output_path}")

        return output_path

    def get_latest_geotiff(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5,
        days: int = 365,
        max_cloud_cover: float = 30 ,
    ):
        """
        Downloads the newest Sentinel product through the CDSE
        ingestion pipeline and returns a locally generated RGB GeoTIFF.
        """

        latest = self.get_latest_image(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            days=days,
            max_cloud_cover=max_cloud_cover,
        )

        if latest is None:
            return None

        geotiff = self.ingestion.ingest(
            latest["product_id"]
        )

        return {
            "geotiff": geotiff,
            "image": latest["image"],
            "image_id": latest["image_id"],
            "product_id": latest["product_id"],
            "date": latest["date"],
            "cloud_cover": latest["cloud_cover"],
            "properties": latest["properties"],
        }
    
    def get_geotiff_from_metadata(self, metadata):
        """
        Downloads a GeoTIFF for any Sentinel metadata dictionary.
        """

        if metadata is None:
            return None

        geotiff = self.ingestion.ingest(
            metadata["product_id"]
        )

        return {
            "geotiff": geotiff,
            "image": metadata["image"],
            "image_id": metadata["image_id"],
            "product_id": metadata["product_id"],
            "date": metadata["date"],
            "cloud_cover": metadata["cloud_cover"],
            "properties": metadata["properties"],
        }


if __name__ == "__main__":

    service = SentinelService()

    result = service.get_latest_image(
        latitude=12.9716,
        longitude=77.5946,
    )

    if result is None:
        print("No Sentinel image found.")

    else:
        print("\nLatest Image Found")
        print("-----------------------------")
        print(f"Image ID    : {result['image_id']}")
        print(f"Product ID  : {result['product_id']}")
        print(f"Date        : {result['date']}")
        print(f"Cloud Cover : {result['cloud_cover']}") 