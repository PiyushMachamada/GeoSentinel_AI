# Roadmap

## Current baseline

**Fact.** The repository already contains an end-to-end local prototype: satellite retrieval, multi-model analysis, rules/evidence, reporting, SQLite history, monitoring, and a dashboard.

## Recommended sequence

### 1. Stabilize runtime contracts

- Select one FastAPI entry point.
- Select one canonical database schema and migration mechanism.
- Resolve the `OutputManager`/semantic-mask path mismatch.
- Define a versioned analysis-result schema and model-output contracts.

### 2. Make execution operable

- Introduce a persisted analysis-job lifecycle: queued, running, failed, complete.
- Move long-running inference/downloads off API workers.
- Add idempotency, stage-level retries, structured logs, and observable failure metadata.

### 3. Make data/model assumptions explicit

- Validate Sentinel band order, scaling, CRS/resolution, cloud handling, and date-pair selection.
- Define class-ontology mapping between Prithvi and Dynamic World before fusing coverage values.
- Calibrate and evaluate change/confidence scores on representative AOIs.

### 4. Harden the product boundary

- Replace hard-coded local URLs and model endpoints with configuration.
- Restrict artifact file serving and add authorization appropriate to the deployment.
- Separate credentials, model weights, generated artifacts, environments, and downloaded data from application source distribution.

### 5. Rationalize the repository

- Declare supported versus experimental model integrations.
- Add reproducible dependency manifests and model version metadata.
- Consolidate duplicated Sentinel/OSINT/database initialization paths.

These are recommendations, not statements that the work is currently scheduled.
