import type { AnalysisTimelineEntry } from "@/types/timeline";

export async function getAnalysisTimeline(
  aoiId: string
): Promise<AnalysisTimelineEntry[]> {

  const response = await fetch(
    `http://127.0.0.1:8000/dashboard/timeline/${aoiId}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch timeline");
  }

  return response.json();
}