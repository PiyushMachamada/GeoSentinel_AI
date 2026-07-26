# Production Pipeline

## Canonical orchestrator

**Fact.** `backend/models/geosentinel_pipeline.py` defines `GeoSentinelPipeline` and `run_pipeline`. This is the repository's primary end-to-end execution path.

```text
AOI + before/after inputs
        |
OutputManager + database initialization
        |
Sentinel download if inputs absent
        |
GeoTIFF/product resolution and PNG preparation
        |
+---------------- Parallel-in-concept, sequential-in-code ----------------+
| Grounding DINO | Prithvi v2 | ChangeStar2 | Dynamic World | SSIM        |
+-------------------------------------------------------------------------+
        |
Semantic transitions + geospatial metadata + OSINT
        |
Reliability -> evidence validation -> fusion -> mission confidence
        |
Historical intelligence + mission assessment
        |
Qwen report -> SQLite record + output files -> dashboard reads
```

## Step-by-step data flow

1. `AOIManager` returns a predefined AOI with location, mission type, and before/after date windows.
2. `OutputManager(aoi_id)` creates a timestamped artifact directory and a canonical path map.
3. If imagery was not passed in, `backend.services.sentinel_service.SentinelService` composites Sentinel-2 SR Harmonized imagery from Earth Engine and exports four bands (B2, B3, B4, B8).
4. `prepare_geotiff_inputs` accepts local image files or Sentinel product IDs; GeoTIFFs are percentile-stretched and converted to PNGs for downstream computer-vision consumers.
5. Grounding DINO detects prompted objects in before and after images. Prithvi segments both images. ChangeStar estimates structural change. Dynamic World is separately exported and compared. SSIM produces a raster difference estimate.
6. Semantic, geospatial, OSINT, reliability, validation, and fusion modules assemble evidence.
7. `MissionConfidenceEngine` produces a score/level. Historical intelligence is loaded from prior analyses and mission assessment rules are applied.
8. `generate_qwen_report` sends a constructed prompt to local Ollama (`qwen2.5:7b` in the module) and saves prompt/report text.
9. `save_result` serializes selected results to SQLite and records paths to generated files.

## Monitoring path

`Scheduler` repeatedly calls `MonitoringService`, which asks `Monitor` to process each active in-memory AOI. `Monitor` uses `backend.services.sentinel.SentinelService` (a separate implementation from the pipeline's Earth Engine service), avoids a previously processed product ID, downloads a pair, records image history, invokes `run_pipeline`, then updates monitoring state.

## Failure behavior observed

- Model/download failures generally propagate from the pipeline; the automation and monitoring wrappers catch exceptions and log them.
- Qwen failures are handled locally and yield a fallback report string.
- There is no observed persisted job status, retry queue, or transaction spanning artifacts and SQLite.

## Recommendation

Keep the current sequence documented as the baseline, but make individual stages explicit jobs with typed input/output contracts before parallelizing or scaling it.
