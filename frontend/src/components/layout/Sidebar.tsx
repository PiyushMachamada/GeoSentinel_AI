export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-slate-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold">GeoSentinel AI</h1>
        <p className="text-xs text-slate-400 mt-1">
          Persistent Earth Observation
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">

          <li className="px-4 py-2 rounded-lg bg-sky-600 text-white font-medium cursor-pointer">
            Dashboard
          </li>

          <li className="px-4 py-2 rounded-lg hover:bg-slate-800 cursor-pointer">
            AOIs
          </li>

          <li className="px-4 py-2 rounded-lg hover:bg-slate-800 cursor-pointer">
            Timeline
          </li>

          <li className="px-4 py-2 rounded-lg hover:bg-slate-800 cursor-pointer">
            Reports
          </li>

          <li className="px-4 py-2 rounded-lg hover:bg-slate-800 cursor-pointer">
            Monitoring
          </li>

          <li className="px-4 py-2 rounded-lg hover:bg-slate-800 cursor-pointer">
            Settings
          </li>

        </ul>
      </nav>
    </aside>
  );
}