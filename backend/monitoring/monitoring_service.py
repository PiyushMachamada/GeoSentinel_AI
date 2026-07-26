from backend.monitoring.aoi_manager import AOIManager
from backend.monitoring.monitor import Monitor
import traceback


class MonitoringService:

    def __init__(self):
        self.aoi_manager = AOIManager()
        self.monitor = Monitor()

    def run(self):

        print("\nLoading active AOIs...")

        aois = self.aoi_manager.get_all()

        active_count = 0

        for aoi in aois:

            if not aoi.active:
                continue

            active_count += 1

            # DEBUG
            print(f"\n{'='*60}")
            print(f"Processing {aoi.id} - {aoi.name}")
            print(f"{'='*60}")

            try:

                self.monitor.monitor(aoi)

            except Exception as e:
                print(f"\nError monitoring {aoi.id}:")
                traceback.print_exc()

        print("\n" + "=" * 70)
        print(f"Monitoring cycle complete.")
        print(f"Active AOIs checked: {active_count}")
        print("=" * 70)

if __name__ == "__main__":
    service = MonitoringService()
    service.run()