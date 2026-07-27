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
        extraction_root = output_directory / zip_path.stem

        if extraction_root.exists():
            shutil.rmtree(extraction_root)

        extraction_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        with zipfile.ZipFile(zip_path, "r") as archive:

            for member in archive.infolist():

                destination = extraction_root / member.filename

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
            extraction_root.rglob("*.SAFE")
        )

        if not safe_folders:
            raise RuntimeError(
                "SAFE folder not found after extraction."
            )

        if len(safe_folders) > 1:
            safe_folders.sort()

        return safe_folders[0]