from backend.services.imagery_downloader import ImageryDownloader


def main():
    print("=" * 60)
    print("GeoSentinel AI - CDSE Authentication Test")
    print("=" * 60)

    downloader = ImageryDownloader()

    token = downloader.authenticate()

    print("\n✅ Authentication Successful")
    print(f"Token Length: {len(token)}")


if __name__ == "__main__":
    main()