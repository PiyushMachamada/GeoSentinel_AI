import os
from datetime import datetime, timedelta
from pathlib import Path

import ee
from backend.config import OUTPUT_DIR
from backend.services.earth_engine import (
    initialize_earth_engine,
    point_buffer_region,
    sentinel2_collection,
)
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

        initialize_earth_engine(
            project=self.project_id,
            credentials_path=service_account_file,
        )

        print("✓ Earth Engine initialized with service account.")

        self.ingestion = SentinelIngestionService()

    def _build_metadata(self, image):
        properties = image.toDictionary().getInfo()
        timestamp = image.get("system:time_start").getInfo()
        centroid = image.geometry().centroid(1).coordinates().getInfo()

        acquisition_date = None

        if timestamp:
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
            "_timestamp_ms": timestamp,
            "_centroid_lon": centroid[0],
            "_centroid_lat": centroid[1],
        }

    def _select_observations(
        self,
        collection,
        latitude: float,
        longitude: float,
        limit: int = 12,
    ):
        count = collection.size().getInfo()

        if count == 0:
            return []

        image_list = collection.toList(
            min(count, limit)
        )

        selected_by_datatake = {}

        for index in range(min(count, limit)):
            image = ee.Image(image_list.get(index))
            metadata = self._build_metadata(image)
            datatake_key = metadata["properties"].get(
                "DATATAKE_IDENTIFIER"
            ) or metadata["image_id"]

            selection_distance = (
                (metadata["_centroid_lat"] - latitude) ** 2
                + (metadata["_centroid_lon"] - longitude) ** 2
            )

            current = selected_by_datatake.get(
                datatake_key
            )

            if (
                current is None
                or selection_distance < current["_selection_distance"]
            ):
                metadata["_selection_distance"] = selection_distance
                selected_by_datatake[datatake_key] = metadata

        observations = sorted(
            selected_by_datatake.values(),
            key=lambda item: item["_timestamp_ms"],
            reverse=True,
        )

        for item in observations:
            item.pop("_timestamp_ms", None)
            item.pop("_centroid_lon", None)
            item.pop("_centroid_lat", None)
            item.pop("_selection_distance", None)

        return observations

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

        region = point_buffer_region(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        collection = sentinel2_collection(
            region=region,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            max_cloud_cover=max_cloud_cover,
            sort_property="system:time_start",
            descending=False,
        )

        count = collection.size().getInfo()

        print(f"\nSentinel Images Found: {count}")

        if count == 0:
            return None

        observations = self._select_observations(
            collection,
            latitude=latitude,
            longitude=longitude,
        )

        if not observations:
            return None

        return observations[0]
    
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

        region = point_buffer_region(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        collection = sentinel2_collection(
            region=region,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=latest_dt.strftime("%Y-%m-%d"),
            max_cloud_cover=max_cloud_cover,
            sort_property="system:time_start",
            descending=False,
        )

        observations = self._select_observations(
            collection,
            latitude=latitude,
            longitude=longitude,
        )

        if not observations:
            return None

        return observations[0]
    
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

        region = point_buffer_region(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        collection = sentinel2_collection(
            region=region,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            max_cloud_cover=max_cloud_cover,
            sort_property="system:time_start",
            descending=False,
        )

        observations = self._select_observations(
            collection,
            latitude=latitude,
            longitude=longitude,
        )

        if len(observations) < 2:
            return None

        return {
            "before": observations[1],
            "after": observations[0],
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
        output_paths=None,
        output_directory: str | None = None,
    ):
        """
        Downloads the before/after Sentinel images using product IDs and
        the Sentinel ingestion pipeline.

        If output_paths are provided, the generated GeoTIFFs will be
        written into the supplied OutputManager paths.

        Returns
        -------
        {
            "before": {...},
            "after": {...}
        }
        """

        if output_paths is not None:
            before_path = str(output_paths["before_image"])
            after_path = str(output_paths["after_image"])
        else:
            output_directory = output_directory or OUTPUT_DIR
            os.makedirs(output_directory, exist_ok=True)
            before_path = os.path.join(
                output_directory,
                f"{pair['before']['product_id']}_RGB.tif",
            )
            after_path = os.path.join(
                output_directory,
                f"{pair['after']['product_id']}_RGB.tif",
            )

        before_result = self.get_geotiff_from_metadata(
            pair["before"],
            output_path=before_path,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        after_result = self.get_geotiff_from_metadata(
            pair["after"],
            output_path=after_path,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        return {
            "before": before_result,
            "after": after_result,
        }
    
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
    
    def get_geotiff_from_metadata(
        self,
        metadata,
        output_path: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_km: float | None = None,
    ):
        """
        Generates a GeoTIFF for a Sentinel metadata dictionary.
        """

        if metadata is None:
            return None

        geotiff = self.ingestion.ingest(
            metadata["product_id"],
            output_path=output_path,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
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