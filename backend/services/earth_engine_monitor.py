from backend.monitoring.aoi_manager import AOIManager
from backend.services.sentinel import SentinelService


class EarthEngineMonitor:

    def __init__(self):

        self.sentinel = SentinelService()
        self.aoi_manager = AOIManager()

        print("\nEarth Engine Monitor Initialized.")

    def load_active_aois(self):
        """
        Returns all active AOIs.
        """

        return [
            aoi
            for aoi in self.aoi_manager.get_all()
            if aoi.active
        ]
    
    def check_latest_images(self):
        """
        Checks the latest Sentinel-2 image for every active AOI.
        """

        aois = self.load_active_aois()

        print("\nChecking Sentinel-2 imagery...")

        for aoi in aois:

            print(f"\n{'='*60}")
            print(f"AOI: {aoi.name}")
            print(f"{'='*60}")

            latest = self.sentinel.get_latest_image(
                latitude=aoi.latitude,
                longitude=aoi.longitude,
                radius_km=aoi.radius_km,
            )

            if latest is None:
                print("No Sentinel image found.")
                continue

            print("\nReturned Metadata:")
            print(latest)

if __name__ == "__main__":

    monitor = EarthEngineMonitor()

    monitor.check_latest_images()