"""Shared Google Earth Engine primitives for Sentinel service adapters.

The pipeline and monitoring services deliberately remain separate because they
have different acquisition semantics. This module owns only common Earth
Engine initialization, AOI geometry, and Sentinel-2 collection construction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import ee
from google.oauth2 import service_account


SENTINEL2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"


def initialize_earth_engine(
    *,
    project: str | None = None,
    credentials_path: str | Path | None = None,
) -> None:
    """Initialize Earth Engine using the caller's existing auth strategy."""
    if credentials_path is not None:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=[
                "https://www.googleapis.com/auth/earthengine",
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )
        ee.Initialize(credentials=credentials, project=project)
        return

    if project is None:
        ee.Initialize()
        return

    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Initialize()


def point_buffer_region(
    *, latitude: float, longitude: float, radius_km: float
) -> Any:
    """Return a circular Earth Engine AOI around a longitude/latitude point."""
    return ee.Geometry.Point([longitude, latitude]).buffer(radius_km * 1000)


def sentinel2_collection(
    *,
    region: Any,
    start_date: str,
    end_date: str,
    max_cloud_cover: float,
    sort_property: str,
    descending: bool = False,
) -> Any:
    """Build a filtered, sorted Sentinel-2 SR Harmonized collection."""
    return (
        ee.ImageCollection(SENTINEL2_COLLECTION)
        .filterBounds(region)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover))
        .sort(sort_property, descending)
    )
