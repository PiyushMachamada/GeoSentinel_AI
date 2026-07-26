# AI Models and Analytical Components

## Models used by the active pipeline

| Component | Implementation | Role in pipeline | Output |
|---|---|---|---|
| Grounding DINO | `backend/models/grounding_dino` using Transformers | Prompted object detection on before/after images; prompts depend on AOI type. | Detections, annotated images, JSON, count differences |
| Prithvi EO 2.0 | `PrithviModelV2`, Terratorch `terratorch_prithvi_eo_v2_300` + `FCNDecoder` | Seven-class segmentation on both dates. | Masks, overlays, per-class percentages |
| ChangeStar2 | `torchange.models.changen2.s9_init_s9c1_changestar_vitb_1x256` | Pairwise structural-change estimation. | Change mask/probability and percentage |
| Dynamic World V1 | Google Earth Engine collection `GOOGLE/DYNAMICWORLD/V1` | Independent land-cover source and temporal transition analysis. | Before/after label rasters and class changes |
| SSIM | `skimage.metrics.structural_similarity` | Conventional image-difference change signal. | Change map, binary map, changed percentage |
| Qwen 2.5 7B | Local Ollama HTTP generation | Converts supplied evidence into a structured intelligence report. | Text report and saved prompt |

## Rule-based analytical components

These are not trained models but materially influence results:

- `SemanticChangeEngine`: converts segmentation class-pair changes to named transitions and scene interpretations.
- `FusionEngine`: compares Prithvi/Dynamic World/ChangeStar/SSIM/object/OSINT evidence, identifies conflicts, and packages evidence.
- `EvidenceValidator`, `EvidenceReliabilityEngine`, and `MissionConfidenceEngine`: calculate heuristic validation, reliability, and confidence.
- `intelligence/`: mission-profile rules, historical context, and mission assessment.

## Input assumptions

**Fact.** The acquisition path exports Sentinel-2 B2/B3/B4/B8, but preprocessing produces normalized RGB PNGs. `PrithviModelV2` pads input with zero channels to meet its six-channel tensor shape. Model inputs are therefore not uniformly native multispectral inputs.

**Recommendation.** Validate each model's required bands, scaling, spatial resolution, and temporal assumptions against the exact preprocessing contract before treating confidence scores as calibrated.

## Present but not active in the main pipeline

| Area | Status inferred from imports |
|---|---|
| ChangeFormer | Wrapper, checkpoint, tile tools, and tests exist; not imported by `GeoSentinelPipeline`. |
| OpenCD | Inference/model wrappers exist; not imported by `GeoSentinelPipeline`. |
| SegFormer, Mask2Former | Standalone wrappers/tests; not imported by active pipeline. |
| OpenEarthMap/FasterSeg | Wrapper exists; not imported by active pipeline. |
| YOLO | Local detector/tests exist; not imported by active pipeline. |
| Older Prithvi and Dynamic World modules | Coexist with active versions; not imported by the active pipeline. |

## Report-generation guardrail

The Qwen system prompt instructs the model to use supplied evidence only, avoid inventing observations, acknowledge conflicts, and produce required report sections. This is a prompt-level control, not a cryptographic or programmatic guarantee.
