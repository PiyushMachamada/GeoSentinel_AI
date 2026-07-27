import type { AnalysisResult } from "@/types/analysis";

interface MissionSummaryProps {
  analysis: AnalysisResult | null;
}

function safeParse(value: string) {
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}

export default function MissionSummary({
  analysis,
}: MissionSummaryProps) {

  if (!analysis) return null;

  const fusion =
    typeof analysis.fusion_results === "string"
      ? safeParse(analysis.fusion_results)
      : analysis.fusion_results;

  const evidence =
    typeof analysis.evidence_results === "string"
      ? safeParse(analysis.evidence_results)
      : analysis.evidence_results;

  const cloud =
    fusion?.preprocessing?.cloud_fraction?.average ?? 0;
  const water =
    fusion?.preprocessing?.water_fraction?.average ?? 0;
  const agreement =
    fusion?.model_agreement_score ?? 0;
  const evidenceScore =
    fusion?.overall_evidence_score ??
    evidence?.evidence_score ??
    0;

  const change = analysis.change_percentage;

  const status =
    change > 30
      ? {
          text: "Significant Change",
          color: "text-red-600",
          bg: "bg-red-100",
          icon: "🔴",
        }
      : change > 10
      ? {
          text: "Moderate Change",
          color: "text-yellow-700",
          bg: "bg-yellow-100",
          icon: "🟡",
        }
      : {
          text: "Stable",
          color: "text-green-600",
          bg: "bg-green-100",
          icon: "🟢",
        };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}

      <div className="flex items-center justify-between px-6 py-5 bg-slate-900 text-white">

        <div>

          <h2 className="text-2xl font-bold">
            🛰 GeoSentinel Mission Summary
          </h2>

          <p className="text-sm text-slate-300 mt-1">
            Persistent Earth Observation Intelligence
          </p>

        </div>

        <div
          className={`px-4 py-2 rounded-full font-semibold ${status.bg} ${status.color}`}
        >
          {status.icon} {status.text}
        </div>

      </div>

      {/* Statistics */}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 p-6">

        <SummaryMetric
          title="Area of Interest"
          value={analysis.aoi_name}
          tooltip="Selected Area of Interest being analysed."
        />

        <SummaryMetric
          title="Mission Confidence"
          value={`${analysis.confidence_score.toFixed(2)}%`}
          tooltip="Overall confidence after model agreement, evidence reliability, cloud impact, water influence, and observation quality."
        />

        <SummaryMetric
          title="Change Detected"
          value={`${analysis.change_percentage.toFixed(2)}%`}
          tooltip="Combined mission change estimate across structural and pixel-level change evidence."
        />

        <SummaryMetric
          title="Analysis Time"
          value={new Date(
            analysis.timestamp
          ).toLocaleString("en-GB")}
          tooltip="Timestamp of the current analysis record."
        />

        <SummaryMetric
          title="Cloud Cover"
          value={`${cloud.toFixed(2)}%`}
          tooltip="Average cloud contamination estimated during preprocessing and excluded from structural scoring."
        />

        <SummaryMetric
          title="Water Influence"
          value={`${water.toFixed(2)}%`}
          tooltip="Average water coverage estimated during preprocessing and down-weighted in structural change calculations."
        />

        <SummaryMetric
          title="Model Agreement"
          value={`${agreement.toFixed(2)}%`}
          tooltip="Cross-model agreement after comparing Prithvi, Dynamic World, ChangeStar, SSIM, and object evidence."
        />

        <SummaryMetric
          title="Evidence Score"
          value={`${evidenceScore.toFixed(2)}%`}
          tooltip="Weighted evidence score combining agreement, reliability, segmentation confidence, detections, and observation quality."
        />

      </div>

    </div>
  );
}

function SummaryMetric({
  title,
  value,
  tooltip,
}: {
  title: string;
  value: string;
  tooltip?: string;
}) {
  return (
    <div
      className="rounded-xl border border-slate-200 bg-slate-50 p-5"
      title={tooltip}
    >

      <div className="text-xs uppercase tracking-wide text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-lg font-semibold text-slate-800 break-words">
        {value}
      </div>

    </div>
  );
}