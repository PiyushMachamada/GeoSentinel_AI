"use client";

interface LayerControlsProps {
  visible: boolean;
  opacity: number;
  onVisibleChange: (visible: boolean) => void;
  onOpacityChange: (opacity: number) => void;
}

export default function LayerControls({
  visible,
  opacity,
  onVisibleChange,
  onOpacityChange,
}: LayerControlsProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

      {/* Header */}
      <div className="px-5 py-3 bg-slate-900 text-white border-b">

        <h3 className="font-semibold text-lg">
          Viewer Controls
        </h3>

        <p className="text-xs text-slate-300 mt-1">
          Customize the current imagery layer
        </p>

      </div>

      <div className="p-5 space-y-6">

        {/* Visibility */}

        <div className="flex items-center justify-between">

          <div>

            <h4 className="font-medium text-slate-700">
              Layer Visibility
            </h4>

            <p className="text-xs text-slate-500">
              Show or hide the selected layer
            </p>

          </div>

          <button
            onClick={() => onVisibleChange(!visible)}
            className={`relative inline-flex h-7 w-14 items-center rounded-full transition ${
              visible
                ? "bg-green-500"
                : "bg-slate-300"
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white transition ${
                visible
                  ? "translate-x-8"
                  : "translate-x-1"
              }`}
            />
          </button>

        </div>

        {/* Opacity */}

        <div>

          <div className="flex justify-between mb-2">

            <span className="font-medium text-slate-700">
              Layer Opacity
            </span>

            <span className="font-semibold text-blue-600">
              {opacity}%
            </span>

          </div>

          <input
            type="range"
            min={0}
            max={100}
            value={opacity}
            onChange={(e) =>
              onOpacityChange(Number(e.target.value))
            }
            className="w-full accent-blue-600"
          />

        </div>

        {/* Status Cards */}

        <div className="grid grid-cols-2 gap-4">

          <div className="rounded-lg border bg-slate-50 p-4">

            <div className="text-xs uppercase text-slate-500">
              Status
            </div>

            <div
              className={`mt-1 font-semibold ${
                visible
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {visible
                ? "Visible"
                : "Hidden"}
            </div>

          </div>

          <div className="rounded-lg border bg-slate-50 p-4">

            <div className="text-xs uppercase text-slate-500">
              Opacity
            </div>

            <div className="mt-1 font-semibold">
              {opacity}%
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}