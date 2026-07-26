import type { AnalysisResult } from "@/types/analysis";

interface MissionSummaryProps {
  analysis: AnalysisResult | null;
}

export default function MissionSummary({
  analysis,
}: MissionSummaryProps) {

  if (!analysis) return null;

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
        />

        <SummaryMetric
          title="Mission Confidence"
          value={`${analysis.confidence_score.toFixed(2)}%`}
        />

        <SummaryMetric
          title="Change Detected"
          value={`${analysis.change_percentage.toFixed(2)}%`}
        />

        <SummaryMetric
          title="Analysis Time"
          value={new Date(
            analysis.timestamp
          ).toLocaleString("en-GB")}
        />

      </div>

    </div>
  );
}

function SummaryMetric({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

      <div className="text-xs uppercase tracking-wide text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-lg font-semibold text-slate-800 break-words">
        {value}
      </div>

    </div>
  );
}