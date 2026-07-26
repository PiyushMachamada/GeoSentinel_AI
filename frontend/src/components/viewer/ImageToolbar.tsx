"use client";

export type ViewerLayer =
  | "before"
  | "after"
  | "changestar"
  | "prithvi"
  | "dynamicworld"
  | "groundingdino";

interface ImageToolbarProps {
  activeLayer: ViewerLayer;
  onLayerChange: (layer: ViewerLayer) => void;
}

const layers: {
  id: ViewerLayer;
  icon: string;
  label: string;
  description: string;
}[] = [
  {
    id: "before",
    icon: "🛰",
    label: "Before",
    description: "Reference satellite image",
  },
  {
    id: "after",
    icon: "🛰",
    label: "Latest",
    description: "Most recent satellite image",
  },
  {
    id: "changestar",
    icon: "🔥",
    label: "Change Detection",
    description: "Temporal changes detected",
  },
  {
    id: "prithvi",
    icon: "🌱",
    label: "Land Cover",
    description: "AI semantic segmentation",
  },
  {
    id: "dynamicworld",
    icon: "🌍",
    label: "Dynamic World",
    description: "Google land cover classes",
  },
  {
    id: "groundingdino",
    icon: "🎯",
    label: "Object Detection",
    description: "Detected objects and assets",
  },
];

export default function ImageToolbar({
  activeLayer,
  onLayerChange,
}: ImageToolbarProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3 border-b bg-slate-50">

        <div>
          <h3 className="font-semibold text-slate-800">
            Intelligence Layers
          </h3>

          <p className="text-xs text-slate-500">
            Explore imagery and AI-generated analysis
          </p>
        </div>

        <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
          {layers.find((l) => l.id === activeLayer)?.label}
        </span>

      </div>

      {/* Layer Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 p-4">

        {layers.map((layer) => {

          const selected = activeLayer === layer.id;

          return (
            <button
              key={layer.id}
              onClick={() => onLayerChange(layer.id)}
              className={`
                transition-all duration-200
                rounded-xl
                border
                p-4
                text-left
                hover:shadow-md
                hover:-translate-y-1

                ${
                  selected
                    ? "border-blue-600 bg-blue-600 text-white shadow-lg"
                    : "border-slate-200 bg-white hover:border-blue-400"
                }
              `}
            >
              <div className="text-3xl">
                {layer.icon}
              </div>

              <div className="mt-3 font-semibold">
                {layer.label}
              </div>

              <div
                className={`text-xs mt-1 ${
                  selected
                    ? "text-blue-100"
                    : "text-slate-500"
                }`}
              >
                {layer.description}
              </div>
            </button>
          );

        })}

      </div>

    </div>
  );
}