import DashboardCard from "./DashboardCard";

export default function LatestObservationCard() {
  return (
    <DashboardCard title="Latest Observation">
      <div className="space-y-3">
        <p className="text-slate-500">
          No analysis loaded.
        </p>

        <div className="text-sm text-slate-600">
          <p>
            <span className="font-medium">AOI:</span> —
          </p>

          <p>
            <span className="font-medium">Observation Time:</span> —
          </p>

          <p>
            <span className="font-medium">Analysis Status:</span> Waiting for first observation
          </p>
        </div>
      </div>
    </DashboardCard>
  );
}