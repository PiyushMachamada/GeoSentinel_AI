"use client";

import { useState } from "react";

import type { AnalysisResult } from "@/types/analysis";

import ImageCanvas from "./ImageCanvas";
import ImagePlaceholder from "./ImagePlaceholder";
import ImageToolbar, { ViewerLayer } from "./ImageToolbar";
import LayerControls from "./LayerControls";

const API_BASE = "http://127.0.0.1:8000/dashboard/file?path=";

const titles: Record<ViewerLayer, string> = {
  before: "Before Image",
  after: "After Image",
  changestar: "ChangeStar Prediction",
  prithvi: "Prithvi Segmentation",
  dynamicworld: "Dynamic World",
  groundingdino: "Grounding DINO Detection",
};

interface ImageViewerProps {
  analysis: AnalysisResult | null;
}

export default function ImageViewer({
  analysis,
}: ImageViewerProps) {

  const [activeLayer, setActiveLayer] =
    useState<ViewerLayer>("before");

  const [layerVisible, setLayerVisible] =
    useState(true);

  const [layerOpacity, setLayerOpacity] =
    useState(100);

  const images: Partial<Record<ViewerLayer, string>> = {

    before:
      analysis?.before_image_path
        ? `${API_BASE}${encodeURIComponent(
            analysis.before_image_path
          )}`
        : undefined,

    after:
      analysis?.after_image_path
        ? `${API_BASE}${encodeURIComponent(
            analysis.after_image_path
          )}`
        : undefined,

    changestar:
      analysis?.changestar_result_path
        ? `${API_BASE}${encodeURIComponent(
            analysis.changestar_result_path
          )}`
        : undefined,

    prithvi:
      analysis?.prithvi_after_path
        ? `${API_BASE}${encodeURIComponent(
            analysis.prithvi_after_path
          )}`
        : undefined,

    dynamicworld:
      analysis?.dynamic_world_transition_map
        ? `${API_BASE}${encodeURIComponent(
            analysis.dynamic_world_transition_map
          )}`
        : undefined,

    groundingdino:
      analysis?.grounding_dino_before_path
        ? `${API_BASE}${encodeURIComponent(
            analysis.grounding_dino_before_path
          )}`
        : undefined,

  };

  console.log("Analysis:", analysis);
  console.log("Images:", images);

  const imageUrl = layerVisible
    ? images[activeLayer]
    : undefined;

  return (
    <div className="space-y-4">

      {/* Layer Selection */}
      <ImageToolbar
        activeLayer={activeLayer}
        onLayerChange={setActiveLayer}
      />

      {/* Viewer */}
      {imageUrl ? (
        <ImageCanvas
          imageUrl={imageUrl}
          title={titles[activeLayer]}
          model={titles[activeLayer]}
          aoi={analysis?.aoi_name}
          confidence={analysis?.confidence_score}
          change={analysis?.change_percentage}
          timestamp={analysis?.timestamp}
          opacity={layerOpacity}
        />
      ) : (
        <ImagePlaceholder />
      )}

      {/* Layer Controls */}
      <LayerControls
        visible={layerVisible}
        opacity={layerOpacity}
        onVisibleChange={setLayerVisible}
        onOpacityChange={setLayerOpacity}
      />

    </div>
  );
}