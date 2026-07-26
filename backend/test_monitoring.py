from backend.monitoring.monitoring_service import MonitoringService


def main():

    print("\n" + "=" * 80)
    print("GeoSentinel Persistent Monitoring Test")
    print("=" * 80)

    service = MonitoringService()

    service.run()

    print("\n" + "=" * 80)
    print("Monitoring Test Finished")
    print("=" * 80)


if __name__ == "__main__":
    main()