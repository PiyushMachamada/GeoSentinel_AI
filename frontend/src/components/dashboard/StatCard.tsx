interface StatCardProps {
  title: string;
  value: string;
  valueColor?: string;
}

export default function StatCard({
  title,
  value,
  valueColor = "text-slate-700",
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-medium text-slate-500">
        {title}
      </h3>

      <p className={`mt-3 text-xl font-semibold ${valueColor}`}>
        {value}
      </p>
    </div>
  );
}