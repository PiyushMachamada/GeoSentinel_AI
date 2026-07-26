interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
}

export default function DashboardCard({
  title,
  children,
}: DashboardCardProps) {
  return (
    <section
      className="
        rounded-2xl
        border border-slate-200
        bg-white
        shadow-sm
        hover:shadow-md
        transition-shadow
        duration-200
        overflow-hidden
      "
    >
      {/* Header */}
      <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">

        <h3 className="text-lg font-semibold text-slate-800">
          {title}
        </h3>

      </div>

      {/* Content */}
      <div className="p-6 text-slate-700">

        {children}

      </div>

    </section>
  );
}