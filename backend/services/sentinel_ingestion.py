from pathlib import Path

from backend.config import OUTPUT_DIR
from backend.services.imagery_downloader import ImageryDownloader
from backend.services.sentinel_extractor import SentinelExtractor
from backend.services.sentinel_preprocessor import SentinelPreprocessor


class SentinelIngestionService:
    """
    End-to-end Sentinel-2 ingestion pipeline.

    Metadata
        ↓
    Download
        ↓
    Extract SAFE
        ↓
    Generate RGB GeoTIFF

    Returns the GeoTIFF path ready for AI inference.
    """

    def __init__(
        self,
        download_directory="backend/downloads",
        extraction_directory="backend/temp_extract",
        output_directory=OUTPUT_DIR,
    ):
        self.download_directory = Path(download_directory)
        self.extraction_directory = Path(extraction_directory)
        self.output_directory = Path(output_directory)

    def ingest(self, product_id: str, output_path: str | None = None):
        """
        Download Sentinel product and convert it into
        an RGB GeoTIFF.

        Parameters
        ----------
        product_id : str

        Returns
        -------
        str
            Path to RGB GeoTIFF
        """

        print("\n" + "=" * 80)
        print("SENTINEL INGESTION")
        print("=" * 80)
        print(f"Product ID : {product_id}")

        downloader = ImageryDownloader()

        print("\nDownloading Sentinel product...")

        zip_path = self.download_directory / f"{product_id}.zip"

        zip_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        zip_path = downloader.download_product(
            product_id,
            str(zip_path),
        )

        print("\nDownloaded ZIP:")
        print(zip_path)

        print("\nExtracting SAFE product...")

        safe_folder = SentinelExtractor.extract(
            zip_path,
            self.extraction_directory,
        )

        print("\nSAFE Folder:")
        print(safe_folder)

        print("\nGenerating RGB GeoTIFF...")

        preprocessor = SentinelPreprocessor(
            str(safe_folder)
        )

        if output_path is None:
            output_geotiff = (
                self.output_directory
                / f"{product_id}_RGB.tif"
            )
        else:
            output_geotiff = Path(output_path)

        output_geotiff.parent.mkdir(parents=True, exist_ok=True)

        print("\nOutput GeoTIFF:")
        print(output_geotiff)

        preprocessor.create_rgb_geotiff(
            str(output_geotiff)
        )

        print("\nSentinel ingestion complete.")
        print("=" * 80)

        return str(output_geotiff)