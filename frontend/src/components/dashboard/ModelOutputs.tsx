"use client";

import { useState } from "react";
import type { AnalysisResult } from "@/types/analysis";

const API_BASE =
  "http://127.0.0.1:8000/dashboard/file?path=";

interface Props {
  analysis: AnalysisResult | null;
}

function imageUrl(path?: string) {
  if (!path) return undefined;
  return `${API_BASE}${encodeURIComponent(path)}`;
}

function ImageCard({
  title,
  path,
  status,
}: {
  title: string;
  path?: string;
  /** Override: shown when path is missing */
  status?: string;
}) {
  const [errored, setErrored] = useState(false);
  const url = imageUrl(path);

  const unavailableMsg = status ?? "Not Available";

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden hover:shadow-md transition-shadow">

      <div className="border-b bg-slate-50 px-4 py-3">
        <h3 className="font-semibold text-slate-800">
          {title}
        </h3>
      </div>

      {url && !errored ? (
        <img
          src={url}
          alt={title}
          className="w-full object-contain bg-slate-100"
          onError={() => setErrored(true)}
        />
      ) : (
        <div className="h-48 flex flex-col items-center justify-center bg-slate-100 text-slate-500 gap-2 p-4">
          <span className="text-2xl">🛰</span>
          <span className="text-sm text-center font-medium">
            {errored ? "Image unavailable" : unavailableMsg}
          </span>
        </div>
      )}

    </div>
  );
}

function Section({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">

      <div>
        <h2 className="text-xl font-bold text-slate-800">
          {title}
        </h2>
        <p className="text-sm text-slate-500">
          {subtitle}
        </p>
      </div>

      {children}

    </section>
  );
}

/** Derive a path relative to analysis_directory using forward-slash segments. */
function derivedPath(analysisDir: string | undefined, ...segments: string[]) {
  if (!analysisDir) return undefined;
  // Support both backslash and forward-slash directory separators
  return `${analysisDir}\\${segments.join("\\")}`;
}

export default function ModelOutputs({
  analysis,
}: Props) {

  if (!analysis) return null;

  const dir = analysis.analysis_directory;

  return (
    <div className="space-y-10">

      <Section
        title="Original Imagery"
        subtitle="Satellite imagery used as input for the analysis."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Reference Image"
            path={analysis.before_image_path}
            status="Reference image not available"
          />

          <ImageCard
            title="Latest Image"
            path={analysis.after_image_path}
            status="Latest image not available"
          />

        </div>
      </Section>

      <Section
        title="Object Detection"
        subtitle="Grounding DINO detected objects and assets."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Reference Detection"
            path={analysis.grounding_dino_before_path}
            status="Object detection not available"
          />

          <ImageCard
            title="Latest Detection"
            path={analysis.grounding_dino_after_path}
            status="Object detection not available"
          />

        </div>
      </Section>

      <Section
        title="Land Cover Segmentation"
        subtitle="Prithvi EO semantic segmentation results."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Reference Segmentation"
            path={analysis.prithvi_before_path}
            status="Segmentation not available"
          />

          <ImageCard
            title="Latest Segmentation"
            path={analysis.prithvi_after_path}
            status="Segmentation not available"
          />

        </div>
      </Section>

      <Section
        title="Change Detection"
        subtitle="Temporal changes detected between the two observations."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Change Prediction"
            path={analysis.changestar_result_path}
            status="Change detection not available"
          />

          <ImageCard
            title="Binary Change Map"
            path={analysis.change_binary_path}
            status="Change map not available"
          />

        </div>
      </Section>

      <Section
        title="Dynamic World"
        subtitle="Official Google Dynamic World land-cover classification with colour legend."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Reference Classification"
            path={analysis.dynamic_world_before_path}
            status="Dynamic World not available for this analysis"
          />

          <ImageCard
            title="Latest Classification"
            path={analysis.dynamic_world_after_path}
            status="Dynamic World not available for this analysis"
          />

        </div>
      </Section>

      <Section
        title="Quality & Evidence Maps"
        subtitle="Cloud mask, model-agreement, and uncertainty products derived during analysis."
      >
        <div className="grid md:grid-cols-3 gap-5">

          <ImageCard
            title="Cloud Mask (After)"
            path={derivedPath(dir, "images", "after", "cloud_mask.png")}
            status="Cloud mask not generated"
          />

          <ImageCard
            title="Agreement Map"
            path={derivedPath(dir, "images", "change_detection", "agreement_map.png")}
            status="Agreement map not generated"
          />

          <ImageCard
            title="Uncertainty Map"
            path={derivedPath(dir, "images", "change_detection", "uncertainty_map.png")}
            status="Uncertainty map not generated"
          />

        </div>
      </Section>

    </div>
  );
}
