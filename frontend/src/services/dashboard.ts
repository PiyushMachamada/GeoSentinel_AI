const API_BASE_URL = "http://127.0.0.1:8000";

export async function getLatestAnalysis(aoiId: string) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/latest/${aoiId}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch latest analysis.");
  }

  return response.json();
}

export async function getAnalysisHistory(aoiId: string) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/history/${aoiId}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analysis history.");
  }

  return response.json();
}

export async function getAnalysisTimeline(aoiId: string) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/timeline/${aoiId}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analysis timeline.");
  }

  return response.json();
}

export async function getAnalysisById(
  analysisId: number
) {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/analysis/${analysisId}`,
    { cache: "no-store" }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch analysis.");
  }

  return response.json();
}