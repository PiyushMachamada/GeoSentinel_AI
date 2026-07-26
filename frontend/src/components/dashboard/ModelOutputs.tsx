"use client";

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
}: {
  title: string;
  path?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden hover:shadow-md transition-shadow">

      <div className="border-b bg-slate-50 px-4 py-3">

        <h3 className="font-semibold text-slate-800">
          {title}
        </h3>

      </div>

      {path ? (
        <img
          src={imageUrl(path)}
          alt={title}
          className="w-full object-contain bg-slate-100"
        />
      ) : (
        <div className="h-72 flex items-center justify-center bg-slate-100 text-slate-500">
          No Image Available
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

export default function ModelOutputs({
  analysis,
}: Props) {

  if (!analysis) return null;

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
          />

          <ImageCard
            title="Latest Image"
            path={analysis.after_image_path}
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
          />

          <ImageCard
            title="Latest Detection"
            path={analysis.grounding_dino_after_path}
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
          />

          <ImageCard
            title="Latest Segmentation"
            path={analysis.prithvi_after_path}
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
          />

          <ImageCard
            title="Binary Change Map"
            path={analysis.change_binary_path}
          />

        </div>
      </Section>

      <Section
        title="Dynamic World"
        subtitle="Land cover classification generated from Dynamic World."
      >
        <div className="grid md:grid-cols-2 gap-5">

          <ImageCard
            title="Reference Classification"
            path={analysis.dynamic_world_before_path}
          />

          <ImageCard
            title="Latest Classification"
            path={analysis.dynamic_world_after_path}
          />

        </div>
      </Section>

    </div>
  );
}