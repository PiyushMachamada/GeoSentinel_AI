"use client";

interface ReportViewerProps {
  report?: string;
}

const sectionIcons: Record<string, string> = {
  "Executive Summary": "🧠",
  "Situation Overview": "🌍",
  "Land Cover Analysis": "🌿",
  "Land Cover Assessment": "🌿",
  "Change Detection": "🔥",
  "Change Assessment": "🔥",
  "Confidence Assessment": "📊",
  "Mission Assessment": "🎯",
  "Threat Assessment": "⚠️",
  "OSINT Findings": "📰",
  "Recommendations": "💡",
  "Conclusion": "✅",
};

export default function ReportViewer({
  report,
}: ReportViewerProps) {
  if (!report) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm p-12 text-center">
        <div className="text-6xl mb-4">📄</div>

        <h3 className="text-xl font-semibold text-slate-700">
          No Intelligence Report Available
        </h3>

        <p className="mt-3 text-slate-500">
          Run a GeoSentinel mission to generate an AI intelligence report.
        </p>
      </div>
    );
  }

  // TypeScript now knows this is definitely a string.
  const reportText = report;

  const sections = reportText
    .split(/\n(?=[A-Z][A-Za-z ()/-]+:)/g)
    .filter((s) => s.trim().length > 0);

  async function copyReport() {
    try {
      await navigator.clipboard.writeText(reportText);
    } catch (error) {
      console.error("Failed to copy report:", error);
    }
  }

  function downloadReport() {
    const blob = new Blob([reportText], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "GeoSentinel_Intelligence_Report.txt";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="sticky top-0 z-10 rounded-2xl bg-slate-900 text-white p-6 shadow">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-2xl font-bold">
              🛰 GeoSentinel AI Intelligence Report
            </h2>

            <p className="mt-1 text-sm text-slate-300">
              AI-generated Earth Observation Intelligence
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={copyReport}
              className="rounded-lg bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
            >
              📋 Copy
            </button>

            <button
              onClick={downloadReport}
              className="rounded-lg bg-green-600 px-4 py-2 text-white transition-colors hover:bg-green-700"
            >
              ⬇ Download
            </button>
          </div>
        </div>
      </div>

      {/* Report Sections */}
      <div className="space-y-5 max-h-[700px] overflow-y-auto pr-2">
        {sections.map((section, index) => {
          const lines = section.trim().split("\n");

          const rawTitle = lines[0].replace(":", "").trim();

          const icon = sectionIcons[rawTitle] ?? "📌";

          const content = lines.slice(1).join("\n");

          return (
            <div
              key={index}
              className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
            >
              {/* Section Header */}
              <div className="flex items-center gap-3 border-b bg-slate-50 px-6 py-4">
                <div className="text-2xl">{icon}</div>

                <h3 className="text-lg font-semibold text-slate-800">
                  {rawTitle}
                </h3>
              </div>

              {/* Section Content */}
              <div className="px-6 py-5">
                <pre className="whitespace-pre-wrap break-words font-sans text-[15px] leading-7 text-slate-700">
                  {content}
                </pre>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}