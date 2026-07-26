import ee


class SentinelSearch:
    """
    Searches Sentinel-2 imagery for a given AOI and date range.

    Responsibilities
    ----------------
    - Query Sentinel-2
    - Filter by AOI
    - Filter by date
    - Filter by cloud cover
    - Select the best available image

    Does NOT
    --------
    - Download imagery
    - Export GeoTIFFs
    - Run preprocessing
    """

    COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"

    def __init__(self):

        try:
            ee.Initialize()

        except Exception:
            ee.Initialize(project="geosentinel-earthengine")

    def search(
        self,
        aoi,
        start_date,
        end_date,
        max_cloud=10,
    ):
        """
        Search Sentinel-2 imagery.

        Parameters
        ----------
        aoi : AOI
            AOI object from AOIManager

        start_date : str
            YYYY-MM-DD

        end_date : str
            YYYY-MM-DD

        max_cloud : int
            Maximum cloud percentage.

        Returns
        -------
        ee.ImageCollection
        """

        roi = aoi.to_ee_geometry()

        collection = (

            ee.ImageCollection(self.COLLECTION)

            .filterBounds(roi)

            .filterDate(start_date, end_date)

            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    max_cloud,
                )
            )

            .sort("CLOUDY_PIXEL_PERCENTAGE")

        )

        return collection

    def get_best_image(
        self,
        aoi,
        start_date,
        end_date,
        max_cloud=10,
    ):
        """
        Returns the least cloudy Sentinel image.
        """

        collection = self.search(
            aoi,
            start_date,
            end_date,
            max_cloud,
        )

        size = collection.size().getInfo()

        if size == 0:

            raise RuntimeError(
                "No Sentinel-2 imagery found."
            )

        image = collection.first()

        metadata = image.toDictionary([
            "PRODUCT_ID",
            "CLOUDY_PIXEL_PERCENTAGE",
            "system:time_start",
        ]).getInfo()

        print("\nSelected Sentinel Image")
        print("-" * 60)

        print(
            f"Product : {metadata.get('PRODUCT_ID')}"
        )

        print(
            f"Clouds  : {metadata.get('CLOUDY_PIXEL_PERCENTAGE')}%"
        )

        print("-" * 60)

        return image

    def get_median_composite(
        self,
        aoi,
        start_date,
        end_date,
        max_cloud=10,
    ):
        """
        Returns a cloud-filtered median composite.

        This is generally better than using
        a single Sentinel acquisition.
        """

        collection = self.search(
            aoi,
            start_date,
            end_date,
            max_cloud,
        )

        if collection.size().getInfo() == 0:

            raise RuntimeError(
                "No Sentinel imagery found."
            )

        return collection.median()