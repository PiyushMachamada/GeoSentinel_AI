import logging

from backend.monitoring.scheduler import Scheduler
from backend.config import MONITOR_INTERVAL_MINUTES


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    logging.info("Starting GeoSentinel Monitoring Scheduler...")

    scheduler = Scheduler(
        interval_minutes=MONITOR_INTERVAL_MINUTES
    )  # 1 minute for testing
    scheduler.start()


if __name__ == "__main__":
    main()