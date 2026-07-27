from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform
from rasterio.windows import Window, from_bounds

from backend.services.sentinel_product_reader import SentinelProductReader


class SentinelPreprocessor:
    """
    Converts Sentinel SAFE products into AI-ready imagery.
    """

    def __init__(self, safe_directory: str):
        self.reader = SentinelProductReader(safe_directory)

    def _build_crop_window(
        self,
        src,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> Window:
        center_x, center_y = transform(
            "EPSG:4326",
            src.crs,
            [longitude],
            [latitude],
        )
        center_x = center_x[0]
        center_y = center_y[0]
        radius_m = radius_km * 1000

        if not (
            src.bounds.left <= center_x <= src.bounds.right
            and src.bounds.bottom <= center_y <= src.bounds.top
        ):
            raise ValueError(
                "Selected Sentinel tile does not contain the AOI center."
            )

        crop_window = from_bounds(
            center_x - radius_m,
            center_y - radius_m,
            center_x + radius_m,
            center_y + radius_m,
            src.transform,
        )

        dataset_window = Window(
            col_off=0,
            row_off=0,
            width=src.width,
            height=src.height,
        )

        crop_window = crop_window.intersection(
            dataset_window
        )

        crop_window = crop_window.round_offsets().round_lengths()

        if crop_window.width <= 0 or crop_window.height <= 0:
            raise ValueError(
                "AOI crop window does not overlap the Sentinel tile."
            )

        print("\n===== AOI Crop Metadata =====")
        print("AOI Latitude:", latitude)
        print("AOI Longitude:", longitude)
        print("AOI Radius km:", radius_km)
        print("AOI Center X:", center_x)
        print("AOI Center Y:", center_y)
        print("Crop Window:", crop_window)

        return crop_window

    def create_rgb_geotiff(
        self,
        output_path: str,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_km: float | None = None,
    ):
        """
        Creates a 3-band GeoTIFF from Sentinel RGB bands.

        Returns
        -------
        str
            Path to the saved GeoTIFF.
        """

        band_paths = self.reader.get_band_paths()
        crop_window = None

        with rasterio.open(band_paths["B04"]) as src:
            print("\n===== Sentinel Tile Metadata =====")
            print("CRS:", src.crs)
            print("Transform:", src.transform)
            print("Bounds:", src.bounds)
            print("Width:", src.width)
            print("Height:", src.height)
            profile = src.profile.copy()

            if (
                latitude is not None
                and longitude is not None
                and radius_km is not None
            ):
                crop_window = self._build_crop_window(
                    src,
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km,
                )
                red = src.read(1, window=crop_window)
                profile.update(
                    width=red.shape[1],
                    height=red.shape[0],
                    transform=src.window_transform(crop_window),
                )
            else:
                red = src.read(1)

        with rasterio.open(band_paths["B03"]) as src:
            if crop_window is None:
                green = src.read(1)
            else:
                green = src.read(1, window=crop_window)

        with rasterio.open(band_paths["B02"]) as src:
            if crop_window is None:
                blue = src.read(1)
            else:
                blue = src.read(1, window=crop_window)

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