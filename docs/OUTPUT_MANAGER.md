# Output Manager

## Purpose

`backend/utils/output_manager.py` defines `OutputManager`, the active convention for analysis artifacts. Creating it with an AOI ID creates a timestamped directory tree.

```text
backend/outputs/<AOI_ID>/<YYYY-MM-DD_HH-MM-SS>/
├─ images/
│  ├─ before/                 before.tif / before.png
│  ├─ after/                  after.tif / after.png
│  ├─ prithvi/                overlays and NumPy masks
│  ├─ changestar/             prediction/probability/result JSON
│  ├─ dynamic_world/          label rasters and transition outputs
│  ├─ grounding_dino/         annotated images and detection JSON
│  ├─ change_detection/       SSIM visualizations
│  └─ yolo/                   reserved YOLO paths
├─ reports/                   Qwen report and prompt
└─ logs/                      reserved pipeline log path
```

## Contract

`default_files()` returns a mapping consumed by the pipeline. Important keys include:

| Group | Keys |
|---|---|
| Inputs | `before_image`, `after_image` |
| Prithvi | `prithvi_before`, `prithvi_after`, `segmask_before`, `segmask_after` |
| ChangeStar | `changestar_prediction`, `changestar_probability`, `changestar_json` |
| Dynamic World | `dynamic_world_before`, `dynamic_world_after`, `dynamic_world_transition`, `dynamic_world_transition_json` |
| Grounding DINO | before/after annotations and JSON keys |
| SSIM | `change_map`, `change_binary` |
| Reports | `intelligence_report`, `qwen_prompt`, `pipeline_log` |

## Design implications

- Each run has isolated artifacts, which supports dashboard history and avoids filename collisions.
- SQLite stores the run directory and individual artifact paths, linking database history to filesystem files.
- The manager creates directories in its constructor; it is not a pure path formatter.

## Known contract violations

**Fact.** `SemanticChangeEngine` reads fixed masks from `backend/outputs/segmask_before.npy` and `backend/outputs/segmask_after.npy`, while `OutputManager` writes masks inside the per-run `images/prithvi/` directory. This bypasses the run-scoped artifact contract.

**Recommendation.** Pass the relevant `OutputManager` paths into every stage and prohibit direct output-path literals in production modules.
