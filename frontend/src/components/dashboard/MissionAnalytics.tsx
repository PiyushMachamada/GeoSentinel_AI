"use client";

import type { AnalysisResult } from "@/types/analysis";

interface Props {
  analysis: AnalysisResult | null;
}

export default function MissionAnalytics({
  analysis,
}: Props) {

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
    },
    {
      title: "Execution Time",
      value:
        analysis?.execution_time != null
          ? `${analysis.execution_time.toFixed(2)} s`
          : "--",
      color: "text-blue-600",
      bg: "bg-blue-50",
      icon: "⏱",
    },
    {
      title: "Pipeline Version",
      value: analysis?.pipeline_version ?? "--",
      color: "text-purple-600",
      bg: "bg-purple-50",
      icon: "🛰",
    },
  ];

  return (
    <div className="grid grid-cols-2 xl:grid-cols-4 gap-5">

      {metrics.map((metric) => (

        <div
          key={metric.title}
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