export interface AnalysisResult {
  id: number;

  analysis_name: string;

  aoi_id: string;
  aoi_name: string;

  timestamp: string;

  confidence_score: number;
  change_percentage: number;

  objects_detected: string;

  prithvi_results: string;
  grounding_dino_results: string;

  dynamic_world_results: string;
  dynamic_world_transition_results: string;

  evidence_results: string;

  fusion_results: string;
  transition_results: string;
  geospatial_results: string;

  report: string;

  pipeline_version: string;
  execution_time: number;

  analysis_directory: string;

  before_image_path: string;
  after_image_path: string;

  prithvi_before_path: string;
  prithvi_after_path: string;

  segmask_before_path: string;
  segmask_after_path: string;

  changestar_result_path: string;

  dynamic_world_before_path: string;
  dynamic_world_after_path: string;
  dynamic_world_transition_map: string;

  grounding_dino_before_path: string;
  grounding_dino_after_path: string;

  change_map_path: string;
  change_binary_path: string;

  grounding_dino_diff_path: string;
  prithvi_change_map_path: string;
  changestar_probability_path: string;
  qwen_raw_output_path: string;
}