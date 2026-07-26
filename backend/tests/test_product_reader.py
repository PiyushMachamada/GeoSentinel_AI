from backend.services.sentinel_product_reader import SentinelProductReader


SAFE_FOLDER = r"D:\projects\GeoSentinel_AI\backend\downloads\S2C_MSIL2A_20260716T050651_N0512_R019_T43PGQ_20260716T095913\S2C_MSIL2A_20260716T050651_N0512_R019_T43PGQ_20260716T095913.SAFE"


def main():
    reader = SentinelProductReader(SAFE_FOLDER)

    print("Blue :", reader.find_band("B02"))
    print("Green:", reader.find_band("B03"))
    print("Red  :", reader.find_band("B04"))
    print("NIR  :", reader.find_band("B08"))


if __name__ == "__main__":
    main()