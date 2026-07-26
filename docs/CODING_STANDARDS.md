# Coding Standards

## Scope

This document records maintenance standards for future changes. It does not claim every existing module follows them.

## Source boundaries

- Treat `backend/models/geosentinel_pipeline.py`, `backend/main.py`, `backend/monitoring`, `backend/database`, `backend/services`, `intelligence`, and `frontend/src` as the application boundary.
- Treat experiments, root-level check scripts, test scripts, model wrappers not imported by the pipeline, in-tree research repositories, environment directories, downloads, and generated outputs as non-production unless a change explicitly promotes them.

## Python

- Use `pathlib.Path` for filesystem contracts and pass paths as parameters instead of using repository-relative literals.
- Keep model adapters responsible for inference and serialization; keep pipeline orchestration responsible for stage order.
- Use typed, JSON-serializable result contracts at pipeline boundaries.
- Do not print secrets, raw credentials, or unbounded model input/output data.
- Use structured logging for runtime paths; reserve `print` for one-off tools/tests.
- Keep external-service initialization and network calls injectable where practical.

## Frontend

- Keep API base URLs in environment configuration, not component/service literals.
- Keep TypeScript types aligned with actual dashboard API responses.
- Handle loading, empty, and API-error states for each dashboard view.

## Persistence and outputs

- Use `OutputManager` for production artifacts; do not write to global `backend/outputs` filenames.
- When changing storage, update schema, migrations, persistence, queries, API response expectations, and documentation together.
- Never hard-code paths under `datasets/` in new production code.

## Documentation convention

- Label present behavior as **Fact**.
- Label desired or suggested behavior as **Recommendation**.
- Update model, pipeline, output, database, and dashboard documents with behavior changes.
