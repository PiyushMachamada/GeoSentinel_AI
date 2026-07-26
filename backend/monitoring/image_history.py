from pathlib import Path
import shutil


class ImageHistory:
    """
    Maintains historical Sentinel GeoTIFFs for every AOI.

    Structure:

    datasets/
        monitoring/
            AOI001/
                2025-07-01.tif
                2025-07-11.tif
                2025-07-21.tif

            AOI002/
                ...
    """

    ROOT = Path("datasets/monitoring")

    def __init__(self):

        self.ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Save Image
    # ==========================================================

    def save_image(
        self,
        aoi_id,
        image_path,
        acquisition_date,
    ):
        """
        Saves a GeoTIFF into the AOI history.

        If the file already exists, it is not copied again.
        """

        folder = self.ROOT / aoi_id

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            folder /
            f"{acquisition_date}.tif"
        )

        if destination.exists():

            return destination

        shutil.copy2(
            image_path,
            destination,
        )

        return destination

    # ==========================================================
    # List Images
    # ==========================================================

    def get_images(self, aoi_id):
        """
        Returns all GeoTIFFs sorted chronologically.
        """

        folder = self.ROOT / aoi_id

        if not folder.exists():
            return []

        images = sorted(
            folder.glob("*.tif")
        )

        return images

    # ==========================================================
    # Latest Image
    # ==========================================================

    def get_latest_image(self, aoi_id):

        images = self.get_images(aoi_id)

        if not images:
            return None

        return images[-1]

    # ==========================================================
    # Previous Image
    # ==========================================================

    def get_previous_image(self, aoi_id):

        images = self.get_images(aoi_id)

        if len(images) < 2:
            return None

        return images[-2]

    # ==========================================================
    # Image Count
    # ==========================================================

    def image_count(self, aoi_id):

        return len(
            self.get_images(aoi_id)
        )

    # ==========================================================
    # Has Enough History
    # ==========================================================

    def has_pair(self, aoi_id):

        return self.image_count(aoi_id) >= 2

    # ==========================================================
    # Most Recent Pair
    # ==========================================================

    def get_latest_pair(self, aoi_id):

        if not self.has_pair(aoi_id):
            return None

        images = self.get_images(aoi_id)

        return (
            images[-2],
            images[-1],
        )

    # ==========================================================
    # Clear History
    # ==========================================================

    def clear_history(self, aoi_id):
        """
        Deletes all stored imagery for an AOI.
        Useful for testing or resetting monitoring.
        """

        folder = self.ROOT / aoi_id

        if not folder.exists():
            return

        shutil.rmtree(folder)

    # ==========================================================
    # AOIs with History
    # ==========================================================

    def list_aois(self):

        return sorted(
            [
                folder.name
                for folder in self.ROOT.iterdir()
                if folder.is_dir()
            ]
        )