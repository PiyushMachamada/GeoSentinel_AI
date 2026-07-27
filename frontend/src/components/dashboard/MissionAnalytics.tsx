"use client";

import type { AnalysisResult } from "@/types/analysis";

interface Props {
  analysis: AnalysisResult | null;
}

function safeParse(value: string) {
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}

export default function MissionAnalytics({
  analysis,
}: Props) {
  const fusion =
    analysis && typeof analysis.fusion_results === "string"
      ? safeParse(analysis.fusion_results)
      : null;

  const confidenceBreakdown =
    fusion?.confidence_breakdown ?? {};

  const metrics = [
    {
      title: "Mission Confidence",
      value:
        analysis?.confidence_score != null
          ? `${analysis.confidence_score.toFixed(1)}%`
          : "--",
      color: "text-green-600",
      bg: "bg-green-50",
      icon: "🎯",
      tooltip:
        "Final mission confidence derived from agreement, reliability, image quality, cloud, water, and uncertainty.",
    },
    {
      title: "Change Detected",
      value:
        analysis?.change_percentage != null
          ? `${analysis.change_percentage.toFixed(2)}%`
          : "--",
      color: "text-red-600",
      bg: "bg-red-50",
      icon: "🔥",
      tooltip:
        "Combined mission change estimate, not just raw pixel difference.",
    },
    {
      title: "Model Agreement",
      value:
        fusion?.model_agreement_score != null
          ? `${fusion.model_agreement_score.toFixed(2)}%`
          : "--",
      color: "text-blue-600",
      bg: "bg-blue-50",
      icon: "🤝",
      tooltip:
        "Agreement across Prithvi, Dynamic World, ChangeStar, SSIM, and object evidence.",
    },
    {
      title: "Uncertainty",
      value:
        confidenceBreakdown.segmentation_confidence != null
          ? `${(100 - confidenceBreakdown.segmentation_confidence).toFixed(2)}%`
          : "--",
      color: "text-amber-600",
      bg: "bg-amber-50",
      icon: "🌫️",
      tooltip:
        "Higher values indicate less certainty in land-cover segmentation and downstream structural interpretation.",
    },
    {
      title: "Evidence Score",
      value:
        fusion?.overall_evidence_score != null
          ? `${fusion.overall_evidence_score.toFixed(2)}%`
          : "--",
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      icon: "📚",
      tooltip:
        "Weighted evidence fusion score across models and observation quality.",
    },
    {
      title: "Cloud Impact",
      value:
        confidenceBreakdown.cloud_percentage != null
          ? `${confidenceBreakdown.cloud_percentage.toFixed(2)}%`
          : "--",
      color: "text-slate-600",
      bg: "bg-slate-50",
      icon: "☁️",
      tooltip:
        "Estimated cloud coverage masked out before structural scoring.",
    },
    {
      title: "Water Impact",
      value:
        confidenceBreakdown.water_percentage != null
          ? `${confidenceBreakdown.water_percentage.toFixed(2)}%`
          : "--",
      color: "text-cyan-600",
      bg: "bg-cyan-50",
      icon: "🌊",
      tooltip:
        "Estimated water coverage suppressed for structural change calculations.",
    },
    {
      title: "Execution Time",
      value:
        analysis?.execution_time != null
          ? `${analysis.execution_time.toFixed(2)} s`
          : "--",
      color: "text-purple-600",
      bg: "bg-purple-50",
      icon: "⏱",
      tooltip:
        "End-to-end processing time for the stored analysis.",
    },
  ];

  return (
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-5">

      {metrics.map((metric) => (

        <div
          key={metric.title}
          title={metric.tooltip}
          className="
            rounded-2xl
            border
            border-slate-200
            bg-white
            shadow-sm
            hover:shadow-md
            transition-shadow
            duration-200
            overflow-hidden
          "
        >

          <div className={`${metric.bg} p-5`}>

            <div className="text-4xl">
              {metric.icon}
            </div>

          </div>

          <div className="p-5">

            <div className="text-xs uppercase tracking-wide text-slate-500">
              {metric.title}
            </div>

            <div
              className={`mt-2 text-3xl font-bold ${metric.color}`}
            >
              {metric.value}
            </div>

          </div>

        </div>

      ))}

    </div>
  );
}