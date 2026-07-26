"use client";

import { useEffect, useState } from "react";

import MainLayout from "@/components/layout/MainLayout";

import DashboardCard from "@/components/dashboard/DashboardCard";
import MissionSummary from "@/components/dashboard/MissionSummary";
import MissionAnalytics from "@/components/dashboard/MissionAnalytics";
import ModelOutputs from "@/components/dashboard/ModelOutputs";

import AnalysisTimelineTable from "@/components/timeline/AnalysisTimelineTable";

import ImageViewer from "@/components/viewer/ImageViewer";
import ReportViewer from "@/components/viewer/ReportViewer";

import {
  getLatestAnalysis,
  getAnalysisById,
} from "@/services/dashboard";

import { getAnalysisTimeline } from "@/services/analysisTimeline";

import type { AnalysisResult } from "@/types/analysis";
import type { AnalysisTimelineEntry } from "@/types/timeline";

export default function HomePage() {
  const [selectedAOI, setSelectedAOI] =
    useState("AOI001");

  const [selectedAnalysisId, setSelectedAnalysisId] =
    useState<number | null>(null);

  const [analysis, setAnalysis] =
    useState<AnalysisResult | null>(null);

  const [timeline, setTimeline] =
    useState<AnalysisTimelineEntry[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    setSelectedAnalysisId(null);
  }, [selectedAOI]);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);

      try {
        let analysisData: AnalysisResult;

        if (selectedAnalysisId !== null) {
          analysisData =
            await getAnalysisById(selectedAnalysisId);
        } else {
          analysisData =
            await getLatestAnalysis(selectedAOI);
        }

        const timelineData =
          await getAnalysisTimeline(selectedAOI);

        setAnalysis(analysisData);
        setTimeline(timelineData);

      } catch (error) {
        console.error(
          "Dashboard loading failed:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [selectedAOI, selectedAnalysisId]);

  return (
    <MainLayout
      selectedAOI={selectedAOI}
      onAOIChange={setSelectedAOI}
    >
      <div className="space-y-8">

        {/* Mission Overview */}
        <MissionSummary analysis={analysis} />

        {/* Analytics */}
        <MissionAnalytics analysis={analysis} />

        {/* Main Analysis */}
        <DashboardCard title="Interactive Analysis Viewer">
          {loading ? (
            <div className="h-[650px] flex items-center justify-center text-slate-500">
              Loading imagery...
            </div>
          ) : (
            <ImageViewer analysis={analysis} />
          )}
        </DashboardCard>

        {/* Outputs + Report */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">

          <DashboardCard title="Model Outputs">
            {loading ? (
              <div className="h-[600px] flex items-center justify-center text-slate-500">
                Loading model outputs...
              </div>
            ) : (
              <ModelOutputs analysis={analysis} />
            )}
          </DashboardCard>

          <DashboardCard title="Mission Intelligence Report">
            {loading ? (
              <div className="h-[600px] flex items-center justify-center text-slate-500">
                Loading intelligence report...
              </div>
            ) : (
              <ReportViewer report={analysis?.report} />
            )}
          </DashboardCard>

        </div>

        {/* Historical Timeline */}
        <DashboardCard title="Historical AOI Analyses">
          {loading ? (
            <div className="py-10 text-center text-slate-500">
              Loading timeline...
            </div>
          ) : (
            <AnalysisTimelineTable
              timeline={timeline}
              onSelectAnalysis={setSelectedAnalysisId}
            />
          )}
        </DashboardCard>

      </div>
    </MainLayout>
  );
}