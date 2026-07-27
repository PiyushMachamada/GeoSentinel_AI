"use client";

import { useState } from "react";
import {
  TransformWrapper,
  TransformComponent,
} from "react-zoom-pan-pinch";

interface ImageCanvasProps {
  imageUrl?: string;
  title?: string;
  model?: string;
  aoi?: string;
  confidence?: number;
  change?: number;
  timestamp?: string;
  opacity?: number;
}

export default function ImageCanvas({
  imageUrl,
  title,
  model,
  aoi,
  confidence,
  change,
  timestamp,
  opacity = 100,
}: ImageCanvasProps) {

  const [fullscreen, setFullscreen] = useState(false);
  const [loadedUrl, setLoadedUrl] = useState<
    string | undefined
  >(undefined);
  const [failedUrl, setFailedUrl] = useState<
    string | undefined
  >(undefined);

  if (!imageUrl) return null;

  const loading =
    loadedUrl !== imageUrl && failedUrl !== imageUrl;
  const imageError = failedUrl === imageUrl;

  console.log("Image URL:", imageUrl);

  return (
    <div
      className={`rounded-xl border bg-white shadow-lg overflow-hidden ${
        fullscreen
          ? "fixed inset-0 z-50 m-4"
          : ""
      }`}
    >
      <TransformWrapper
        initialScale={1}
        minScale={0.5}
        maxScale={10}
      >
        {({
          zoomIn,
          zoomOut,
          resetTransform,
        }) => (
          <>
            {/* ================= HEADER ================= */}

            <div className="flex justify-between items-center px-5 py-3 bg-slate-900 text-white">

              <div>

                <h2 className="font-bold text-lg">
                  {title}
                </h2>

                <p className="text-xs text-slate-300">
                  {model}
                </p>

              </div>

              <div className="flex gap-2 flex-wrap">

                <button
                  onClick={() => zoomIn()}
                  className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600"
                >
                  +
                </button>

                <button
                  onClick={() => zoomOut()}
                  className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600"
                >
                  −
                </button>

                <button
                  onClick={() => resetTransform()}
                  className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600"
                >
                  Reset
                </button>

                <button
                  onClick={() =>
                    setFullscreen(!fullscreen)
                  }
                  className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-700"
                >
                  {fullscreen
                    ? "Exit"
                    : "Fullscreen"}
                </button>

                <a
                  href={imageUrl}
                  download
                  className="px-3 py-1 rounded bg-green-600 hover:bg-green-700"
                >
                  Download
                </a>

              </div>

            </div>

            {/* ================= IMAGE ================= */}

            <div className="bg-black min-h-[650px] flex justify-center items-center relative overflow-hidden">

              {loading && (
                <div className="absolute z-10 text-white animate-pulse">
                  Loading imagery...
                </div>
              )}

              {imageError && (
                <div className="absolute z-10 text-red-400">
                  Failed to load image
                </div>
              )}

              <TransformComponent>

                <img
                  src={imageUrl}
                  alt={title}
                  onLoad={() => {
                    console.log("LOADED");
                    setLoadedUrl(imageUrl);
                    setFailedUrl(undefined);
                  }}
                  onError={(e) => {
                    console.log("ERROR", e);
                    setLoadedUrl(undefined);
                    setFailedUrl(imageUrl);
                  }}
                  className="max-h-[650px] object-contain select-none"
                  draggable={false}
                  style={{
                    opacity: opacity / 100,
                  }}
                />

              </TransformComponent>

            </div>

            {/* ================= METADATA ================= */}

            <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 p-5 bg-slate-50 border-t">

              <Metric
                title="AOI"
                value={aoi ?? "N/A"}
              />

              <Metric
                title="Confidence"
                value={
                  confidence != null
                    ? `${confidence.toFixed(2)}%`
                    : "N/A"
                }
              />

              <Metric
                title="Change"
                value={
                  change != null
                    ? `${change.toFixed(2)}%`
                    : "N/A"
                }
              />

              <Metric
                title="Opacity"
                value={`${opacity}%`}
              />

              <Metric
                title="Generated"
                value={
                  timestamp
                    ? new Date(
                        timestamp
                      ).toLocaleString("en-GB")
                    : "N/A"
                }
              />

              <Metric
                title="Layer"
                value={model ?? "N/A"}
              />

            </div>

          </>
        )}
      </TransformWrapper>
    </div>
  );
}

function Metric({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border bg-white p-3 shadow-sm">

      <div className="text-xs uppercase text-slate-500">
        {title}
      </div>

      <div className="mt-1 font-semibold">
        {value}
      </div>

    </div>
  );
}