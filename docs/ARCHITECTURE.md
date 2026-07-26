# Architecture

## Runtime architecture

```text
                 +------------------------------+
                 | Next.js frontend (port 3000)  |
                 | pages, viewers, map, timeline |
                 +---------------+--------------+
                                 | HTTP
                 +---------------v--------------+
                 | FastAPI (normally port 8000)  |
                 | dashboard / AOI read routes   |
                 +---------------+--------------+
                                 |
                  +--------------+--------------+
                  |                             |
        +---------v---------+         +---------v---------+
        | SQLite database   |         | backend/outputs/   |
        | analysis history  |         | imagery + reports  |
        +-------------------+         +-------------------+

Scheduled/manual execution is outside the API request path:

Monitor/Scheduler or caller -> GeoSentinelPipeline -> external services + models
```

## Backend responsibilities

| Package | Responsibility |
|---|---|
| `backend/api` | Read-oriented FastAPI routers. Dashboard exposes latest, history, timeline, analysis-by-ID, and files. AOI router reads AOIs from SQLite. |
| `backend/models` | Pipeline orchestration, imagery conversion, model adapters, evidence and fusion logic, report generation. |
| `backend/services` | Earth Engine and Copernicus/Sentinel discovery, download, extraction, and preprocessing. |
| `backend/monitoring` | AOI registry, polling, image history, scheduler, monitoring state. |
| `backend/database` | SQLite DDL, query functions, result persistence, migration/seed helpers. |
| `backend/utils` | `OutputManager` and pipeline-context support. |
| `backend/validation`, `backend/evaluation` | Supporting validation/metrics utilities; not invoked by the main pipeline. |

## Intelligence layer

`intelligence/` supplies the domain-level structures that make model output mission-specific: evidence collections, mission profiles, rules, fusion, timelines, historical intelligence, alerts, explainability, and knowledge definitions for airport, forest, and military contexts. The main pipeline directly uses `Evidence`, `EvidenceCollection`, `MissionAssessor`, `get_profile`, and `HistoricalIntelligence`.

## Frontend architecture

**Fact.** The dashboard is a client-side Next.js application. Its service modules call a hard-coded FastAPI base URL (`http://127.0.0.1:8000`). The home page loads the latest analysis or a selected historical analysis, then renders mission summaries, analytics, image viewer, model outputs, report, and timeline. Leaflet/react-leaflet support interactive maps.

## Key design decisions observed

- Analysis artifacts are filesystem-first and then referenced from SQLite, instead of being stored as blobs.
- The pipeline combines learned models with deterministic rules and a language-model report writer.
- Monitoring is pull-based polling; there is no observed queue, worker service, or API-managed job lifecycle.
- Output directories are per-AOI and per timestamp, enabling historical artifact retention.

## Recommendations

- Define a single canonical FastAPI entry point and a single Sentinel acquisition abstraction.
- Treat the pipeline as a background job with an explicit lifecycle before exposing write/trigger endpoints.
- Establish a module-status registry (active, supported optional, experimental, archived) to prevent accidental use of unused wrappers.
