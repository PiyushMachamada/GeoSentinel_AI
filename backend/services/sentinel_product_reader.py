from pathlib import Path

import numpy as np
import rasterio


class SentinelProductReader:
    """
    Reads Sentinel-2 SAFE products.

    Features
    --------
    - Locate spectral bands
    - Load individual bands
    - Load RGB imagery
    - Load common multispectral bands
    """

    def __init__(self, safe_directory: str):
        self.safe_directory = Path(safe_directory)

        if not self.safe_directory.exists():
            raise FileNotFoundError(
                f"SAFE directory not found:\n{safe_directory}"
            )

    # --------------------------------------------------
    # Internal helper
    # --------------------------------------------------

    def find_band(self, band_name: str) -> Path:
        """
        Locate the requested Sentinel band inside the SAFE product.

        For RGB/NIR bands we prefer the 10 m resolution image.
        """

        matches = sorted(
            self.safe_directory.rglob(f"*{band_name}*.jp2")
        )

        matches = [
            p
            for p in matches
            if "MSK_" not in p.name
        ]

        if not matches:
            raise FileNotFoundError(
                f"Band {band_name} not found."
            )

        print(f"\nSearching for {band_name}")
        print("-" * 60)

        for p in matches:
            print(p)

        preferred = None

        # Prefer 10 m products for RGB/NIR bands
        if band_name in ("B02", "B03", "B04", "B08"):

            for p in matches:
                path_str = str(p)

                if (
                    "R10m" in path_str
                    or "_10m" in path_str
                ):
                    preferred = p
                    break

        if preferred is None:
            preferred = matches[0]

        print(f"\nSelected {band_name}:")
        print(preferred)

        return preferred

    # --------------------------------------------------
    # Read one band
    # --------------------------------------------------

    def load_band(self, band_name: str):

        band_path = self.find_band(band_name)

        with rasterio.open(band_path) as src:
            return src.read(1)

    # --------------------------------------------------
    # RGB
    # --------------------------------------------------

    def load_rgb(self):

        red = self.load_band("B04")
        green = self.load_band("B03")
        blue = self.load_band("B02")

        return np.dstack(
            (
                red,
                green,
                blue,
            )
        )

    # --------------------------------------------------
    # Common multispectral bands
    # --------------------------------------------------

    def load_multispectral(self):

        return {
            "B02": self.load_band("B02"),
            "B03": self.load_band("B03"),
            "B04": self.load_band("B04"),
            "B08": self.load_band("B08"),
            "B11": self.load_band("B11"),
            "B12": self.load_band("B12"),
        }

    # --------------------------------------------------
    # Metadata
    # --------------------------------------------------

    def get_band_paths(self):

        return {
            "B02": self.find_band("B02"),
            "B03": self.find_band("B03"),
            "B04": self.find_band("B04"),
            "B08": self.find_band("B08"),
            "B11": self.find_band("B11"),
            "B12": self.find_band("B12"),
        }