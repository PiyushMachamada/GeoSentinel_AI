# Database

## Storage model

**Fact.** The active database helper resolves its SQLite file to `backend/database/geosentinel.db`. Results are stored as a wide `analysis_results` row: scalar fields, JSON-serialized result objects, report text, execution information, and filesystem paths for artifacts.

```text
analysis run
  ├─ backend/outputs/<AOI>/<timestamp>/...  (large artifacts)
  └─ analysis_results row                   (metadata, JSON, references)
```

## Main tables

| Table | Purpose |
|---|---|
| `aois` | AOI identity/location/configuration. |
| `monitoring_state` | Latest processed product and monitoring status. |
| `analysis_results` | Historical analysis records and artifact paths. |

`init_db.py` additionally defines `satellite_images`, `text_reports`, and `social_posts`; storage helpers reference those kinds of records.

## Access paths

- Pipeline: `create_database()` then `save_result(...)`.
- Dashboard APIs: `get_latest_analysis`, `get_analysis_history`, `get_analysis_timeline`, `get_analysis_by_id`.
- AOI router: raw query against `aois`.
- Monitoring: `MonitoringStateDB` and image history filesystem records.

## Schema inconsistency

**Fact.** `database.py:create_database()` and `init_db.py:create_tables()` define incompatible `aois` schemas. The former has a text `id` and no `mission_type`; the latter has numeric `id`, string `aoi_id`, and `mission_type`. The AOI API expects `aoi_id` and `mission_type`. `migrate_db.py` targets a separate relative `geosentinel.db` path.

This is a production-risk inconsistency, not merely documentation debt.

## Recommendations

- Designate one canonical schema creation/migration path and make all callers use it.
- Introduce versioned migrations and a schema version table.
- Keep artifact files in storage, but record a stable run identifier and validate referenced paths before serving them.
- Treat SQLite as appropriate for local/single-process use until concurrency requirements are defined.
