from backend.services.imagery_downloader import ImageryDownloader


PRODUCT_ID = (
    "S2C_MSIL2A_20260716T050651_N0512_R019_T43PGQ_20260716T095913"
)


def main():
    print("=" * 60)
    print("GeoSentinel AI - CDSE Product Lookup Test")
    print("=" * 60)

    downloader = ImageryDownloader()

    uuid = downloader.get_product_uuid(PRODUCT_ID)

    print("\n✅ Product Found")
    print(f"UUID: {uuid}")


if __name__ == "__main__":
    main()