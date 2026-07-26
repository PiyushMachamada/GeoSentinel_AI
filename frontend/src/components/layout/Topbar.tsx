"use client";

import { useEffect, useState } from "react";

import { getAOIs } from "@/services/aoi";
import type { AOI } from "@/types/aoi";

interface TopbarProps {
  selectedAOI: string;
  onAOIChange: (aoi: string) => void;
}

export default function Topbar({
  selectedAOI,
  onAOIChange,
}: TopbarProps) {
  const [aois, setAOIs] = useState<AOI[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAOIs() {
      try {
        const data: any = await getAOIs();

        console.log("AOIs from backend:", data);

        // Handle both possible response formats
        if (Array.isArray(data)) {
          setAOIs(data);
        } else if (Array.isArray(data.aois)) {
          setAOIs(data.aois);
        } else {
          console.error("Unexpected AOI response:", data);
          setAOIs([]);
        }
      } catch (error) {
        console.error("Failed to load AOIs:", error);
        setAOIs([]);
      } finally {
        setLoading(false);
      }
    }

    loadAOIs();
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-800">
          Dashboard
        </h2>

        <p className="text-sm text-slate-500">
          Persistent Earth Observation Intelligence Platform
        </p>
      </div>

      <div className="flex items-center gap-8">
        {/* Monitoring Status */}
        <div className="text-right">
          <p className="text-sm font-medium text-slate-700">
            Monitoring Status
          </p>

          <div className="flex items-center justify-end gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-green-500"></span>

            <p className="text-sm text-green-600 font-medium">
              Active
            </p>
          </div>
        </div>

        {/* AOI Selector */}
        <div className="text-right">
          <label
            htmlFor="aoi-selector"
            className="block text-sm font-medium text-slate-700 mb-1"
          >
            Area of Interest
          </label>

          <select
            id="aoi-selector"
            value={selectedAOI}
            onChange={(e) => onAOIChange(e.target.value)}
            disabled={loading || aois.length === 0}
            className="min-w-[260px] rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100 disabled:text-slate-400"
          >
            {loading ? (
              <option>Loading AOIs...</option>
            ) : aois.length === 0 ? (
              <option>No AOIs Found</option>
            ) : (
              aois.map((aoi) => (
                <option
                  key={aoi.id}
                  value={aoi.id}
                >
                  {aoi.name}
                </option>
              ))
            )}
          </select>
        </div>
      </div>
    </header>
  );
}