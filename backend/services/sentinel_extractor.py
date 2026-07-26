from pathlib import Path
import zipfile
import shutil


class SentinelExtractor:
    """
    Extract Sentinel SAFE products from downloaded ZIP archives.
    """

    @staticmethod
    def extract(
        zip_path: str,
        output_directory: str,
    ) -> Path:

        zip_path = Path(zip_path)
        output_directory = Path(output_directory)

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        with zipfile.ZipFile(zip_path, "r") as archive:

            for member in archive.infolist():

                destination = output_directory / member.filename

                if member.is_dir():
                    destination.mkdir(
                        parents=True,
                        exist_ok=True,
                    )
                    continue

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                with archive.open(member) as source:
                    with open(destination, "wb") as target:
                        shutil.copyfileobj(source, target)

        safe_folders = list(
            output_directory.glob("*.SAFE")
        )

        if not safe_folders:
            raise RuntimeError(
                "SAFE folder not found after extraction."
            )

        return safe_folders[0]