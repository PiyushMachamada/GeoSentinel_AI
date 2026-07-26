from pathlib import Path
from datetime import datetime


class OutputManager:
    """
    GeoSentinel AI Output Manager

    Creates and manages the output directory for a single
    AOI analysis.

    Structure

    backend/
        outputs/
            AOI001/
                2026-07-20_11-35-20/
                    images/
                        before/
                        after/
                        prithvi/
                        changestar/
                        dynamic_world/
                        grounding_dino/
                        change_detection/
                    reports/
                    logs/
    """

    def __init__(self, aoi_id: str):

        self.aoi_id = aoi_id

        self.timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        self.analysis_dir = (
            Path("backend")
            / "outputs"
            / aoi_id
            / self.timestamp
        )

        self.images_dir = self.analysis_dir / "images"

        self.before_dir = self.images_dir / "before"
        self.after_dir = self.images_dir / "after"

        self.prithvi_dir = self.images_dir / "prithvi"

        self.changestar_dir = self.images_dir / "changestar"

        self.dynamic_world_dir = (
            self.images_dir / "dynamic_world"
        )

        self.grounding_dino_dir = (
            self.images_dir / "grounding_dino"
        )

        self.change_detection_dir = (
            self.images_dir / "change_detection"
        )

        self.reports_dir = (
            self.analysis_dir / "reports"
        )

        self.logs_dir = (
            self.analysis_dir / "logs"
        )

        self.yolo_dir = self.images_dir / "yolo"

        directories = [

            self.analysis_dir,

            self.images_dir,

            self.before_dir,
            self.after_dir,

            self.prithvi_dir,

            self.changestar_dir,

            self.dynamic_world_dir,

            self.grounding_dino_dir,

            self.change_detection_dir,

            self.reports_dir,

            self.logs_dir,

            self.yolo_dir,

        ]

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True
            )

    @property
    def directory(self):
        return self.analysis_dir

    def get_path(
        self,
        category: str,
        filename: str,
    ):

        mapping = {

            "before": self.before_dir,

            "after": self.after_dir,

            "prithvi": self.prithvi_dir,

            "changestar": self.changestar_dir,

            "dynamic_world": self.dynamic_world_dir,

            "grounding_dino": self.grounding_dino_dir,

            "change_detection": self.change_detection_dir,

            "reports": self.reports_dir,

            "logs": self.logs_dir,

            "yolo": self.yolo_dir,

        }

        if category not in mapping:
            raise ValueError(
                f"Unknown category: {category}"
            )

        return mapping[category] / filename

    def default_files(self):
        """
        Returns every standard output file used by GeoSentinel.
        """

        return {

            # -------------------------
            # Input imagery
            # -------------------------

            "before_image":
                self.get_path(
                    "before",
                    "before.tif",
                ),

            "after_image":
                self.get_path(
                    "after",
                    "after.tif",
                ),

            # -------------------------
            # Prithvi
            # -------------------------

            "prithvi_before":
                self.get_path(
                    "prithvi",
                    "prithvi_before.png",
                ),

            "prithvi_after":
                self.get_path(
                    "prithvi",
                    "prithvi_after.png",
                ),

            "segmask_before":
                self.get_path(
                    "prithvi",
                    "segmask_before.npy",
                ),

            "segmask_after":
                self.get_path(
                    "prithvi",
                    "segmask_after.npy",
                ),

            # -------------------------
            # ChangeStar
            # -------------------------

            "changestar_prediction":
                self.get_path(
                    "changestar",
                    "changestar_prediction.png",
                ),

            "changestar_probability":
                self.get_path(
                    "changestar",
                    "changestar_probability.npy",
                ),

            "changestar_json":
                self.get_path(
                    "changestar",
                    "changestar_result.json",
                ),

            # -------------------------
            # Dynamic World
            # -------------------------

            "dynamic_world_before":
                self.get_path(
                    "dynamic_world",
                    "before_dynamic_world.tif",
                ),

            "dynamic_world_after":
                self.get_path(
                    "dynamic_world",
                    "after_dynamic_world.tif",
                ),

            "dynamic_world_transition":
                self.get_path(
                    "dynamic_world",
                    "dynamic_world_transition_map.png",
                ),

            "dynamic_world_transition_json":
                self.get_path(
                    "dynamic_world",
                    "dynamic_world_transition_results.json",
                ),
            # -------------------------
            # Grounding DINO
            # -------------------------

            "grounding_dino_before":
                self.get_path(
                    "grounding_dino",
                    "before.png",
                ),

            "grounding_dino_after":
                self.get_path(
                    "grounding_dino",
                    "after.png",
                ),

                "grounding_dino_before_json":
                    self.get_path(
                        "grounding_dino",
                        "before.json",
                    ),

                "grounding_dino_after_json":
                    self.get_path(
                        "grounding_dino",
                        "after.json",
                    ),

            # -------------------------
            # SSIM
            # -------------------------

            "change_map":
                self.get_path(
                    "change_detection",
                    "change_map.jpg",
                ),

            "change_binary":
                self.get_path(
                    "change_detection",
                    "change_binary.jpg",
                ),

            # -------------------------
            # YOLO
            # -------------------------

            "yolo_before":
                self.get_path(
                    "yolo",
                    "before.png",
                ),

            "yolo_after":
                self.get_path(  
                    "yolo",
                    "after.png",
                ),

            # -------------------------
            # Reports
            # -------------------------

            "intelligence_report":
                self.get_path(
                    "reports",
                    "intelligence_report.txt",
                ),

            "qwen_prompt":
                self.get_path(
                    "reports",
                    "qwen_prompt.txt",
                ),

            "pipeline_log":
                self.get_path(
                    "logs",
                    "pipeline.log",
                ),
        }

    def metadata(self):

        return {

            "aoi_id": self.aoi_id,

            "timestamp": self.timestamp,

            "analysis_directory": str(self.analysis_dir),

            "images_directory": str(self.images_dir),

            "reports_directory": str(self.reports_dir),

            "logs_directory": str(self.logs_dir),

        }