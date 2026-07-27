import json
import time
from pathlib import Path

import cv2
import numpy as np

from backend.database.database import create_database
from backend.database.save_results import save_result
from backend.services.sentinel_service import SentinelService

from backend.monitoring.aoi_manager import AOIManager

from backend.utils.output_manager import OutputManager
from backend.utils.output_validation import validate_outputs
from backend.utils.research_outputs import generate_research_outputs

from backend.models.geotiff_preprocessing import prepare_geotiff_inputs
from backend.models.geospatial_analysis import analyze_geotiff
from backend.models.change_detection import run_change_detection
from backend.models.dynamic_world_colorizer import generate_dw_png_pair

from backend.models.grounding_dino.grounding_dino_engine import (
    GroundingDINOEngine,
)

from backend.models.prithvi.prithvi_model_v2 import (
    PrithviModelV2,
)

from intelligence.historical_intelligence import (
    HistoricalIntelligence,
)

from backend.models.changestar.changestar_model import (
    ChangeStarModel,
)

from backend.models.semantic_change_engine import (
    SemanticChangeEngine,
)

from backend.models.fusion_engine import FusionEngine

from backend.models.dynamic_world_service import (
    download_dynamic_world,
)

from backend.models.dynamic_world_temporal_analysis import (
    compare_dynamic_world,
    empty_dynamic_world_results,
)

from backend.models.dynamic_world_transition_analysis import (
    analyze_dynamic_world_transitions,
    empty_dynamic_world_transition_results,
)

from backend.models.osint.osint_engine import (
    OSINTEngine,
)

from backend.models.osint.osint_fusion import (
    OSINTFusion,
)

from backend.models.evidence_validator import (
    EvidenceValidator,
)

from backend.models.mission_confidence_engine import (
    MissionConfidenceEngine,
)

from backend.models.qwen_reasoning import (
    generate_qwen_report,
)

import backend.models.qwen_reasoning as qr

print("Qwen module:", qr.__file__)

from backend.models.evidence_reliability import (
    EvidenceReliabilityEngine,
)

from intelligence.evidence import Evidence
from intelligence.evidence import EvidenceCollection

from intelligence.mission_assessor import MissionAssessor
from intelligence.profiles import get_profile

class GeoSentinelPipeline:
    """
    Main orchestration pipeline for GeoSentinel AI.

    Pipeline:

    Grounding DINO
            ↓
    Prithvi EO 2
            ↓
    ChangeStar2
            ↓
    Semantic Change Analysis
            ↓
    Dynamic World
            ↓
    OSINT
            ↓
    Fusion
            ↓
    SSIM
            ↓
    Evidence Validation
            ↓
    Qwen Intelligence
            ↓
    SQLite Storage
    """

    def __init__(
        self,
        before_image=None,
        after_image=None,
        aoi_id="AOI001",
        output_manager=None,
    ):

        print("\nInitializing GeoSentinel AI")

        # ==================================================
        # Database
        # ==================================================

        create_database()

        # ==================================================
        # Output Manager
        # ==================================================

        if output_manager is None:
            self.output_manager = OutputManager(aoi_id)
        else:
            self.output_manager = output_manager

        self.paths = self.output_manager.default_files()

        self.output_paths = self.paths

        print("\nAnalysis Output Directory")

        print(self.output_manager.directory)

        # ==================================================
        # AOI
        # ==================================================

        self.aoi_manager = AOIManager()

        self.aoi = self.aoi_manager.get_by_id(aoi_id)

        if self.aoi is None:

            raise ValueError(
                f"Unknown AOI: {aoi_id}"
            )

        # ==========================================
        # Acquire Sentinel imagery
        # ==========================================

        if before_image is None or after_image is None:

            print("\nNo imagery supplied.")
            print("Downloading Sentinel imagery...")

            sentinel = SentinelService()

            imagery = sentinel.download(

                aoi=self.aoi,

                output_paths=self.paths,

            )

            before_image = imagery["before_path"]

            after_image = imagery["after_path"]


        (
            self.before_display_image,
            self.after_display_image,
            self.preprocessing_results,
        ) = prepare_geotiff_inputs(

            before_input=before_image,

            after_input=after_image,

            output_paths=self.paths,
            return_context=True,

        )

        self.before_image = self.preprocessing_results["before_model_input_path"]
        self.after_image = self.preprocessing_results["after_model_input_path"]
        self.before_source_image = self.preprocessing_results["before_source_path"]
        self.after_source_image = self.preprocessing_results["after_source_path"]

        self.aoi_id = self.aoi.id

        self.aoi_name = self.aoi.name

        print("=" * 60)
        print("PIPELINE INITIALIZATION")
        print("=" * 60)
        print(f"AOI ID   : {self.aoi_id}")
        print(f"AOI Name : {self.aoi_name}")
        print("=" * 60)

        # ==================================================
        # AI MODELS
        # ==================================================

        self.object_detector = GroundingDINOEngine()

        self.segmentation_model = PrithviModelV2()

        self.changestar_model = ChangeStarModel()

        self.semantic_engine = SemanticChangeEngine()

        self.fusion_engine = FusionEngine()

        self.osint_engine = OSINTEngine()

        self.osint_fusion = OSINTFusion()

        self.evidence_validator = EvidenceValidator()

        self.reliability_engine = EvidenceReliabilityEngine()

        self.confidence_engine = MissionConfidenceEngine()

        # ==================================================
        # Intelligence Layer
        # ==================================================

        self.evidence = EvidenceCollection()

        self.mission_assessor = MissionAssessor(
            get_profile(
                self.aoi.mission_type
            )
)

        # ==================================================
        # Historical Intelligence
        # ==================================================

        self.historical = HistoricalIntelligence()

        print("\nGeoSentinel Initialized Successfully.")

    # ==================================================
    # Grounding DINO
    # ==================================================

    def run_object_detection(self):

        print("\n[1/5] Running Grounding DINO")

        return self.object_detector.compare_images(

            before_image=self.before_image,

            after_image=self.after_image,

            before_output=self.paths[
                "grounding_dino_before"
            ],

            after_output=self.paths[
                "grounding_dino_after"
            ],

            before_json=self.paths[
                "grounding_dino_before_json"
            ],

            after_json=self.paths[
                "grounding_dino_after_json"
            ],

            statistics_output=self.paths[
                "grounding_dino_statistics_json"
            ],

            aoi_type=self.aoi.mission_type,

        )
    # ==================================================
    # Prithvi EO 2
    # ==================================================

    def run_scene_understanding(self):

        print("\n[2/5] Running Prithvi EO 2")

        print("\nSegmenting BEFORE image...")

        before_result = self.segmentation_model.segment(

            self.before_image,

            self.paths,

        )

        print("\nSegmenting AFTER image...")

        after_result = self.segmentation_model.segment(

            self.after_image,

            self.paths,

        )

        comparison = {}

        all_classes = (

            set(before_result["class_statistics"].keys())

            |

            set(after_result["class_statistics"].keys())

        )

        for cls in sorted(all_classes):

            comparison[cls] = round(

                after_result["class_statistics"].get(cls, 0)

                -

                before_result["class_statistics"].get(cls, 0),

                2,

            )

        return {

            "before": before_result["class_statistics"],

            "after": after_result["class_statistics"],

            "comparison": comparison,

            "confidence_summary": {
                "before_average_confidence": before_result["average_confidence"],
                "after_average_confidence": after_result["average_confidence"],
                "before_average_uncertainty": before_result["average_uncertainty"],
                "after_average_uncertainty": after_result["average_uncertainty"],
            },

        }

    # ==================================================
    # ChangeStar2
    # ==================================================

    def run_changestar(self):

        print("\n[3/5] Running ChangeStar2")

        before_cloud_mask = cv2.imread(
            str(self.preprocessing_results["before_cloud_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        after_cloud_mask = cv2.imread(
            str(self.preprocessing_results["after_cloud_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        before_water_mask = cv2.imread(
            str(self.preprocessing_results["before_water_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        after_water_mask = cv2.imread(
            str(self.preprocessing_results["after_water_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )

        combined_cloud_mask = None
        combined_water_mask = None

        if before_cloud_mask is not None and after_cloud_mask is not None:
            combined_cloud_mask = np.where(
                (before_cloud_mask > 0) | (after_cloud_mask > 0),
                255,
                0,
            ).astype(np.uint8)

        if before_water_mask is not None and after_water_mask is not None:
            combined_water_mask = np.where(
                (before_water_mask > 0) | (after_water_mask > 0),
                255,
                0,
            ).astype(np.uint8)

        return self.changestar_model.predict(

            self.before_image,

            self.after_image,

            self.paths,

            cloud_mask_path=combined_cloud_mask,
            water_mask_path=combined_water_mask,
            before_segmentation_path=self.paths["segmask_before"],
            after_segmentation_path=self.paths["segmask_after"],

        )

    # ==================================================
    # SSIM
    # ==================================================

    def run_temporal_analysis(self):

        print("\n[5/5] Running SSIM Change Detection")

        before_cloud_mask = cv2.imread(
            str(self.preprocessing_results["before_cloud_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        after_cloud_mask = cv2.imread(
            str(self.preprocessing_results["after_cloud_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        before_water_mask = cv2.imread(
            str(self.preprocessing_results["before_water_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        after_water_mask = cv2.imread(
            str(self.preprocessing_results["after_water_mask_path"]),
            cv2.IMREAD_GRAYSCALE,
        )
        ignore_mask = None

        cloud_mask = None
        water_mask = None

        if before_cloud_mask is not None and after_cloud_mask is not None:
            cloud_mask = np.where(
                (before_cloud_mask > 0) | (after_cloud_mask > 0),
                255,
                0,
            ).astype(np.uint8)

        if before_water_mask is not None and after_water_mask is not None:
            water_mask = np.where(
                (before_water_mask > 0) | (after_water_mask > 0),
                255,
                0,
            ).astype(np.uint8)

        if cloud_mask is not None and water_mask is not None:
            ignore_mask = np.where(
                (cloud_mask > 0) | (water_mask > 0),
                255,
                0,
            ).astype(np.uint8)
        elif cloud_mask is not None:
            ignore_mask = cloud_mask
        elif water_mask is not None:
            ignore_mask = water_mask

        return run_change_detection(

            before_image=self.before_image,

            after_image=self.after_image,

            output_paths=self.paths,

            ignore_mask=ignore_mask,

        )
        # ==================================================
    # MAIN PIPELINE
    # ==================================================

    def run(self):

        start_time = time.time()

        # --------------------------------------------------
        # Grounding DINO
        # --------------------------------------------------

        grounding_dino_results = self.run_object_detection()

        detections = []
        detections.extend(grounding_dino_results.get("before", []))
        detections.extend(grounding_dino_results.get("after", []))

        for obj in detections:

            self.evidence.add(

                Evidence(

                    source="Grounding DINO",

                    category="Object Detection",

                    confidence=obj.get(
                        "confidence",
                        0.5
                    ),

                    importance=0.8,

                    description=f"Detected {obj.get('label')}",

                    metadata=obj

                )

            )

        print("\n" + "=" * 70)
        print("GROUNDING DINO RESULTS")
        print("=" * 70)
        print(json.dumps(grounding_dino_results, indent=4))
        print("=" * 70)

        # --------------------------------------------------
        # Prithvi EO 2
        # --------------------------------------------------

        prithvi_results = self.run_scene_understanding()

        dominant = max(
            prithvi_results["after"],
            key=prithvi_results["after"].get
        )

        self.evidence.add(

            Evidence(

                source="Prithvi",

                category="Land Cover",

                confidence=0.95,

                importance=0.9,

                description="Dominant land cover.",

                metadata={

                    "dominant_class": dominant,

                    "statistics":
                        prithvi_results

                }

            )

        )

        # --------------------------------------------------
        # ChangeStar2
        # --------------------------------------------------

        changestar_results = self.run_changestar()

        self.evidence.add(

            Evidence(

                source="ChangeStar",

                category="Change Detection",

                confidence=min(

                    changestar_results[
                        "change_percentage"
                    ] / 100,

                    1.0

                ),

                importance=1.0,

                description="Structural change detected.",

                metadata=changestar_results

            )

        )

        # --------------------------------------------------
        # Semantic Change Analysis
        # --------------------------------------------------

        print("\nRunning Semantic Change Analysis")

        semantic_results = self.semantic_engine.analyze(
            self.paths
        )

        transition_results = semantic_results.get(
            "transitions",
            {},
        )

        # --------------------------------------------------
        # GeoTIFF Metadata
        # --------------------------------------------------

        geospatial_results = analyze_geotiff(
            self.after_source_image
        )

        # --------------------------------------------------
        # Dynamic World
        # --------------------------------------------------

        dynamic_world_results = empty_dynamic_world_results()
        dynamic_world_transition_results = (
            empty_dynamic_world_transition_results()
        )
        dynamic_world_before_path = None
        dynamic_world_after_path = None
        dynamic_world_transition_map = None
        dominant = None

        try:
            print("\n[4/5] Downloading Dynamic World")

            download_dynamic_world(
                aoi=self.aoi,
                output_paths=self.paths,
            )

            print("\n[4/5] Running Dynamic World Analysis")

            dynamic_world_results = compare_dynamic_world(
                before_path=self.paths["dynamic_world_before"],
                after_path=self.paths["dynamic_world_after"],
            )

            print("\nDynamic World Results")
            print("\n===== Dynamic World =====")
            print("Type:", type(dynamic_world_results))

            if isinstance(dynamic_world_results, dict):
                print("Keys:", list(dynamic_world_results.keys()))

                for key, value in dynamic_world_results.items():
                    print(f"{key}: {type(value)}")

                dominant = max(
                    dynamic_world_results,
                    key=lambda cls: dynamic_world_results[cls]["after"]
                )

            dynamic_world_transition_results = (
                analyze_dynamic_world_transitions(
                    before_path=self.paths["dynamic_world_before"],
                    after_path=self.paths["dynamic_world_after"],
                    output_paths=self.paths,
                )
            )

            # Generate browser-displayable colorized PNG versions
            print("\n[4/5] Generating Dynamic World colorized PNGs...")
            dw_pngs = generate_dw_png_pair(self.paths)

            # Store PNG paths in DB (browser-renderable) instead of raw TIF
            dynamic_world_before_path = (
                dw_pngs.get("before_png")
                or self.paths["dynamic_world_before"]
            )
            dynamic_world_after_path = (
                dw_pngs.get("after_png")
                or self.paths["dynamic_world_after"]
            )
            dynamic_world_transition_map = (
                self.paths["dynamic_world_transition"]
            )

        except Exception as exc:
            print(
                "\nDynamic World stage failed:"
                f" {exc}"
            )

        self.evidence.add(

            Evidence(

                source="Dynamic World",

                category="Land Cover",

                confidence=0.92 if dominant is not None else 0.0,

                importance=0.8,

                description="Dynamic World classification.",

                metadata={

                    "dominant_class":
                        dominant,

                    "statistics":
                        dynamic_world_results,

                    "transition_results":
                        dynamic_world_transition_results,

                }

            )

        )

        # --------------------------------------------------
        # Open Source Intelligence
        # --------------------------------------------------

        print("\nRunning Open Source Intelligence...")

        osint_results = self.osint_engine.collect(
            prithvi_results,
            dynamic_world_results,
            transition_results,
            geospatial_results,
        )

        osint_summary = self.osint_fusion.summarize(
            osint_results
        )

        # --------------------------------------------------
        # Evidence Reliability
        # --------------------------------------------------

        print("\nComputing Evidence Reliability")

        reliability_results = self.reliability_engine.compute(
            grounding_dino_results,
            prithvi_results,
            dynamic_world_results,
            changestar_results,
        )

        # --------------------------------------------------
        # SSIM Change Detection
        # --------------------------------------------------

        ssim_results = self.run_temporal_analysis()

        ssim_change = ssim_results["change_percentage"]

        changestar_change = 0

        if isinstance(changestar_results, dict):

            changestar_change = float(
                changestar_results.get(
                    "change_percentage",
                    0,
                )
            )

        change_percentage = round(
            (
                ssim_change
                + changestar_change
            ) / 2,
            2,
        )

        # --------------------------------------------------
        # Fusion Engine
        # --------------------------------------------------

        fusion_results = self.fusion_engine.fuse(
            prithvi_results,
            dynamic_world_results,
            changestar_results,
            ssim_results,
            grounding_dino_results,
            semantic_results,
            osint_results,
            reliability_results,
            output_paths=self.paths,
            preprocessing_results=self.preprocessing_results,
        )

        fusion_results["osint"] = osint_results

        evidence_results = (
            self.evidence_validator.validate(
                change_percentage=change_percentage,
                transition_results=transition_results,
                dynamic_world_results=dynamic_world_results,
                objects_detected=grounding_dino_results,
            )
        )

        print("\nEvidence Validation")
        print(
            json.dumps(
                evidence_results,
                indent=4,
            )
        )

        # --------------------------------------------------
        # Mission Confidence Calculation
        # --------------------------------------------------

        confidence = self.confidence_engine.compute(
            grounding_dino_results,
            prithvi_results,
            dynamic_world_results,
            changestar_results,
            fusion_results,
            evidence_results,
            reliability_results,
            preprocessing_results=self.preprocessing_results,
        )

        mission_confidence = confidence

        self.mission_assessor.clear()

        self.mission_assessor.add_many(
            self.evidence.evidence
        )

        # --------------------------------------------------
        # Historical Intelligence
        # --------------------------------------------------

        print("\nLoading Historical Intelligence...")

        self.historical.load_history(
            self.aoi_id
        )

        history = self.historical.summary()

        for item in history["temporal_evidence"]:

            self.evidence.add(

                Evidence(

                    source="Historical Intelligence",

                    category=item["category"],

                    confidence=0.90,

                    importance=0.90,

                    description=item["name"],

                    metadata=item

                )

            )

        print(json.dumps(history, indent=4, default=str))

        mission_assessment = (
            self.mission_assessor.assess()
        )

        print("\nMISSION ASSESSMENT")
        print("=" * 60)

        print(
            json.dumps(
                mission_assessment,
                indent=4
            )
        )

        print("\n" + "=" * 60)
        print("MISSION CONFIDENCE BREAKDOWN")
        print("=" * 60)

        for key, value in mission_confidence.breakdown.items():
            print(f"{key:<25}: {value}")

        print("-" * 60)
        print(f"Mission Confidence : {mission_confidence.score:.2f}%")
        print(f"Confidence Level   : {mission_confidence.level}")
        print(f"Reason             : {mission_confidence.reasoning}")

        print("=" * 60)

        # --------------------------------------------------
        # Qwen Intelligence Report
        # --------------------------------------------------

        intelligence_report = generate_qwen_report(
            prithvi_results,
            changestar_results,
            fusion_results,
            transition_results,
            geospatial_results,
            dynamic_world_results,
            dynamic_world_transition_results,
            osint_summary,
            mission_confidence=mission_confidence,
            reliability_results=reliability_results,
            mission_assessment=mission_assessment,
            historical_results=history,
            report_path=self.paths[
                "intelligence_report"
            ],
            prompt_path=self.paths[
                "qwen_prompt"
            ],
            aoi_context={
                "id": self.aoi_id,
                "name": self.aoi_name,
                "mission_type": self.aoi.mission_type,
            },
        )

        print("\n")
        print("=" * 70)
        print("GeoSentinel Intelligence Report")
        print("=" * 70)

        print(intelligence_report)

        # --------------------------------------------------
        # Execution Time
        # --------------------------------------------------

        execution_time = round(
            time.time() - start_time,
            2,
        )

        print(
            f"\nPipeline Execution Time : {execution_time} sec"
        )

            # --------------------------------------------------
        # Save Results
        # --------------------------------------------------

        print("\n========== PIPELINE SAVE ==========")
        print("AOI ID  :", self.aoi_id)
        print("AOI Name:", self.aoi_name)
        print("===================================")

        print("=" * 60)
        print("SAVING")
        print(f"AOI being saved: {self.aoi_id}")
        print("=" * 60)

        print("\n===== PATHS BEING SAVED =====")
        print("Before :", self.before_display_image)
        print("After  :", self.after_display_image)

        for key, value in self.paths.items():
            print(f"{key}: {value}")

        print("=============================\n")

        print("SAVE:", self.before_display_image)
        print("SAVE:", self.after_display_image)

        try:

            save_result(

                analysis_name="before_after_analysis",

                aoi_id=self.aoi_id,
                aoi_name=self.aoi_name,

                objects_detected=grounding_dino_results,

                confidence_score=mission_confidence.score,

                change_percentage=change_percentage,

                segformer_results=prithvi_results,

                dynamic_world_results=dynamic_world_results,
                dynamic_world_transition_results=dynamic_world_transition_results,

                fusion_results=fusion_results,

                transition_results=transition_results,

                geospatial_results=geospatial_results,

                evidence_results=evidence_results,

                historical_results=history,

                report=intelligence_report,

                analysis_directory=self.output_manager.directory,

                before_image_path=self.before_display_image,
                after_image_path=self.after_display_image,

                prithvi_before_path=self.paths["prithvi_before"],
                prithvi_after_path=self.paths["prithvi_after"],

                segmask_before_path=self.paths["segmask_before"],
                segmask_after_path=self.paths["segmask_after"],

                changestar_result_path=self.paths["changestar_prediction"],

                dynamic_world_before_path=dynamic_world_before_path,
                dynamic_world_after_path=dynamic_world_after_path,
                dynamic_world_transition_map=dynamic_world_transition_map,

                grounding_dino_before_path=self.paths["grounding_dino_before"],
                grounding_dino_after_path=self.paths["grounding_dino_after"],

                change_map_path=self.paths["change_map"],
                change_binary_path=self.paths["change_binary"],

                execution_time=execution_time,

            )

            print("\nResults saved to database.")

        except Exception as e:

            print(f"\nDatabase Error : {e}")
            raise

        # --------------------------------------------------
        # Research Outputs
        # --------------------------------------------------

        try:
            print("\n[Post] Generating research output files...")
            generate_research_outputs(
                output_paths=self.paths,
                aoi_id=self.aoi_id,
                aoi_name=self.aoi_name,
                pipeline_version="GeoSentinel AI v1.0",
                execution_time=execution_time,
                confidence_result=mission_confidence,
                fusion_results=fusion_results,
                prithvi_results=prithvi_results,
                changestar_results=changestar_results,
                dynamic_world_results=dynamic_world_results,
                grounding_dino_results=grounding_dino_results,
                evidence_results=evidence_results,
                reliability_results=reliability_results,
                historical_results=history,
                intelligence_report=intelligence_report,
                semantic_results=semantic_results,
                preprocessing_results=self.preprocessing_results,
            )
        except Exception as exc:
            print(f"\n[Post] Research output generation failed: {exc}")

        # --------------------------------------------------
        # Output Validation
        # --------------------------------------------------

        try:
            print("\n[Post] Validating output artifacts...")
            validation_report = validate_outputs(
                output_paths=self.paths,
                aoi_id=self.aoi_id,
                attempt_regeneration=True,
            )
            health = validation_report.get("health_percentage", 0)
            missing_req = validation_report.get("missing_required", [])
            print(
                f"[Post] Output health: {health:.1f}%"
                f" | Missing required: {missing_req}"
            )
        except Exception as exc:
            print(f"\n[Post] Output validation failed: {exc}")

        print("\nGeoSentinel AI Complete.")

        return {

            "grounding_dino": grounding_dino_results,

            "segmentation": prithvi_results,

            "changestar": changestar_results,

            "fusion": fusion_results,

            "transitions": transition_results,

            "dynamic_world": dynamic_world_results,

            "dynamic_world_transitions": dynamic_world_transition_results,

            "geospatial": geospatial_results,

            "mission_confidence": mission_confidence,

            "execution_time": execution_time,

            "evidence_results": evidence_results,

            "report": intelligence_report,

            "osint": osint_results,

            "mission_assessment": mission_assessment,

            "historical": history,

        }
    
    # ==========================================================
# Convenience Wrapper
# ==========================================================

def run_pipeline(
    before_image,
    after_image,
    aoi_id,
    output_manager=None,
):
    """
    Convenience wrapper for running the GeoSentinel pipeline.
    """

    pipeline = GeoSentinelPipeline(
        before_image=before_image,
        after_image=after_image,
        aoi_id=aoi_id,
        output_manager=output_manager,
    )

    return pipeline.run()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    TEST_AOI = "AOI001"

    pipeline = GeoSentinelPipeline(
        aoi_id=TEST_AOI,
    )

    results = pipeline.run()

    print("\n" + "=" * 70)
    print("GeoSentinel Pipeline Finished Successfully")
    print("=" * 70)

    print("\nReturned Results:")

    print(
        json.dumps(
            {
                "mission_confidence": results["mission_confidence"].score,
                "execution_time": results["execution_time"],    
            },
            indent=4,
        )
    )