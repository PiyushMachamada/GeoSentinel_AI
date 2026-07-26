import os

from backend.services.imagery_downloader import ImageryDownloader


PRODUCT_ID = (
    "S2C_MSIL2A_20260716T050651_N0512_R019_T43PGQ_20260716T095913"
)


def main():
    print("=" * 60)
    print("GeoSentinel AI - CDSE Download Test")
    print("=" * 60)

    downloader = ImageryDownloader()

    output_path = os.path.join(
        "backend",
        "downloads",
        f"{PRODUCT_ID}.zip"
    )

    downloaded_file = downloader.download_product(
        PRODUCT_ID,
        output_path,
    )

    print("\n✅ Download Complete")
    print(f"Saved to: {downloaded_file}")


if __name__ == "__main__":
    main()