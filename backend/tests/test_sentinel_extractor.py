import shutil
from pathlib import Path

from backend.services.sentinel_extractor import SentinelExtractor


ZIP_PATH = (
    r"D:\projects\GeoSentinel_AI\backend\downloads"
    r"\S2C_MSIL2A_20260716T050651_N0512_R019_T43PGQ_20260716T095913.zip"
)

OUTPUT_DIR = r"D:\projects\GeoSentinel_AI\backend\temp_extract"


def main():
    output = Path(OUTPUT_DIR)

    if output.exists():
        shutil.rmtree(output)

    safe_folder = SentinelExtractor.extract(
        ZIP_PATH,
        OUTPUT_DIR,
    )

    print("\nExtraction Successful!")
    print(f"SAFE Folder:\n{safe_folder}")


if __name__ == "__main__":
    main()