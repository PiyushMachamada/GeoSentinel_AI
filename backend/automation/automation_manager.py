import time
import traceback

from backend.monitoring.aoi_manager import AOIManager
from backend.models.geosentinel_pipeline import GeoSentinelPipeline


class AutomationManager:
    """
    Runs GeoSentinel analyses for one or more AOIs.
    """

    def __init__(self):
        self.aoi_manager = AOIManager()
        self.success = 0
        self.failed = 0
        self.results = []

    def run_aoi(self, aoi, before_image, after_image):
        print("\n" + "=" * 70)
        print(f"Processing {aoi.id} - {aoi.name}")
        print("=" * 70)

        start = time.time()

        try:
            pipeline = GeoSentinelPipeline(
                before_image=before_image,
                after_image=after_image,
                aoi_id=aoi.id
            )

            result = pipeline.run()

            elapsed = round(time.time() - start, 2)

            self.success += 1

            self.results.append({
                "aoi": aoi.id,
                "status": "SUCCESS",
                "time": elapsed,
                "confidence": result.get("mission_confidence", 0)
            })

            return result

        except Exception:
            elapsed = round(time.time() - start, 2)

            self.failed += 1

            traceback.print_exc()

            self.results.append({
                "aoi": aoi.id,
                "status": "FAILED",
                "time": elapsed
            })

            return None

    def print_summary(self):

        print("\n")
        print("=" * 70)
        print("GeoSentinel Automation Summary")
        print("=" * 70)

        for result in self.results:

            print(
                f"{result['aoi']:10}"
                f"{result['status']:10}"
                f"{result['time']:8}s"
            )

            if "confidence" in result:

                print(
                    f"   Mission Confidence : "
                    f"{result['confidence']}%"
                )

        print("-" * 70)

        print(f"Successful Missions : {self.success}")

        print(f"Failed Missions     : {self.failed}")

        print("=" * 70)

    def run_all(self, before_image, after_image):
        """
        Run GeoSentinel for every active AOI.
        """

        active_aois = [
            aoi
            for aoi in self.aoi_manager.get_all()
            if aoi.active
        ]

        print("\n" + "=" * 70)
        print(f"Found {len(active_aois)} active AOIs")
        print("=" * 70)

        overall_start = time.time()

        for aoi in active_aois:

            self.run_aoi(
                aoi,
                before_image,
                after_image
            )

        total_time = round(
            time.time() - overall_start,
            2
        )

        self.print_summary()

        print(f"\nTotal Execution Time : {total_time} sec")


    def run_single(self, aoi_id, before_image, after_image):

        aoi = self.aoi_manager.get_by_id(aoi_id)

        if aoi is None:
            raise ValueError(
                f"Unknown AOI : {aoi_id}"
            )

        self.run_aoi(
            aoi,
            before_image,
            after_image
        )

        self.print_summary()

    def main():

        manager = AutomationManager()

        BEFORE_IMAGE = "datasets/geotiff/before.tif"

        AFTER_IMAGE = "datasets/geotiff/after.tif"

        manager.run_single(
            "AOI001",
            BEFORE_IMAGE,
            AFTER_IMAGE
        )


    if __name__ == "__main__":
        main()