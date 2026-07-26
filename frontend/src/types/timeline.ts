export interface AnalysisTimelineEntry {
  id: number;

  analysis_name: string;

  aoi_id: string;

  aoi_name: string;

  timestamp: string;

  change_percentage: number;

  confidence_score: number;
}