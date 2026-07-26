# Known Issues and Technical Debt

This list records observations from repository code. It does not assert that every issue has been reproduced in a live deployment.

## High priority

1. **Competing SQLite schemas.** `database.py` and `init_db.py` define incompatible AOI table shapes, while the AOI API expects columns not created by `database.py`.
2. **Run-scoped output violation.** Semantic change reads fixed global mask paths instead of masks in the active `OutputManager` run directory.
3. **No-change semantic path risk.** The semantic engine constructs result fields from variables that are only assigned when changed pixels exist.
4. **Arbitrary path file endpoint.** Dashboard file delivery accepts a supplied path without limiting it to a managed root.

## Architecture

5. **Two FastAPI applications.** Root `main.py` and `backend/main.py` expose different router/static-file sets.
6. **Two Sentinel service approaches.** The pipeline uses `sentinel_service.py` with Earth Engine, while monitoring imports `sentinel.py`, which also incorporates product ingestion/authentication behavior.
7. **AOI split-brain.** Runtime pipeline/monitoring AOIs are hard-coded in `AOIManager`; frontend/API AOIs are queried from SQLite.
8. **Configuration drift.** `backend/config.py` exposes Qwen settings, but `qwen_reasoning.py` hard-codes its own Ollama URL and model.
9. **Synchronous heavyweight work.** Downloads, inference, OSINT, report generation, and database writes run sequentially without a worker queue.

## Data and ML

10. **Potential model-input mismatch.** Multispectral Sentinel imagery is converted to normalized RGB for CV consumers, while Prithvi v2 receives zero-padded channels.
11. **Ontology mismatch.** Prithvi and Dynamic World class sets differ; fusion compares them without an explicit harmonization contract.
12. **Heuristic confidence.** Reliability, fusion, validation, and mission confidence are rule/weight driven; no calibration/evaluation artefact is identified in the active path.
13. **Inconsistent temporal modes.** The pipeline uses date-window median composites; monitoring obtains product pairs. These produce different temporal semantics.

## Repository hygiene

14. **Machine-local state in tree.** Databases, downloaded imagery, extracted products, outputs, environments, model weights, and credentials are present alongside source.
15. **Hard-coded data paths.** Root scripts, experiments, and some supporting modules reference `datasets/...` directly.
16. **Unclassified model code.** Multiple wrappers and in-tree model repositories are present with no single support-status manifest.
