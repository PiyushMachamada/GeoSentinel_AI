import type { AnalysisTimelineEntry } from "@/types/timeline";

interface AnalysisTimelineTableProps {
  timeline: AnalysisTimelineEntry[];
  onSelectAnalysis?: (id: number) => void;
}

function getChangeStatus(change: number) {
  if (change < 10) {
    return {
      label: "Stable",
      color:
        "bg-green-100 text-green-700 border border-green-300",
    };
  }

  if (change < 30) {
    return {
      label: "Moderate",
      color:
        "bg-yellow-100 text-yellow-700 border border-yellow-300",
    };
  }

  return {
    label: "Significant",
    color:
      "bg-red-100 text-red-700 border border-red-300",
    };
}

export default function AnalysisTimelineTable({
  timeline,
  onSelectAnalysis,
}: AnalysisTimelineTableProps) {

  if (timeline.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center">

        <div className="text-5xl mb-4">
          📅
        </div>

        <h3 className="text-xl font-semibold text-slate-700">
          No Historical Analyses
        </h3>

        <p className="mt-2 text-slate-500">
          Historical missions will appear here once analyses have been completed.
        </p>

      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}

      <div className="border-b bg-slate-50 px-6 py-4">

        <h2 className="text-xl font-bold text-slate-800">
          Observation Timeline
        </h2>

        <p className="text-sm text-slate-500 mt-1">
          Select a previous mission to review historical results.
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="px-6 py-3 text-left text-sm font-semibold">
                Timestamp
              </th>

              <th className="px-6 py-3 text-left text-sm font-semibold">
                Analysis
              </th>

              <th className="px-6 py-3 text-left text-sm font-semibold">
                Change
              </th>

              <th className="px-6 py-3 text-left text-sm font-semibold">
                Confidence
              </th>

              <th className="px-6 py-3 text-left text-sm font-semibold">
                Status
              </th>

            </tr>

          </thead>

          <tbody>

            {timeline.map((entry) => {

              const status =
                getChangeStatus(
                  entry.change_percentage
                );

              return (

                <tr
                  key={entry.id}
                  onClick={() =>
                    onSelectAnalysis?.(
                      entry.id
                    )
                  }
                  className="
                    cursor-pointer
                    border-b
                    hover:bg-blue-50
                    transition-colors
                  "
                >

                  <td className="px-6 py-4 whitespace-nowrap">

                    {new Date(
                      entry.timestamp
                    ).toLocaleString(
                      "en-GB",
                      {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      }
                    )}

                  </td>

                  <td className="px-6 py-4 font-medium">

                    {entry.analysis_name}

                  </td>

                  <td className="px-6 py-4 font-semibold">

                    {entry.change_percentage.toFixed(2)}%

                  </td>

                  <td className="px-6 py-4 font-semibold">

                    {entry.confidence_score.toFixed(2)}%

                  </td>

                  <td className="px-6 py-4">

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${status.color}`}
                    >
                      {status.label}
                    </span>

                  </td>

                </tr>

              );

            })}

          </tbody>

        </table>

      </div>

    </div>
  );
}