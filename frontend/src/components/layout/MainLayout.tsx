import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface MainLayoutProps {
  children: React.ReactNode;
  selectedAOI: string;
  onAOIChange: (aoi: string) => void;
}

export default function MainLayout({
  children,
  selectedAOI,
  onAOIChange,
}: MainLayoutProps) {
  return (
    <div className="flex h-screen bg-slate-100">
      <Sidebar />

      <div className="flex flex-col flex-1">
        <Topbar
          selectedAOI={selectedAOI}
          onAOIChange={onAOIChange}
        />

        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}