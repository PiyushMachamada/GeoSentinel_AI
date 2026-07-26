import ee
import time


class EarthEngineExportService:
    """
    Handles exporting imagery from Google Earth Engine.
    """

    def __init__(self):
        self.project_id = "geosentinel-earthengine"

        try:
            ee.Initialize(project=self.project_id)
        except Exception:
            ee.Authenticate()
            ee.Initialize(project=self.project_id)


    def create_export_task(
    self,
    image,
    region,
    description,
    folder,
    filename,
    scale=10,
):
        """
        Creates an Earth Engine export task.
        """

        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder=folder,
            fileNamePrefix=filename,
            region=region.coordinates().getInfo(),
            scale=scale,
            fileFormat="GeoTIFF",
            maxPixels=1e13,
        )

        return task
    
    def start_task(self, task):
        """
        Starts an Earth Engine export task.
        """

        task.start()

        print("\nEarth Engine export task started.")

        return task
    
    def wait_for_completion(
    self,
    task,
    poll_interval=10,
):
        """
        Wait until an Earth Engine export finishes.
        """

        print("\nWaiting for export to finish...")

        while task.active():

            status = task.status()

            print(
                f"State: {status['state']}"
            )

            time.sleep(poll_interval)

        status = task.status()

        print(f"\nFinal State: {status['state']}")

        if status["state"] != "COMPLETED":

            raise RuntimeError(
                f"Export failed: {status}"
            )

        return status