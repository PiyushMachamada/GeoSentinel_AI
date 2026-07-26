import time

from backend.monitoring.monitoring_service import MonitoringService


class Scheduler:
    """
    Runs GeoSentinel monitoring at fixed intervals.
    """

    def __init__(self, interval_minutes=60):

        self.interval = interval_minutes * 60

        self.service = MonitoringService()

    def start(self):

        print("\nGeoSentinel Scheduler Started.")

        print(
            f"Monitoring every {self.interval // 60} minutes."
        )

        while True:

            print("\n" + "=" * 70)
            print("Starting monitoring cycle...")
            print("=" * 70)

            try:

                self.service.run()

            except Exception as e:

                print(f"\nScheduler Error: {e}")

            print(
                f"\nSleeping for {self.interval // 60} minutes..."
            )

            time.sleep(self.interval)


if __name__ == "__main__":

    Scheduler(interval_minutes=60).start()