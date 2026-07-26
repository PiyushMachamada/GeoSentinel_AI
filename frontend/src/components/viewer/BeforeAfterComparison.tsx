"use client";

import { useState } from "react";
import {
  TransformWrapper,
  TransformComponent,
} from "react-zoom-pan-pinch";

interface BeforeAfterComparisonProps {
  beforeImage: string;
  afterImage: string;
}

export default function BeforeAfterComparison({
  beforeImage,
  afterImage,
}: BeforeAfterComparisonProps) {
  const [fullscreen, setFullscreen] = useState(false);

  return (
    <div
      className={`rounded-xl border bg-white shadow-lg overflow-hidden ${
        fullscreen
          ? "fixed inset-0 z-50 m-4"
          : ""
      }`}
    >
      {/* Header */}

      <div className="flex items-center justify-between bg-slate-900 text-white px-5 py-3">

        <div>
          <h2 className="font-bold text-lg">
            Before / After Comparison
          </h2>

          <p className="text-xs text-slate-300">
            Visual comparison of satellite imagery
          </p>
        </div>

        <button
          onClick={() =>
            setFullscreen(!fullscreen)
          }
          className="rounded-lg bg-blue-600 px-4 py-2 hover:bg-blue-700"
        >
          {fullscreen
            ? "Exit Fullscreen"
            : "Fullscreen"}
        </button>

      </div>

      {/* Images */}

      <div className="grid grid-cols-1 xl:grid-cols-2">

        {/* BEFORE */}

        <ComparisonPanel
          title="🛰 Before Image"
          image={beforeImage}
          borderRight
        />

        {/* AFTER */}

        <ComparisonPanel
          title="🛰 After Image"
          image={afterImage}
        />

      </div>

    </div>
  );
}

interface ComparisonPanelProps {
  title: string;
  image: string;
  borderRight?: boolean;
}

function ComparisonPanel({
  title,
  image,
  borderRight = false,
}: ComparisonPanelProps) {
  return (
    <div
      className={`${
        borderRight
          ? "xl:border-r border-slate-300"
          : ""
      }`}
    >
      <div className="bg-slate-100 px-4 py-3 border-b">

        <h3 className="font-semibold">
          {title}
        </h3>

      </div>

      <TransformWrapper
        initialScale={1}
        minScale={0.5}
        maxScale={8}
      >
        {({
          zoomIn,
          zoomOut,
          resetTransform,
        }) => (
          <>
            {/* Toolbar */}

            <div className="flex justify-center gap-2 bg-slate-50 py-2 border-b">

              <button
                onClick={() => zoomIn()}
                className="px-3 py-1 rounded bg-slate-700 text-white hover:bg-slate-600"
              >
                +
              </button>

              <button
                onClick={() => zoomOut()}
                className="px-3 py-1 rounded bg-slate-700 text-white hover:bg-slate-600"
              >
                −
              </button>

              <button
                onClick={() => resetTransform()}
                className="px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
              >
                Reset
              </button>

              <a
                href={image}
                download
                className="px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700"
              >
                Download
              </a>

            </div>

            {/* Image */}

            <div className="bg-black h-[650px] flex items-center justify-center">

              <TransformComponent>

                <img
                  src={image}
                  alt={title}
                  className="max-h-[650px] object-contain"
                />

              </TransformComponent>

            </div>
          </>
        )}
      </TransformWrapper>
    </div>
  );
}