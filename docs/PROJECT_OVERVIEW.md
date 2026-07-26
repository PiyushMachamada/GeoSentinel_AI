# GeoSentinel AI: Project Overview

## Purpose

**Fact.** GeoSentinel AI is a local multimodal Earth-observation intelligence application. It compares satellite observations for predefined areas of interest (AOIs), combines visual, land-cover, change, and open-source evidence, produces an intelligence report, and exposes historical results through a dashboard.

## Runtime at a glance

```text
Sentinel / Dynamic World / OSINT / local input imagery
                         |
                 GeoSentinelPipeline
                         |
     model outputs -> fusion -> confidence -> Qwen report
                         |
          SQLite analysis record + timestamped artifacts
                         |
            FastAPI dashboard API <- Next.js dashboard
```

**Fact.** The primary implementation is a Python backend with a Next.js frontend. It is designed for local execution: API URLs, CORS origins, Ollama, Earth Engine, filesystem output paths, and SQLite are local-machine oriented.

## Major repository directories

| Directory | Role | Classification |
|---|---|---|
| `backend/` | FastAPI, pipeline, model adapters, acquisition, monitoring, persistence, tests, and generated output. | Active application plus legacy utilities |
| `frontend/` | Next.js/React dashboard and client-side API services. | Active dashboard |
| `intelligence/` | Rule-based evidence, profiles, mission assessment, historical/temporal intelligence. | Active pipeline dependency |
| `datasets/`, `satellite_data/` | Local sample, monitoring, and satellite data. | Data/state |
| `backend/outputs/` | Per-analysis images, masks, reports, and logs. | Generated state |
| `backend/downloads/`, `backend/temp_extract/` | Copernicus Sentinel product archives/extractions. | Generated/cache state |
| `backend/database/` | SQLite schema, save/query code, migrations, and local database. | Active persistence, with competing schema definitions |
| `experiments/` | Model investigations and one-off scripts. | Experimental |
| `ChangeFormer/`, `GeoSeg/`, `open-cd/`, `oem-lightweight/` | Model/research codebases or dependencies retained in-tree. | Vendored/research |
| `ai_models/` | Model assets or local model-related material. | Model asset area |
| `*_env/` | Local Python environments. | Machine-local; not application source |
| `credentials/` | Earth Engine service-account material. | Sensitive local configuration |

Directories named `New folder*`, root-level demos/checks, and many model-specific scripts do not form part of the identified production pipeline.

## Application entry points

| Entry point | Observed role |
|---|---|
| `backend/main.py` | Full FastAPI app: status, satellite, change, dashboard, AOI routers; serves `backend/outputs`. |
| `main.py` | Reduced second FastAPI app: dashboard only; serves outputs and datasets. |
| `backend/models/geosentinel_pipeline.py` | Primary analysis orchestration, callable through `run_pipeline`. |
| `backend/monitoring/run_monitor.py` | Starts recurring monitoring using configured interval. |
| `backend/automation/automation_manager.py` | Batch/manual orchestration helper. |

## Classification of code

### Production-path modules

The current production path is inferred from imports in `GeoSentinelPipeline`, `backend/main.py`, and monitoring modules. It includes AOI management, Sentinel/Dynamic World acquisition, preprocessing, Grounding DINO, Prithvi v2, ChangeStar, SSIM change detection, fusion/evidence/confidence, OSINT, Qwen reporting, output management, and SQLite persistence.

### Legacy, experimental, or unintegrated modules

**Fact.** Wrappers for ChangeFormer, OpenCD, SegFormer, Mask2Former, OpenEarthMap/FasterSeg, YOLO, older Prithvi code, standalone Dynamic World scripts, debug scripts, and experiments exist but are not imported by `GeoSentinelPipeline`.

**Recommendation.** Maintain a small manifest of supported models and move unintegrated scripts to an explicitly archival location only through a separately approved cleanup effort.
