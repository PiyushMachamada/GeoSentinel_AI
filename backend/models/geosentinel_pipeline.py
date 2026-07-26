import json
import time

from backend.database.database import create_database
from backend.database.save_results import save_result
from backend.services.sentinel_service import SentinelService

from backend.monitoring.aoi_manager import AOIManager

from backend.utils.output_manager import OutputManager

from backend.models.geotiff_preprocessing import prepare_geotiff_inputs
from backend.models.geospatial_analysis import analyze_geotiff
from backend.models.change_detection import run_change_detection

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
)

from backend.models.dynamic_world_transition_analysis import (
    analyze_dynamic_world_transitions,
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
    ):

        print("\nInitializing GeoSentinel AI")

        # ==================================================
        # Database
        # ==================================================

        create_database()

        # ==================================================
        # Output Manager
        # ==================================================

        self.output_manager = OutputManager(aoi_id)

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
            self.before_image,
            self.after_image,
        ) = prepare_geotiff_inputs(

            before_input=before_image,

            after_input=after_image,

            output_paths=self.paths,

        )

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

            aoi_type=self.aoi.mission_type,

        )
    # ==================================================
    # Prithvi EO 2
    # ==================================================

    def run_scene_understanding(self):

        print("\n[2/5] Running Prithvi EO 2")

        print("\nSegmenting BEFORE image...")

        before_stats = self.segmentation_model.segment(

            self.before_image,

            self.paths,

        )

        print("\nSegmenting AFTER image...")

        after_stats = self.segmentation_model.segment(

            self.after_image,

            self.paths,

        )

        comparison = {}

        all_classes = (

            set(before_stats.keys())

            |

            set(after_stats.keys())

        )

        for cls in sorted(all_classes):

            comparison[cls] = round(

                after_stats.get(cls, 0)

                -

                before_stats.get(cls, 0),

                2,

            )

        return {

            "before": before_stats,

            "after": after_stats,

            "comparison": comparison,

        }

    # ==================================================
    # ChangeStar2
    # ==================================================

    def run_changestar(self):

        print("\n[3/5] Running ChangeStar2")

        return self.changestar_model.predict(

            self.before_image,

            self.after_image,

            self.paths,

        )

    # ==================================================
    # SSIM
    # ==================================================

    def run_temporal_analysis(self):

        print("\n[5/5] Running SSIM Change Detection")

        return run_change_detection(

            before_image=self.before_image,

            after_image=self.after_image,

            output_paths=self.paths,

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

        for obj in grounding_dino_results.get(
            "detections",
            []
        ):

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

        semantic_results = self.semantic_engine.analyze()

        transition_results = semantic_results.get(
            "transitions",
            {},
        )

        # --------------------------------------------------
        # GeoTIFF Metadata
        # --------------------------------------------------

        geospatial_results = analyze_geotiff(
            self.after_image
        )

        # --------------------------------------------------
        # Dynamic World
        # --------------------------------------------------

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

        self.evidence.add(

            Evidence(

                source="Dynamic World",

                category="Land Cover",

                confidence=0.92,

                importance=0.8,

                description="Dynamic World classification.",

                metadata={

                    "dominant_class":
                        dominant,

                    "statistics":
                        dynamic_world_results

                }

            )

        )

        dynamic_world_transition_results = (
            analyze_dynamic_world_transitions(
                before_path=self.paths["dynamic_world_before"],
                after_path=self.paths["dynamic_world_after"],
                output_paths=self.paths,
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
            ssim_results,              # <-- ADD THIS
            grounding_dino_results,
            semantic_results,
            osint_results,
            reliability_results,
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
        print("Before :", self.before_image)
        print("After  :", self.after_image)

        for key, value in self.paths.items():
            print(f"{key}: {value}")

        print("=============================\n")

        print("SAVE:", self.before_image)
        print("SAVE:", self.after_image)

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

                before_image_path=self.before_image,
                after_image_path=self.after_image,

                prithvi_before_path=self.paths["prithvi_before"],
                prithvi_after_path=self.paths["prithvi_after"],

                segmask_before_path=self.paths["segmask_before"],
                segmask_after_path=self.paths["segmask_after"],

                changestar_result_path=self.paths["changestar_prediction"],

                dynamic_world_before_path=self.paths["dynamic_world_before"],
                dynamic_world_after_path=self.paths["dynamic_world_after"],
                dynamic_world_transition_map=self.paths["dynamic_world_transition"],

                grounding_dino_before_path=self.paths["grounding_dino_before"],
                grounding_dino_after_path=self.paths["grounding_dino_after"],

                change_map_path=self.paths["change_map"],
                change_binary_path=self.paths["change_binary"],

                execution_time=execution_time,

            )

            print("\nResults saved to database.")

        except Exception as e:

            print(f"\nDatabase Error : {e}")

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
):
    """
    Convenience wrapper for running the GeoSentinel pipeline.
    """

    pipeline = GeoSentinelPipeline(
        before_image=before_image,
        after_image=after_image,
        aoi_id=aoi_id,
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