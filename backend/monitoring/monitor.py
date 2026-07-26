from datetime import datetime
import logging

from backend.monitoring.aoi_manager import AOI
from backend.monitoring.image_history import ImageHistory
from backend.database.monitoring_state import MonitoringStateDB


from backend.services.sentinel import SentinelService
from backend.models.geosentinel_pipeline import run_pipeline

logger = logging.getLogger(__name__)


class Monitor:
    """
    Monitors a single AOI for new Sentinel imagery.
    """

    from backend.config import MAX_CLOUD_COVER

    def __init__(self):

        self.sentinel = SentinelService()

        self.state_db = MonitoringStateDB()

        self.history = ImageHistory()

    def monitor(self, aoi: AOI):

        logger.info("=" * 70)
        logger.info("Monitoring AOI : %s", aoi.id)
        logger.info("Name           : %s", aoi.name)
        logger.info(
            "Location       : (%s, %s)",
            aoi.latitude,
            aoi.longitude,
        )
        logger.info("Radius         : %.2f km", aoi.radius_km)
        logger.info("=" * 70)

        # ==========================================================
        # STEP 1 : Retrieve newest Sentinel pair
        # ==========================================================

        pair = self.sentinel.get_image_pair(
            latitude=aoi.latitude,
            longitude=aoi.longitude,
            radius_km=aoi.radius_km,
            max_cloud_cover=self.MAX_CLOUD_COVER,
        )
        print(f"\n[{aoi.id}] Image pair found: {pair is not None}")

        if pair is None:

            logger.warning(
                "Less than two Sentinel images available."
            )

            return None

        latest = pair["after"]
        previous = pair["before"]

        print("\n==============================")
        print("BEFORE IMAGE")
        print("==============================")
        print(previous["product_id"])
        print(previous["date"])
        print(previous["image_id"])

        print("\n==============================")
        print("AFTER IMAGE")
        print("==============================")
        print(latest["product_id"])
        print(latest["date"])
        print(latest["image_id"])

        logger.info(
            "Previous Product : %s",
            previous["product_id"],
        )

        logger.info(
            "Latest Product   : %s",
            latest["product_id"],
        )

        logger.info(
            "Latest Date      : %s",
            latest["date"],
        )

        # ==========================================================
        # STEP 2 : Skip if already processed
        # ==========================================================

        state = self.state_db.get_state(aoi.id)

        if (
            state is not None
            and state["latest_product_id"] == latest["product_id"]
        ):

            logger.info(
                "No new Sentinel imagery."
            )

            return None

        logger.info(
            "New Sentinel acquisition detected."
        )

        # ==========================================================
        # STEP 3 : Download BOTH images
        # ==========================================================

        downloads = self.sentinel.download_pair_aoi(
            pair=pair,
            latitude=aoi.latitude,
            longitude=aoi.longitude,
            radius_km=aoi.radius_km,
        )

        print(f"[{aoi.id}] Images downloaded successfully")

        before_download = downloads["before"]
        after_download = downloads["after"]

        # ==========================================================
        # STEP 4 : Save into image history
        # ==========================================================

        self.history.save_image(
            aoi_id=aoi.id,
            image_path=before_download["geotiff"],
            acquisition_date=before_download["date"],
        )

        self.history.save_image(
            aoi_id=aoi.id,
            image_path=after_download["geotiff"],
            acquisition_date=after_download["date"],
        )

        before = self.history.get_previous_image(
            aoi.id
        )

        after = self.history.get_latest_image(
            aoi.id
        )

        if before is None or after is None:

            logger.error(
                "Unable to initialize image history."
            )

            return None

        logger.info(
            "Previous Image : %s",
            before,
        )

        logger.info(
            "Latest Image   : %s",
            after,
        )

        # ==========================================================
        # STEP 5 : Launch GeoSentinel
        # ==========================================================

        logger.info("Launching GeoSentinel Pipeline...")

        logger.info("=" * 70)
        logger.info("STARTING PIPELINE")
        logger.info("AOI ID   : %s", aoi.id)
        logger.info("AOI Name : %s", aoi.name)
        logger.info("=" * 70)

        print("=" * 60)
        print("MONITOR")
        print(f"AOI ID: {aoi.id}")
        print("=" * 60)

        print(f"[{aoi.id}] Starting GeoSentinel pipeline...")

        try:

            results = run_pipeline(
                before_image=str(before),
                after_image=str(after),
                aoi_id=aoi.id,
            )

            print(f"[{aoi.id}] Pipeline completed successfully")

            logger.info("=" * 70)
            logger.info("PIPELINE COMPLETED")
            logger.info("AOI ID   : %s", aoi.id)
            logger.info("AOI Name : %s", aoi.name)
            logger.info("=" * 70)

            self.state_db.update_state(
                aoi_id=aoi.id,
                product_id=latest["product_id"],
                analysis_date=latest["date"],
                checked_time=datetime.utcnow().isoformat(),
                status="ACTIVE",
            )

            logger.info("Monitoring state updated.")

            return results

        except Exception:

            logger.exception("=" * 70)
            logger.exception("PIPELINE FAILED")
            logger.exception("AOI ID   : %s", aoi.id)
            logger.exception("AOI Name : %s", aoi.name)
            logger.exception("=" * 70)

            self.state_db.update_state(
                aoi_id=aoi.id,
                product_id=latest["product_id"],
                analysis_date=latest["date"],
                checked_time=datetime.utcnow().isoformat(),
                status="FAILED",
            )

            return None