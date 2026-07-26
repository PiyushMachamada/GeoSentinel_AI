import ee
import geemap


class SentinelService:
    """
    GeoSentinel Sentinel-2 Service

    Downloads BEFORE and AFTER Sentinel-2 imagery for an AOI.

    Output:
        {
            "before_path": "...",
            "after_path": "..."
        }
    """

    def __init__(self):

        try:
            ee.Initialize(project="geosentinel-earthengine")

        except Exception:
            ee.Initialize()

    # ======================================================
    # Cloud Mask
    # ======================================================

    @staticmethod
    def _mask_clouds(image):
        """
        Removes clouds and cloud shadows using the
        Sentinel-2 Scene Classification Layer (SCL).
        """

        scl = image.select("SCL")

        mask = (
            scl.neq(3)      # Cloud shadow
            .And(scl.neq(8))   # Medium cloud
            .And(scl.neq(9))   # High cloud
            .And(scl.neq(10))  # Thin cirrus
            .And(scl.neq(11))  # Snow
        )

        return image.updateMask(mask)

    # ======================================================
    # Collection
    # ======================================================

    def _collection(
        self,
        aoi,
        start_date,
        end_date,
        max_cloud,
    ):

        return (

            ee.ImageCollection(
                "COPERNICUS/S2_SR_HARMONIZED"
            )

            .filterBounds(
                aoi.to_ee_geometry()
            )

            .filterDate(
                start_date,
                end_date,
            )

            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    max_cloud,
                )
            )

            .map(
                self._mask_clouds
            )

            .sort(
                "CLOUDY_PIXEL_PERCENTAGE"
            )

        )

    # ======================================================
    # Export
    # ======================================================

    def _export(
        self,
        image,
        roi,
        output_path,
    ):

        geemap.ee_export_image(
            image,
            filename=output_path,
            region=roi,
            scale=10,
            file_per_band=False,
        )

    # ======================================================
    # Download
    # ======================================================

    def download(
        self,
        aoi,
        output_paths,
        max_cloud=20,
    ):

        print("\n========================================")
        print("Sentinel-2 Download")
        print("========================================")

        roi = aoi.to_ee_geometry()

        before_path = str(
            output_paths["before_image"]
        )

        after_path = str(
            output_paths["after_image"]
        )

        # -----------------------------------------
        # BEFORE
        # -----------------------------------------

        print("\nSearching BEFORE imagery...")

        before_collection = self._collection(

            aoi,

            aoi.before_start,

            aoi.before_end,

            max_cloud,

        )

        before_count = before_collection.size().getInfo()

        print(f"Images Found : {before_count}")

        if before_count == 0:

            raise RuntimeError(
                "No Sentinel-2 BEFORE imagery found."
            )

        before_image = (

            before_collection

            .median()

            .clip(roi)

            .select(
                [
                    "B2",
                    "B3",
                    "B4",
                    "B8",
                ]
            )

        )

        # -----------------------------------------
        # AFTER
        # -----------------------------------------

        print("\nSearching AFTER imagery...")

        after_collection = self._collection(

            aoi,

            aoi.after_start,

            aoi.after_end,

            max_cloud,

        )

        after_count = after_collection.size().getInfo()

        print(f"Images Found : {after_count}")

        if after_count == 0:

            raise RuntimeError(
                "No Sentinel-2 AFTER imagery found."
            )

        after_image = (

            after_collection

            .median()

            .clip(roi)

            .select(
                [
                    "B2",
                    "B3",
                    "B4",
                    "B8",
                ]
            )

        )

        # -----------------------------------------
        # Export
        # -----------------------------------------

        print("\nExporting BEFORE GeoTIFF...")

        self._export(

            before_image,

            roi,

            before_path,

        )

        print("Saved :", before_path)

        print("\nExporting AFTER GeoTIFF...")

        self._export(

            after_image,

            roi,

            after_path,

        )

        print("Saved :", after_path)

        print("\n========================================")
        print("Sentinel Download Complete")
        print("========================================")

        return {

            "before_path": before_path,

            "after_path": after_path,

        }