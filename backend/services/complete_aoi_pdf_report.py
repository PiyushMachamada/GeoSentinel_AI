from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "reportlab is required. Install with: pip install reportlab"
    ) from exc


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "backend" / "outputs" / "GeoSentinel_AI_Complete_AOI_Report.pdf"
DB_PATH = ROOT / "backend" / "database" / "geosentinel.db"
OUTPUTS_DIR = ROOT / "backend" / "outputs"
CONFIGURED_AOIS = [
    {
        "id": "AOI001",
        "name": "Kempegowda International Airport",
        "latitude": 13.1986,
        "longitude": 77.7066,
        "radius_km": 5,
    },
    {
        "id": "AOI002",
        "name": "Jawaharlal Nehru Port (JNPT)",
        "latitude": 18.9497,
        "longitude": 72.9523,
        "radius_km": 8,
    },
    {
        "id": "AOI003",
        "name": "Strait of Hormuz",
        "latitude": 26.5667,
        "longitude": 56.2500,
        "radius_km": 25,
    },
    {
        "id": "AOI004",
        "name": "Amazon Rainforest",
        "latitude": -3.4653,
        "longitude": -62.2159,
        "radius_km": 25,
    },
    {
        "id": "AOI005",
        "name": "Bengaluru Urban Expansion",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "radius_km": 15,
    },
]


@dataclass
class AOIReportContext:
    aoi_id: str
    aoi_name: str
    latitude: float
    longitude: float
    radius_km: float
    analysis_timestamp: str = "Unavailable"
    imagery_dates: dict[str, str] = field(default_factory=lambda: {"before": "Unavailable", "after": "Unavailable"})
    analysis_dir: Path | None = None
    db_row: dict[str, Any] | None = None
    missing_evidence: list[str] = field(default_factory=list)
    llm_outputs: dict[str, Any] = field(default_factory=dict)


class PDFBuilder:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name="Small", parent=self.styles["Normal"], fontSize=8, leading=11))
        self.styles.add(ParagraphStyle(name="Tiny", parent=self.styles["Normal"], fontSize=7, leading=9))
        self.styles.add(ParagraphStyle(name="AOIHeading", parent=self.styles["Heading1"], fontSize=18, spaceAfter=10, textColor=colors.HexColor("#0A2E5D")))
        self.story: list[Any] = []

    def build(self):
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title="GeoSentinel AI Complete AOI Report",
            author="GeoSentinel AI",
        )

        def add_page_number(canvas, document):
            canvas.saveState()
            canvas.setFont("Helvetica", 9)
            canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Page {document.page}")
            canvas.restoreState()

        doc.build(self.story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    def add_cover(self):
        self.story.append(Spacer(1, 3 * cm))
        self.story.append(Paragraph("GeoSentinel AI", self.styles["Title"]))
        self.story.append(Spacer(1, 0.2 * cm))
        self.story.append(Paragraph("Complete Multi-AOI Evidence & LLM Intelligence Report", self.styles["Heading2"]))
        self.story.append(Spacer(1, 0.6 * cm))
        self.story.append(
            Paragraph(
                "Purpose: Consolidate all available stored evidence and LLM outputs for AOI001–AOI005 using existing database records and saved outputs only.",
                self.styles["BodyText"],
            )
        )
        self.story.append(Spacer(1, 0.4 * cm))
        self.story.append(
            Paragraph(
                "Qwen 2.5 7B — only LLM currently integrated in GeoSentinel AI.",
                self.styles["BodyText"],
            )
        )
        self.story.append(Spacer(1, 0.4 * cm))
        self.story.append(Paragraph(f"Generated: {datetime.utcnow().isoformat()}Z", self.styles["BodyText"]))
        self.story.append(PageBreak())

    def add_aoi_section(self, ctx: AOIReportContext):
        self.story.append(Paragraph(f"{ctx.aoi_id} — {ctx.aoi_name}", self.styles["AOIHeading"]))

        info_data = [
            ["AOI", ctx.aoi_id],
            ["Name", ctx.aoi_name],
            ["Coordinates", f"{ctx.latitude:.4f}, {ctx.longitude:.4f}"],
            ["Radius", f"{ctx.radius_km} km"],
            ["Analysis Timestamp", ctx.analysis_timestamp],
            ["Imagery Date (Before)", ctx.imagery_dates.get("before", "Unavailable")],
            ["Imagery Date (After)", ctx.imagery_dates.get("after", "Unavailable")],
        ]
        self._add_table(info_data)

        self._add_model_images_title("Original Imagery")
        self._add_image_pair(
            "Satellite BEFORE (Original)",
            "Satellite AFTER (Original)",
            _artifact_path(ctx, "before_image_path", fallback_rel="images/before/before.png"),
            _artifact_path(ctx, "after_image_path", fallback_rel="images/after/after.png"),
            ctx,
        )

        self._add_model_images_title("Grounding DINO Evidence")
        self._add_image_pair(
            "Grounding DINO BEFORE",
            "Grounding DINO AFTER",
            _artifact_path(ctx, "grounding_dino_before_path", fallback_rel="images/grounding_dino/before.png"),
            _artifact_path(ctx, "grounding_dino_after_path", fallback_rel="images/grounding_dino/after.png"),
            ctx,
        )
        self._add_single_image(
            "Grounding DINO Object-Change Visualization (Diff Map)",
            _artifact_path(ctx, "grounding_dino_diff_path", fallback_rel="images/grounding_dino/diff_map.png"),
            ctx,
        )

        self._add_model_images_title("Prithvi EO Evidence")
        self._add_image_pair(
            "Prithvi BEFORE Segmentation",
            "Prithvi AFTER Segmentation",
            _artifact_path(ctx, "prithvi_before_path", fallback_rel="images/prithvi/prithvi_before.png"),
            _artifact_path(ctx, "prithvi_after_path", fallback_rel="images/prithvi/prithvi_after.png"),
            ctx,
        )
        self._add_single_image(
            "Prithvi Semantic Change Map",
            _artifact_path(ctx, "prithvi_change_map_path", fallback_rel="images/prithvi/semantic_change_map.png"),
            ctx,
        )

        self._add_model_images_title("ChangeStar2 Evidence")
        self._add_single_image(
            "ChangeStar2 Change Map",
            _artifact_path(ctx, "changestar_result_path", fallback_rel="images/changestar/changestar_prediction.png"),
            ctx,
        )
        self._add_single_image(
            "ChangeStar2 Probability Map",
            _artifact_path(ctx, "changestar_probability_path", fallback_rel="images/changestar/changestar_probability_map.png"),
            ctx,
        )

        self._add_model_images_title("Dynamic World Evidence")
        self._add_image_pair(
            "Dynamic World BEFORE",
            "Dynamic World AFTER",
            _artifact_path(ctx, "dynamic_world_before_path", fallback_rel="images/dynamic_world/before_dynamic_world.png"),
            _artifact_path(ctx, "dynamic_world_after_path", fallback_rel="images/dynamic_world/after_dynamic_world.png"),
            ctx,
        )
        self._add_single_image(
            "Dynamic World Transition / Change Map",
            _artifact_path(ctx, "dynamic_world_transition_map", fallback_rel="images/dynamic_world/dynamic_world_transition_map.png"),
            ctx,
        )

        self._add_model_images_title("SSIM / Pixel-Level Change Evidence")
        self._add_image_pair(
            "SSIM Change Map",
            "Binary Change Map",
            _artifact_path(ctx, "change_map_path", fallback_rel="images/change_detection/change_map.jpg"),
            _artifact_path(ctx, "change_binary_path", fallback_rel="images/change_detection/change_binary.jpg"),
            ctx,
        )

        self.story.append(Paragraph("Metrics", self.styles["Heading3"]))
        metrics_table = _build_metrics_table(ctx)
        self._add_table(metrics_table)

        self.story.append(Paragraph("LLM Outputs", self.styles["Heading3"]))
        self.story.append(Paragraph("Qwen 2.5 7B — only LLM currently integrated in GeoSentinel AI.", self.styles["BodyText"]))

        self._add_llm_section(ctx)

        self.story.append(Paragraph("Intelligence Summary", self.styles["Heading3"]))
        cleaned = ctx.llm_outputs.get("cleaned_intelligence_report") or "Unavailable"
        self.story.append(Preformatted(cleaned, self.styles["Small"]))

        if ctx.missing_evidence:
            self.story.append(Paragraph("Unavailable Evidence", self.styles["Heading3"]))
            for item in sorted(set(ctx.missing_evidence)):
                self.story.append(Paragraph(f"• {item}", self.styles["BodyText"]))

        self.story.append(PageBreak())

    def add_comparative_summary(self, contexts: list[AOIReportContext]):
        self.story.append(Paragraph("Final Comparative Summary", self.styles["Heading1"]))
        rows = [["AOI", "Analysis Timestamp", "Change %", "Confidence %", "Model Agreement", "LLM"]]
        for ctx in contexts:
            rows.append([
                ctx.aoi_id,
                ctx.analysis_timestamp,
                _metric_value(ctx, ["change_percentage"], "Unavailable"),
                _metric_value(ctx, ["confidence_score"], "Unavailable"),
                _metric_value(ctx, ["model_agreement_score", "model_agreement"], "Unavailable"),
                "Qwen 2.5 7B",
            ])
        self._add_table(rows)
        self.story.append(Paragraph("Comparison uses only stored records and artifacts currently available on disk.", self.styles["BodyText"]))

    def _add_model_images_title(self, title: str):
        self.story.append(Paragraph(title, self.styles["Heading2"]))

    def _add_image_pair(self, left_title: str, right_title: str, left_path: Path | None, right_path: Path | None, ctx: AOIReportContext):
        self.story.append(Paragraph(f"{left_title} | {right_title}", self.styles["Small"]))
        left = _build_image_flowable(left_path, ctx)
        right = _build_image_flowable(right_path, ctx)
        table = Table([[left, right]], colWidths=[8.8 * cm, 8.8 * cm])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * cm))

    def _add_single_image(self, title: str, image_path: Path | None, ctx: AOIReportContext):
        self.story.append(Paragraph(title, self.styles["Small"]))
        item = _build_image_flowable(image_path, ctx, width=17.6 * cm, height=9.5 * cm)
        table = Table([[item]], colWidths=[17.6 * cm])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * cm))

    def _add_table(self, rows: list[list[str]]):
        col_width = 17.6 * cm / len(rows[0])
        table = Table(rows, colWidths=[col_width for _ in rows[0]])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF6")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#102A43")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2 * cm))

    def _add_llm_section(self, ctx: AOIReportContext):
        model_info = ctx.llm_outputs.get("qwen_model_info")
        prompt_text = ctx.llm_outputs.get("qwen_prompt") or "Unavailable"
        raw_text = ctx.llm_outputs.get("qwen_raw_output") or "Unavailable"
        discovered_files = ctx.llm_outputs.get("discovered_llm_files") or []

        self.story.append(Paragraph("LLM Label: Qwen 2.5 7B (Ollama)", self.styles["BodyText"]))
        if discovered_files:
            self.story.append(Paragraph("LLM-related artifacts discovered:", self.styles["BodyText"]))
            for path in discovered_files:
                self.story.append(Paragraph(f"• {path}", self.styles["Small"]))
        else:
            self.story.append(Paragraph("No LLM artifacts found on disk.", self.styles["BodyText"]))

        if isinstance(model_info, dict):
            info_rows = [["Field", "Value"]]
            for k in ["llm", "model_name", "ollama_url", "attempt", "generation_time_seconds"]:
                info_rows.append([k, str(model_info.get(k, "Unavailable"))])
            options = model_info.get("options")
            if options is not None:
                info_rows.append(["options", json.dumps(options)])
            self._add_table(info_rows)
        else:
            self.story.append(Paragraph("Model metadata: Unavailable", self.styles["BodyText"]))

        self.story.append(Paragraph("Prompt / Context Used (if available)", self.styles["Heading4"]))
        self.story.append(Preformatted(prompt_text, self.styles["Tiny"]))

        self.story.append(Paragraph("Raw Verbatim Output", self.styles["Heading4"]))
        self.story.append(Preformatted(raw_text, self.styles["Tiny"]))

        self.story.append(Paragraph("Final Cleaned Intelligence Report", self.styles["Heading4"]))


def _build_image_flowable(path: Path | None, ctx: AOIReportContext, width: float = 8.6 * cm, height: float = 6.0 * cm):
    if path is None:
        return Paragraph("Unavailable", getSampleStyleSheet()["BodyText"])

    if not _is_valid_artifact_path(path, ctx.aoi_id):
        ctx.missing_evidence.append(f"Path verification failed: {path}")
        return Paragraph("Unavailable (AOI path mismatch)", getSampleStyleSheet()["BodyText"])

    if not path.exists() or path.stat().st_size == 0:
        ctx.missing_evidence.append(path.name)
        return Paragraph("Unavailable", getSampleStyleSheet()["BodyText"])

    try:
        img = Image(str(path), width=width, height=height)
        return img
    except Exception:
        ctx.missing_evidence.append(path.name)
        return Paragraph("Unavailable", getSampleStyleSheet()["BodyText"])


def _is_valid_artifact_path(path: Path, aoi_id: str) -> bool:
    normalized = str(path).replace("\\", "/")
    return f"/{aoi_id}/" in normalized or normalized.endswith(f"/{aoi_id}")


def _parse_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _read_text(path: Path | None) -> str | None:
    if not path or not path.exists() or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _read_json(path: Path | None) -> dict[str, Any] | None:
    text = _read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def _artifact_path(ctx: AOIReportContext, db_field: str, fallback_rel: str) -> Path | None:
    if ctx.db_row:
        value = ctx.db_row.get(db_field)
        if value:
            p = Path(str(value))
            if not p.is_absolute():
                p = ROOT / str(value)
            return p
    if ctx.analysis_dir:
        return ctx.analysis_dir / fallback_rel
    return None


def _find_latest_analysis_dir(aoi_id: str) -> Path | None:
    base = OUTPUTS_DIR / aoi_id
    if not base.exists():
        return None
    dirs = [d for d in base.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.name, reverse=True)[0]


def _fetch_latest_db_row(aoi_id: str) -> dict[str, Any] | None:
    if not DB_PATH.exists():
        return None

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT *
            FROM analysis_results
            WHERE aoi_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (aoi_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    except sqlite3.DatabaseError:
        return None
    finally:
        conn.close()


def _extract_imagery_dates(ctx: AOIReportContext) -> dict[str, str]:
    result = {"before": "Unavailable", "after": "Unavailable"}

    metadata_path = None
    if ctx.analysis_dir:
        metadata_path = ctx.analysis_dir / "reports" / "preprocessing_metadata.json"

    metadata = _read_json(metadata_path)
    if not isinstance(metadata, dict):
        return result

    for side in ["before", "after"]:
        meta = metadata.get(f"{side}_metadata", {})
        candidate_keys = ["acquisition_date", "date", "timestamp", "datetime"]
        found = None
        if isinstance(meta, dict):
            for key in candidate_keys:
                if key in meta and meta[key]:
                    found = str(meta[key])
                    break
            if found is None:
                found = _first_date_like(meta)
        if found:
            result[side] = found

    return result


def _first_date_like(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for _, value in obj.items():
            out = _first_date_like(value)
            if out:
                return out
    elif isinstance(obj, list):
        for value in obj:
            out = _first_date_like(value)
            if out:
                return out
    elif isinstance(obj, str):
        if any(t in obj for t in ["20", "-", "T", ":"]) and len(obj) >= 8:
            return obj
    return None


def _collect_llm_outputs(ctx: AOIReportContext):
    reports_dir = ctx.analysis_dir / "reports" if ctx.analysis_dir else None
    qwen_prompt = _read_text(reports_dir / "qwen_prompt.txt") if reports_dir else None
    qwen_raw_output = _read_text(reports_dir / "qwen_raw_output.txt") if reports_dir else None
    qwen_model_info = _read_json(reports_dir / "qwen_model_info.json") if reports_dir else None
    cleaned = _read_text(reports_dir / "intelligence_report.txt") if reports_dir else None

    if cleaned is None and ctx.db_row:
        cleaned = ctx.db_row.get("report")

    discovered = []
    if reports_dir and reports_dir.exists():
        for file_path in sorted(reports_dir.iterdir()):
            if not file_path.is_file():
                continue
            lower = file_path.name.lower()
            if any(key in lower for key in [\"qwen\", \"llm\", \"intelligence_report\"]):
                discovered.append(str(file_path))

    ctx.llm_outputs = {
        "qwen_prompt": qwen_prompt,
        "qwen_raw_output": qwen_raw_output,
        "qwen_model_info": qwen_model_info,
        "cleaned_intelligence_report": cleaned,
        "discovered_llm_files": discovered,
    }


def _metric_value(ctx: AOIReportContext, keys: list[str], default: str) -> str:
    sources = []
    if ctx.db_row:
        sources.append(ctx.db_row)
    if ctx.analysis_dir:
        report_json = _read_json(ctx.analysis_dir / "reports" / "fusion_results.json")
        if isinstance(report_json, dict):
            sources.append(report_json)

    for source in sources:
        for key in keys:
            if key in source and source[key] is not None:
                val = source[key]
                if isinstance(val, float):
                    return f"{val:.2f}"
                return str(val)
    return default


def _build_metrics_table(ctx: AOIReportContext) -> list[list[str]]:
    row = ctx.db_row or {}
    fusion = _parse_json(row.get("fusion_results"))
    geospatial = _parse_json(row.get("geospatial_results"))
    transition = _parse_json(row.get("transition_results"))
    dw_transition = _parse_json(row.get("dynamic_world_transition_results"))

    def getv(*containers_and_keys):
        for container, key in containers_and_keys:
            if isinstance(container, dict) and key in container and container[key] is not None:
                value = container[key]
                if isinstance(value, float):
                    return f"{value:.4f}"
                return str(value)
        return "Unavailable"

    return [
        ["Metric", "Value"],
        ["Overall Change Percentage", getv((row, "change_percentage"), (fusion, "change_percentage"))],
        ["Mission Confidence Score", getv((row, "confidence_score"), (fusion, "confidence_score"), (fusion, "mission_confidence"))],
        ["Model Agreement Score", getv((fusion, "model_agreement_score"), (fusion, "model_agreement"))],
        ["Evidence Score", getv((fusion, "overall_evidence_score"), (fusion, "evidence_score"))],
        ["SSIM Score", getv((geospatial, "ssim_score"), (geospatial, "ssim"), (transition, "ssim_score"))],
        ["Pixel Change Percentage", getv((geospatial, "pixel_change_percentage"), (transition, "pixel_change_percentage"))],
        ["ChangeStar Relevant Metric", getv((transition, "changestar_change_percentage"), (transition, "changestar_confidence"), (fusion, "changestar"))],
        ["Dynamic World Transition Count", getv((dw_transition, "transition_count"), (dw_transition, "total_transitions"), (dw_transition, "num_transitions"))],
    ]


def build_contexts() -> list[AOIReportContext]:
    contexts: list[AOIReportContext] = []

    for aoi in CONFIGURED_AOIS:
        ctx = AOIReportContext(
            aoi_id=aoi["id"],
            aoi_name=aoi["name"],
            latitude=aoi["latitude"],
            longitude=aoi["longitude"],
            radius_km=aoi["radius_km"],
        )

        db_row = _fetch_latest_db_row(aoi["id"])
        ctx.db_row = db_row

        analysis_dir = None
        if db_row and db_row.get("analysis_directory"):
            p = Path(str(db_row["analysis_directory"]))
            analysis_dir = p if p.is_absolute() else ROOT / str(p)
        if analysis_dir is None or not analysis_dir.exists():
            analysis_dir = _find_latest_analysis_dir(aoi["id"])

        ctx.analysis_dir = analysis_dir

        if db_row and db_row.get("timestamp"):
            ctx.analysis_timestamp = str(db_row["timestamp"])
        elif analysis_dir:
            ctx.analysis_timestamp = analysis_dir.name

        ctx.imagery_dates = _extract_imagery_dates(ctx)
        _collect_llm_outputs(ctx)

        contexts.append(ctx)

    return contexts


def generate_complete_aoi_pdf(output_path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    contexts = build_contexts()

    builder = PDFBuilder(output_path)
    builder.add_cover()
    for ctx in contexts:
        builder.add_aoi_section(ctx)
    builder.add_comparative_summary(contexts)
    builder.build()

    summary = {
        "pdf_path": str(output_path),
        "aois_included": [f"{c.aoi_id} — {c.aoi_name}" for c in contexts],
        "llm_outputs_included": {
            c.aoi_id: {
                "qwen_prompt": bool(c.llm_outputs.get("qwen_prompt")),
                "qwen_raw_output": bool(c.llm_outputs.get("qwen_raw_output")),
                "qwen_model_info": bool(c.llm_outputs.get("qwen_model_info")),
                "cleaned_intelligence_report": bool(c.llm_outputs.get("cleaned_intelligence_report")),
            }
            for c in contexts
        },
        "unavailable_evidence": {
            c.aoi_id: sorted(set(c.missing_evidence)) for c in contexts if c.missing_evidence
        },
    }

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate complete GeoSentinel AOI PDF report.")
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="Absolute or relative output PDF path.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    summary = generate_complete_aoi_pdf(output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
