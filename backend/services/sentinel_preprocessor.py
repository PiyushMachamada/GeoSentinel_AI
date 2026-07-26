from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from backend.services.sentinel_product_reader import SentinelProductReader


class SentinelPreprocessor:
    """
    Converts Sentinel SAFE products into AI-ready imagery.
    """

    def __init__(self, safe_directory: str):
        self.reader = SentinelProductReader(safe_directory)

    def create_rgb_geotiff(self, output_path: str):
        """
        Creates a 3-band GeoTIFF from Sentinel RGB bands.

        Returns
        -------
        str
            Path to the saved GeoTIFF.
        """

        band_paths = self.reader.get_band_paths()

        with rasterio.open(band_paths["B04"]) as src:
            print("\n===== Sentinel Tile Metadata =====")
            print("CRS:", src.crs)
            print("Transform:", src.transform)
            print("Bounds:", src.bounds)
            print("Width:", src.width)
            print("Height:", src.height)
            profile = src.profile.copy()

            red = src.read(1)

        with rasterio.open(band_paths["B03"]) as src:
            green = src.read(1)

        with rasterio.open(band_paths["B02"]) as src:
            blue = src.read(1)

        profile.update(
            driver="GTiff",
            count=3,
            dtype=red.dtype,
            compress="lzw"
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(red, 1)
            dst.write(green, 2)
            dst.write(blue, 3)

        return str(output_path)