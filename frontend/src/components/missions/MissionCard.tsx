"use client";

import type { AOI } from "@/types/aoi";

interface MissionCardProps {
  mission: AOI;
  selected?: boolean;
  onSelect?: (id: string) => void;
}

export default function MissionCard({
  mission,
  selected = false,
  onSelect,
}: MissionCardProps) {
  return (
    <div
      onClick={() => onSelect?.(mission.id)}
      className={`
        cursor-pointer
        rounded-xl
        border
        p-6
        shadow-sm
        transition-all
        duration-200
        hover:shadow-lg
        hover:-translate-y-1
        ${
          selected
            ? "border-blue-600 bg-blue-50"
            : "border-slate-200 bg-white"
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between">

        <div>

          <p className="text-xs font-semibold tracking-widest text-blue-600 uppercase">
            {mission.id}
          </p>

          <h3 className="mt-1 text-lg font-bold text-slate-800">
            {mission.name}
          </h3>

        </div>

        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            mission.active
              ? "bg-green-100 text-green-700"
              : "bg-red-100 text-red-700"
          }`}
        >
          {mission.active ? "Active" : "Inactive"}
        </span>

      </div>

      {/* Description */}
      <p className="mt-4 text-sm text-slate-600">
        {mission.description}
      </p>

      {/* Details */}
      <div className="mt-6 grid grid-cols-2 gap-4 text-sm">

        <div>
          <p className="text-slate-500">Monitoring</p>
          <p className="font-semibold">
            {mission.monitoring_interval}
          </p>
        </div>

        <div>
          <p className="text-slate-500">Radius</p>
          <p className="font-semibold">
            {mission.radius_km} km
          </p>
        </div>

        <div>
          <p className="text-slate-500">Latitude</p>
          <p className="font-semibold">
            {mission.latitude.toFixed(4)}
          </p>
        </div>

        <div>
          <p className="text-slate-500">Longitude</p>
          <p className="font-semibold">
            {mission.longitude.toFixed(4)}
          </p>
        </div>

      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-slate-200 flex justify-between items-center">

        <span className="text-xs text-slate-500">
          Persistent Monitoring Mission
        </span>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect?.(mission.id);
          }}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition"
        >
          Open Mission
        </button>

      </div>
    </div>
  );
}   