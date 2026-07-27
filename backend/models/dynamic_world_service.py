from pathlib import Path

import ee
import geemap


def download_dynamic_world(aoi, output_paths):
    """
    Downloads Dynamic World imagery for a given AOI.

    Parameters
    ----------
    aoi : AOI
        AOI object from AOIManager.

    output_paths : dict
        Dictionary returned by OutputManager.default_files().

    Returns
    -------
    dict
        Downloaded file paths.
    """

    print("\n==========================================")
    print("Downloading Dynamic World")
    print("==========================================")

    # ==========================================
    # Initialize Earth Engine
    # ==========================================

    try:

        ee.Initialize(project="geosentinel-earthengine")

        print("Earth Engine initialized successfully.")

    except Exception as e:

        raise RuntimeError(
            f"Failed to initialize Earth Engine:\n{e}"
        )

    # ==========================================
    # AOI
    # ==========================================

    roi = aoi.to_ee_geometry()

    # ==========================================
    # BEFORE COLLECTION
    # ==========================================

    before_collection = (

        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")

        .filterBounds(roi)

        .filterDate(
            aoi.before_start,
            aoi.before_end,
        )

    )

    if before_collection.size().getInfo() == 0:

        raise RuntimeError(
            f"No Dynamic World imagery found "
            f"between {aoi.before_start} "
            f"and {aoi.before_end}."
        )

    before_image = (

        before_collection

        .mode()

        .select("label")

    )

    # ==========================================
    # AFTER COLLECTION
    # ==========================================

    after_collection = (

        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")

        .filterBounds(roi)

        .filterDate(
            aoi.after_start,
            aoi.after_end,
        )

    )

    if after_collection.size().getInfo() == 0:

        raise RuntimeError(
            f"No Dynamic World imagery found "
            f"between {aoi.after_start} "
            f"and {aoi.after_end}."
        )

    after_image = (

        after_collection

        .mode()

        .select("label")

    )

    # ==========================================
    # Output Paths
    # ==========================================

    before_path = str(
        output_paths["dynamic_world_before"]
    )

    after_path = str(
        output_paths["dynamic_world_after"]
    )

    # ==========================================
    # Download BEFORE
    # ==========================================

    print("\nDownloading BEFORE Dynamic World...")

    geemap.ee_export_image(

        before_image,

        filename=before_path,

        scale=10,

        region=roi,

    )

    if not Path(before_path).exists():
        raise RuntimeError(
            "Dynamic World BEFORE export did not produce a raster file."
        )

    print("Saved:", before_path)

    # ==========================================
    # Download AFTER
    # ==========================================

    print("\nDownloading AFTER Dynamic World...")

    geemap.ee_export_image(

        after_image,

        filename=after_path,

        scale=10,

        region=roi,

    )

    if not Path(after_path).exists():
        raise RuntimeError(
            "Dynamic World AFTER export did not produce a raster file."
        )

    print("Saved:", after_path)

    print("\n==========================================")
    print("Dynamic World Download Complete")
    print("==========================================")

    return {

        "before_path": before_path,

        "after_path": after_path,

    }


# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    from backend.monitoring.aoi_manager import AOIManager
    from backend.utils.output_manager import OutputManager

    manager = AOIManager()

    aoi = manager.get_by_id("AOI001")

    outputs = OutputManager(
        aoi.id
    ).default_files()

    results = download_dynamic_world(
        aoi,
        outputs,
    )

    print("\nDownload Results")
    print(results)