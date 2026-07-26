"use client";

import { useEffect, useState } from "react";

import MainLayout from "@/components/layout/MainLayout";
import MissionCard from "@/components/missions/MissionCard";

import { getAOIs } from "@/services/aoi";

import type { AOI } from "@/types/aoi";

export default function MissionsPage() {
  const [selectedAOI, setSelectedAOI] =
    useState("AOI001");

  const [missions, setMissions] =
    useState<AOI[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function loadMissions() {
      try {
        const data = await getAOIs();
        setMissions(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadMissions();
  }, []);

  return (
    <MainLayout
      selectedAOI={selectedAOI}
      onAOIChange={setSelectedAOI}
    >
      <div className="space-y-8">

        <div>
          <h1 className="text-3xl font-bold text-slate-800">
            Mission Catalog
          </h1>

          <p className="mt-2 text-slate-500">
            Persistent Earth Observation intelligence
            missions available in GeoSentinel AI.
          </p>
        </div>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            Loading Missions...
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">

            {missions.map((mission) => (
              <MissionCard
                key={mission.id}
                mission={mission}
                selected={selectedAOI === mission.id}
                onSelect={setSelectedAOI}
              />
            ))}

          </div>
        )}

      </div>
    </MainLayout>
  );
}