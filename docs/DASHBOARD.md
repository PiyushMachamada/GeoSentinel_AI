# Dashboard and API

## Frontend

**Fact.** `frontend/` is a Next.js 16, React 19, TypeScript application using Tailwind CSS and Leaflet/react-leaflet. The home page is the main analysis dashboard.

```text
AOI selection
  -> latest analysis or historical analysis selection
  -> mission summary + analytics
  -> before/after image viewer and layers
  -> model outputs + Qwen report
  -> analysis timeline
```

The frontend service modules fetch data from `http://127.0.0.1:8000`. Dashboard data is loaded client-side with `fetch`.

## API routes observed

| Route | Role |
|---|---|
| `GET /` | Basic API health message. |
| `GET /status/*` | Status router endpoints. |
| `GET /satellite/info` | Static Sentinel/Copernicus information. |
| `GET /change-detection/analyze` | Static placeholder response; does not run pipeline inference. |
| `GET /aois/` | Reads AOIs from SQLite. |
| `GET /dashboard/latest/{aoi_id}` | Latest persisted analysis. |
| `GET /dashboard/history/{aoi_id}` | All persisted analyses for AOI. |
| `GET /dashboard/timeline/{aoi_id}` | Lightweight historical timeline. |
| `GET /dashboard/analysis/{analysis_id}` | One persisted analysis. |
| `GET /dashboard/file?path=...` | Serves an existing path supplied by request. |
| `/outputs/...` | Static serving of `backend/outputs`. |

## Runtime relationship

The dashboard is a consumer of persisted output. No active API endpoint is identified that queues, launches, monitors, or cancels `GeoSentinelPipeline` analyses.

## Security and deployment observations

- The dashboard/API have no observed authentication or authorization.
- `/dashboard/file` accepts a caller-provided filesystem path and checks only existence; it is not restricted to the output root.
- CORS permits localhost frontend origins only.
- Frontend API base URLs are hard-coded for local development.

## Recommendations

- Add configuration-driven API endpoints and environment-specific CORS settings.
- Restrict file serving to resolved paths below the managed output directory.
- Add an authenticated analysis/job API only after job lifecycle and authorization requirements are designed.
