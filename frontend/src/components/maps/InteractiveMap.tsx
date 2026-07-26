"use client";

import { useState } from "react";

import "leaflet/dist/leaflet.css";

import { MapContainer, TileLayer } from "react-leaflet";

import type { MapLayer, MapLayerOption } from "@/types/map";

const layers: MapLayerOption[] = [
  { id: "satellite", label: "🛰 Satellite" },
  { id: "change", label: "🔥 Change Detection" },
  { id: "segmentation", label: "🌱 Segmentation" },
  { id: "dynamicworld", label: "🌍 Dynamic World" },
  { id: "objects", label: "📦 Objects" },
];

export default function InteractiveMap() {
  const [activeLayer, setActiveLayer] =
    useState<MapLayer>("satellite");

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-2">
        {layers.map((layer) => (
          <button
            key={layer.id}
            onClick={() => setActiveLayer(layer.id)}
            className={`px-4 py-2 rounded-lg border text-sm font-medium transition
              ${
                activeLayer === layer.id
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white hover:bg-slate-100 border-slate-300"
              }`}
          >
            {layer.label}
          </button>
        ))}
      </div>

      {/* Active Layer */}
      <div className="text-sm text-slate-600">
        Active Layer:
        <span className="font-semibold ml-2 capitalize">
          {activeLayer}
        </span>
      </div>

      {/* Map */}
      <div className="w-full h-[500px] rounded-xl overflow-hidden border border-gray-200 shadow-sm">
        <MapContainer
          center={[12.9716, 77.5946]}
          zoom={11}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          {activeLayer === "satellite" && (
            <TileLayer
              attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          )}

          {activeLayer !== "satellite" && (
            <TileLayer
              attribution="GeoSentinel AI"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          )}
        </MapContainer>
      </div>
    </div>
  );
}