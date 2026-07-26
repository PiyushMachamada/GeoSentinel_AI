# GeoSentinel AI — Contributor Guide

## Repository intent

GeoSentinel AI is a local Earth-observation intelligence prototype. Its operational path is centred on `backend/models/geosentinel_pipeline.py`; the dashboard reads saved analysis results rather than executing analysis jobs.

## Working rules

- Preserve `backend/outputs/`, downloaded imagery, SQLite files, credentials, model weights, and environment directories unless a task explicitly authorizes changing them.
- Treat `ChangeFormer/`, `GeoSeg/`, `open-cd/`, `oem-lightweight/`, and `*_env/` as vendored/research or environment material. Do not make broad refactors there as part of application work.
- Make runtime changes in the canonical backend/frontend modules only after confirming the active import path. There are duplicate or legacy modules in this repository.
- Keep generated analysis artifacts out of source changes. Use `OutputManager` for new runtime artifacts.
- Do not add secrets to source control. Configuration currently uses local credentials and environment variables; document any new configuration requirement.

## Verification expectations

- For backend changes, inspect imports from `backend/main.py`, `backend/models/geosentinel_pipeline.py`, and `backend/monitoring/monitor.py` before declaring a path production-ready.
- For frontend changes, run the relevant Next.js lint/build check when dependencies are available.
- For schema changes, reconcile `database.py`, `init_db.py`, migrations, query code, and the existing SQLite database before modifying persistence.
- State whether a change affects manual pipeline execution, monitoring, dashboard reads, or only an experiment/test.

## Documentation

Maintain the files under `docs/` when architecture, models, data contracts, output paths, or operational assumptions change. Mark observations from the repository as **Fact** and future-state guidance as **Recommendation**.
